# Quartet Mittaristo

Purjeveneen **s/y Quartet** reaaliaikainen mittaristo- ja karttasovellus (J Sailing Tmi). Suunniteltu kiinteäksi ohjaamonäytöksi: `manifest.json` asettaa näkymän fullscreen + landscape, ja mukana on erillinen yötila (punasävyinen paletti, kohdistin piilotettu).

## Sisältö

- **`index.html` – Mittaristo** (v3.0.2): tuulikompassi (näennäinen/tosi tuuli, säädettävä no-go-alue, pehmennetty neulan/lukemien animaatio), tuulen nopeus, SOG/COG/loki-nopeus (STW), syväysmittari väri-indikaattoreineen (cyan → amber → red -kynnysarvot), sijainti (lat/lon) ja kellonaika. Yhdistää SignalK-palvelimeen WebSocketilla.
- **`kartta.html` – Kartta** (v2.0.0): Leaflet.js + OpenStreetMap-pohjakartta ja OpenSeaMap-merimerkkitaso, oma alus -merkki (kääntyy kompassisuunnan mukaan) ja AIS-kohteet, asetusvalikko kartta-tason valintaan (OSM / Traficom-rasterikartta), offline-alueen esilataus veneen omaa (internetitöntä) WiFi-verkkoa varten. Yhdistää samaan SignalK-palvelimeen kuin mittaristo.
- **`manifest.json` / `service-worker.js`**: PWA-asennettavuus ("Lisää aloitusnäytölle") ja offline-tuki verkko-first-fallback-to-cache-strategialla; sama service worker cachettaa myös karttalaatat, mikä mahdollistaa offline-alueen latauksen.

## Tila

Molemmat sivut yhdistävät oikeaan SignalK-palvelimeen (`connectToSignalK()`, WebSocket-deltavirta `ws://<host>:3000/signalk/v1/stream?subscribe=all`). Host johdetaan aina sivun omasta `location.hostname`-arvosta, ei kovakoodatusta IP-osoitteesta — sovellus toimii siis riippumatta siitä ollaanko veneen omassa WiFi-verkossa, kotiverkossa Pi:n vieressä, tai Tailscalen kautta, kunhan sivu on ladattu Raspberry Pi:n omasta http-osoitteesta (portti 8080). GitHub Pages -version (https) selain estää mixed contentin takia yhdistämästä paikalliseen SignalKiin — tämä näkyy sovelluksessa selkeänä tilaviestinä eikä hiljaisena jumituksena.

Kartta hakee AIS-kohteet SignalK:n `vessels`-datasta (paikallinen AIS-vastaanotin NMEA-verkossa); kohteet katoavat kartalta automaattisesti 2 minuutin kuluttua viimeisestä päivityksestä. Fintrafficin digitraffic.fi-rajapinta (kantaman ulkopuoliset alukset LTE:n kautta) on yhä toteuttamatta — se täydentäisi paikallista AIS-listaa (vaatisi MMSI-perusteisen yhdistämisen), eikä sitä ole voitu testata oikeaa AIS-vastaanotinta vasten. Traficom-rasterikarttataso on valmiina koodissa mutta odottaa oikeaa API-avainta ja WMTS-osoitetta.

Ei taustatietokantaa (ei Firebase/Firestorea) eikä kirjautumista — kaikki tila on selaimen muistissa.

## Versiointi

Mittaristo ja Kartta versioidaan erikseen (`vMAJOR.MINOR.PATCH` + build-päivä, näkyy yläpalkin versiotunnisteessa).

## Deploy

GitHub Pages, ei build-vaihetta. Live: https://jackeseilaa.github.io/quartet-mittaristo/

✅ **Deploy/tietoturva tarkistettu 2.8.2026**: live-sivu vastaa repon HEAD:iä, ei viivettä. Ei kovakoodattuja API-avaimia (Traficom-avain on käyttäjän itse syöttämä ja tallentuu vain selaimen localStorageen, ei koskaan lähetetä repoon). SignalK-hostina käytetään sivun omaa `location.hostname`-arvoa, ei kovakoodattua IP-osoitetta. Koska sovelluksella ei ole backendia, ei myöskään Firestore-suojausta tarkistettavaksi.
