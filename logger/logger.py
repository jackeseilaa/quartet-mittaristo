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
import time
import urllib.request
from datetime import datetime

SIGNALK_URL = "http://localhost:3000/signalk/v1/api/vessels/self"
LOG_DIR = os.path.expanduser("~/quartet-logs")
INTERVAL_S = 10  # kuinka usein piste kirjataan

CSV_HEADER = [
    "timestamp", "lat", "lon", "sog_kt", "cog_deg", "heading_deg", "depth_m",
    "wind_true_speed_kt", "wind_true_angle_deg",
    "wind_apparent_speed_kt", "wind_apparent_angle_deg",
]

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from csv_to_gpx import convert as csv_to_gpx  # noqa: E402


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
        ms_to_kt(get_value(data, "environment.wind.speedTrue")),
        rad_to_deg(get_value(data, "environment.wind.angleTrueWater")
                   or get_value(data, "environment.wind.angleTrueGround")),
        ms_to_kt(get_value(data, "environment.wind.speedApparent")),
        rad_to_deg(get_value(data, "environment.wind.angleApparent")),
    ]


def main():
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
