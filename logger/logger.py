#!/usr/bin/env python3
"""Quartet-lokittaja: kirjaa sijainnin + instrumenttidataa CSV:hen niin kauan kuin
tama prosessi on kaynnissa. Kaynnistetaan/pysaytetaan NetworkManager dispatcher
-skriptin toimesta aina kun Pi liittyy/eroaa QUARTET-WiFista, ei riipu selaimesta
tai mistaan muusta laitteesta. Puhuu SignalK:lle paikallisen REST-rajapinnan
kautta (ei websocketia, ei ulkoisia riippuvuuksia -- vain Python stdlib)."""
import csv
import json
import os
import signal
import sys
import threading
import time
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

SIGNALK_URL = "http://localhost:3000/signalk/v1/api/vessels/self"
LOG_DIR = os.path.expanduser("~/quartet-logs")
INTERVAL_S = 10  # kuinka usein piste kirjataan
ENGINE_PORT = 8091  # kartta.html/index.html POSTaavat tanne Moottori-napista

CSV_HEADER = [
    "timestamp", "lat", "lon", "sog_kt", "cog_deg", "heading_deg", "depth_m",
    "wind_true_speed_ms", "wind_true_angle_deg",
    "wind_apparent_speed_ms", "wind_apparent_angle_deg",
    "engine_on",
]

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from csv_to_gpx import convert as csv_to_gpx  # noqa: E402

# Moottorin tila -- taman prosessin ainoa jaettu muuttuja selaimen ja
# CSV-kirjoituksen valilla. Vain manuaalinen nappi tallahetkella; automaattinen
# GPIO-pohjainen tunnistus (virtalukko/laturi/oljynpainekytkin, optoeristetty)
# on suunniteltu mutta vaatii fyysisen johdotuksen ennen kuin se voidaan lisata.
engine_state = {"on": False}
engine_lock = threading.Lock()


class EngineHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _reply_state(self, code=200):
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        with engine_lock:
            self.wfile.write(json.dumps({"on": engine_state["on"]}).encode())

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/engine":
            self._reply_state()
        else:
            self.send_response(404)
            self._cors()
            self.end_headers()

    def do_POST(self):
        if self.path == "/engine/on":
            with engine_lock:
                engine_state["on"] = True
            self._reply_state()
        elif self.path == "/engine/off":
            with engine_lock:
                engine_state["on"] = False
            self._reply_state()
        else:
            self.send_response(404)
            self._cors()
            self.end_headers()

    def log_message(self, fmt, *args):
        pass  # ei tarpeen journaaliin, quartet-logger printtaa omat rivinsa


def start_engine_server():
    server = HTTPServer(("0.0.0.0", ENGINE_PORT), EngineHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"[quartet-logger] moottori-API kuuntelee portissa {ENGINE_PORT}", flush=True)
    return server


def fetch_signalk():
    try:
        with urllib.request.urlopen(SIGNALK_URL, timeout=5) as resp:
            return json.load(resp)
    except Exception as err:
        print(f"[quartet-logger] SignalK ei vastaa: {err}", flush=True)
        return None


def get_value(data, path):
    node = data
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    if isinstance(node, dict) and "value" in node:
        return node["value"]
    return None


def rad_to_deg(rad):
    return None if rad is None else rad * 180.0 / 3.141592653589793


def ms_to_kt(ms):
    return None if ms is None else ms * 1.94384


def build_row(data):
    pos = get_value(data, "navigation.position")
    if not pos or "latitude" not in pos or "longitude" not in pos:
        return None  # ei viela GPS-fiksia, ei kirjata riviä

    return [
        datetime.now().astimezone().isoformat(timespec="seconds"),
        pos["latitude"],
        pos["longitude"],
        ms_to_kt(get_value(data, "navigation.speedOverGround")),
        rad_to_deg(get_value(data, "navigation.courseOverGroundTrue")),
        rad_to_deg(get_value(data, "navigation.headingTrue")),
        get_value(data, "environment.depth.belowSurface"),
        get_value(data, "environment.wind.speedTrue"),
        rad_to_deg(get_value(data, "environment.wind.angleTrueWater")
                   or get_value(data, "environment.wind.angleTrueGround")),
        get_value(data, "environment.wind.speedApparent"),
        rad_to_deg(get_value(data, "environment.wind.angleApparent")),
        1 if engine_state["on"] else 0,
    ]


def main():
    start_engine_server()
    os.makedirs(LOG_DIR, exist_ok=True)
    start_name = datetime.now().strftime("%Y-%m-%d_%H%M")
    csv_path = os.path.join(LOG_DIR, f"{start_name}.csv")

    is_new = not os.path.exists(csv_path)
    f = open(csv_path, "a", newline="", buffering=1)
    writer = csv.writer(f)
    if is_new:
        writer.writerow(CSV_HEADER)
        f.flush()

    print(f"[quartet-logger] kaynnistyi, kirjoitan: {csv_path}", flush=True)

    def finalize_and_exit(signum, frame):
        print(f"[quartet-logger] sammutus (signal {signum}), muunnan GPX:n", flush=True)
        f.close()
        try:
            gpx_path = csv_path.replace(".csv", ".gpx")
            csv_to_gpx(csv_path, gpx_path)
            print(f"[quartet-logger] kirjoitettu: {gpx_path}", flush=True)
        except Exception as err:
            print(f"[quartet-logger] GPX-muunnos epaonnistui: {err}", flush=True)
        sys.exit(0)

    signal.signal(signal.SIGTERM, finalize_and_exit)
    signal.signal(signal.SIGINT, finalize_and_exit)

    while True:
        data = fetch_signalk()
        if data:
            row = build_row(data)
            if row:
                writer.writerow(row)
        time.sleep(INTERVAL_S)


if __name__ == "__main__":
    main()
