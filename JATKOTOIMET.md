# Jatkotoimet — Quartet Mittaristo & SignalK

Tilannekatsaus 2026-08-03 tehdystä työstä, jotta seuraavalla kerralla pääsee suoraan asiaan kiinni.

## Avoin: Fluxgate-kompassin heading ei tule Raspberrylle

- Fluxgate-kompassi näyttää **oikean suunnan (esim. 46°) omalla näytöllään**, mutta tämä data **ei kulje Nexus NX2:n NMEA0183-ulostulossa** Raspberrylle asti.
- Todennettu suoraan raakadatasta (`cat /dev/ttyUSB0`): `$IIHDM,,M*0C` ja `$IIHDT,,T*0C` — molemmat lauseet tulevat, mutta kentät ovat **tyhjiä**.
- Kartta.html käyttää tällä hetkellä siis varakeinona GPS-kurssia (COG, VTG-lauseesta) veneen keulan suuntana, mikä on väärä silloin kun vene ei liiku (esim. laiturissa) — COG kertoo vain liikkeen suunnan, ei todellista asentoa.
- **Tehtävä veneellä**: tarkista Nexus NX2 -järjestelmän NMEA0183-ulostulon asetuksista (yleensä joku "NMEA output" / "Data output" -valikko instrumenttinäytöllä), onko heading-lauseet (HDG/HDM/HDT) kytketty päälle ulostulevaan lauselistaan. Ne pitää lisätä/aktivoida siellä — tämä ei ole korjattavissa Raspberryn tai SignalK:n päästä.
- **Koodin puolella ei tarvitse tehdä mitään lisää**: heti kun HDT tai HDM alkaa tulla oikealla arvolla, `kartta.html` käyttää sitä automaattisesti COG:n sijaan (`ownShip.hasHeading`-lippu, ks. `connectToSignalK()`-funktio).

## Muuta kesken/tiedossa (ei kiireellistä)

- **Traficom-rasterikartta (live WMTS)**: koodissa yhä vain tynkä (`addTraficomLayer()` kartta.html:ssä), odottaa API-avainta ja WMTS-osoitetta Traficomin paikkatietopalveluiden rekisteröinnin kautta (Suomi.fi-valtuudet, esim. J Sailing Tmi). Tämän sijaan käytössä on jo paikallinen `rannikkokartat.mbtiles` (SignalK:n oma chart-tiles-rajapinta), joka on nyt sovelluksen oletuskarttataso — riittää useimpaan käyttöön.
- **Fintrafficin digitraffic.fi-rajapinta** (kantaman ulkopuoliset AIS-alukset LTE:n kautta): ei toteutettu, täydentäisi paikallista AIS-vastaanotinta. Ei testattu oikeaa AIS-vastaanotinta vasten.

## Tehty tässä istunnossa (kaikki pushattu GitHubiin)

- Nexus NX2 kytketty USB/RS232-sarjaportin (`/dev/ttyUSB0`, 4800 baud) kautta SignalK:hon — data virtaa (sijainti, syvyys, veden lämpö, tuuli, SOG/COG, loki).
- SignalK:n `allow_readonly` asetettu pysyvästi todeksi — sovelluksella ei ole kirjautumista, joten se vaatii tämän toimiakseen.
- Korjattu piilevä bugi: koodi vertasi SignalK-kontekstia kirjaimelliseen `"vessels.self"`-merkkijonoon, jota palvelin ei koskaan lähetä (oikea konteksti tulee `self`-kentässä striimin ensimmäisessä viestissä) — aiheutti mm. sen että oma vene näkyi virheellisesti AIS-kohteena.
- `kartta.html`: Rannikkokartat-taso (paikallinen, ei API-avainta) lisätty ja asetettu oletukseksi, valinta muistetaan `localStorage`issa; Keskitä-nappi; oma vene -merkki piirtyy vasta oikean GPS-sijainnin saavuttua; iso SOG/COG-näyttö kartan päällä; COG:n aiheuttama keulan "täriseminä" vaimennettu alle 0.3 kt nopeuksilla.
- `index.html`: uusi "Kaikki data" -välilehti (näyttää kaiken SignalK-datan, myös veden lämmön, virtauksen, lokin — yksiköt: tuuli m/s, matkat nm, muut solmuina); sijainti näytetään WGS84 DD° MM' SS.S" -muodossa.
- GitHub-push toimii Raspberryltä ilman kirjautumista — Personal Access Token tallennettu `~/.git-credentials`iin (`credential.helper=store`).

## Hyödylliset osoitteet

- SignalK admin: `http://100.114.253.32:3000` (tai `http://quartet-signalk.tail47f013.ts.net:3000`) — Tailscalen kautta mistä tahansa.
- Mittaristo: `http://100.114.253.32:8080/index.html`
- Kartta: `http://100.114.253.32:8080/kartta.html`
- Live (GitHub Pages, ei toimi paikallisen SignalK:n datalla https-rajoituksen takia): https://jackeseilaa.github.io/quartet-mittaristo/
- Repo: https://github.com/jackeseilaa/quartet-mittaristo
