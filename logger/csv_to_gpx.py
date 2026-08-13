#!/usr/bin/env python3
"""Muuntaa quartet-loggerin CSV-tiedoston standardiksi GPX 1.1 -jaljeksi
(vain aika+sijainti, GPX-ydinskeema -- yhteensopiva Google Earthin, OpenCPN:n
ja muiden karttaohjelmien kanssa). Ajettavissa myos itsenaisesti komentoriviltä
korjaamaan puuttuvia .gpx-tiedostoja jos logger.py ei syysta tai toisesta
sammunut siististi (esim. sahkokatko) eika ehtinyt tehda muunnosta itse."""
import csv
import glob
import os
import sys
import xml.sax.saxutils as sax

GPX_HEADER = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<gpx version="1.1" creator="quartet-logger" '
    'xmlns="http://www.topografix.com/GPX/1/1">\n'
    "<trk><name>{name}</name><trkseg>\n"
)
GPX_FOOTER = "</trkseg></trk>\n</gpx>\n"


def convert(csv_path, gpx_path):
    name = os.path.splitext(os.path.basename(csv_path))[0]
    with open(csv_path, newline="") as cf, open(gpx_path, "w") as gf:
        gf.write(GPX_HEADER.format(name=sax.escape(name)))
        reader = csv.DictReader(cf)
        for row in reader:
            lat, lon, ts = row.get("lat"), row.get("lon"), row.get("timestamp")
            if not lat or not lon:
                continue
            gf.write(
                f'<trkpt lat="{lat}" lon="{lon}"><time>{sax.escape(ts)}</time></trkpt>\n'
            )
        gf.write(GPX_FOOTER)


def convert_missing(log_dir):
    """Regeneroi GPX kaikille CSV:ille joilta puuttuu vastaava .gpx -- talteenotto
    tapauksiin joissa logger.py ei sammunut siististi."""
    fixed = 0
    for csv_path in glob.glob(os.path.join(log_dir, "*.csv")):
        gpx_path = csv_path.replace(".csv", ".gpx")
        if not os.path.exists(gpx_path):
            convert(csv_path, gpx_path)
            print(f"Korjattu: {gpx_path}")
            fixed += 1
    if fixed == 0:
        print("Ei puuttuvia GPX-tiedostoja.")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        convert_missing(sys.argv[1])
    elif len(sys.argv) == 3:
        convert(sys.argv[1], sys.argv[2])
    else:
        print(f"Kaytto: {sys.argv[0]} <csv> <gpx>  TAI  {sys.argv[0]} <hakemisto>")
        sys.exit(1)
