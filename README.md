# Quartet Mittaristo

Purjeveneen **s/y Quartet** reaaliaikainen mittaristo- ja karttasovellus (J Sailing Tmi). Suunniteltu kiinteäksi ohjaamonäytöksi: `manifest.json` asettaa näkymän fullscreen + landscape, ja mukana on erillinen yötila (punasävyinen paletti, kohdistin piilotettu).

## Sisältö

- **`index.html` – Mittaristo** (v2.1.0): tuulikompassi (näennäinen/tosi tuuli, säädettävä no-go-alue), tuulen nopeus, SOG/COG/loki-nopeus (STW), syväysmittari väri-indikaattoreineen (cyan → amber → red -kynnysarvot), sijainti (lat/lon) ja kellonaika.
- **`kartta.html` – Kartta** (v1.2.0): Leaflet.js + OpenStreetMap-pohjakartta ja OpenSeaMap-merimerkkitaso, oma alus -merkki (kääntyy kompassisuunnan mukaan) ja AIS-kohteet, asetusvalikko kartta-tason valintaan (OSM / Traficom-rasterikartta), offline-alueen esilataus veneen omaa (internetitöntä) WiFi-verkkoa varten.
- **`manifest.json` / `service-worker.js`**: PWA-asennettavuus ("Lisää aloitusnäytölle") ja offline-tuki verkko-first-fallback-to-cache-strategialla; sama service worker cachettaa myös karttalaatat, mikä mahdollistaa offline-alueen latauksen.

## Tila

Sovellus käyttää tällä hetkellä **demo-dataa** (satunnaiskävely-simulaatio) — ei vielä yhteyttä oikeaan veneen instrumentointiin. Koodissa on valmiiksi kirjoitettu mutta kommentoitu `connectToSignalK()`-integraatio, joka on tarkoitus kytkeä veneen SignalK-palvelimeen (esim. Raspberry Pi, joka lukee NMEA 0183/2000 -instrumenttidataa) sekä AIS-kohteille Fintraffic/digitraffic.fi-rajapintaan kantaman ulkopuolisia aluksia varten. Traficom-rasterikarttataso on niin ikään valmiina mutta odottaa API-avainta.

Ei taustatietokantaa (ei Firebase/Firestorea) eikä kirjautumista — kaikki tila on selaimen muistissa.

## Versiointi

Mittaristo ja Kartta versioidaan erikseen (`vMAJOR.MINOR.PATCH` + build-päivä, näkyy yläpalkin versiotunnisteessa).

## Deploy

GitHub Pages, ei build-vaihetta. Live: https://jackeseilaa.github.io/quartet-mittaristo/
