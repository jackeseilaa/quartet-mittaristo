// Quartet -- offline-cache service worker (mittaristo + kartta).
// Kasvata CACHE_NAME-versiota aina kun sovellus muuttuu merkittävästi,
// niin selain hakee uuden version seuraavalla kerralla kun nettiä on.
const CACHE_NAME = 'quartet-v3';
const APP_SHELL = [
  './index.html',
  './kartta.html',
  './manifest.json',
  './vendor/leaflet/leaflet.min.css',
  './vendor/leaflet/leaflet.min.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Leaflet (vendor/) on pinnattu versio joka ei koskaan muutu ilman
// CACHE_NAME-numeron kasvattamista -- ei ole mitään syytä odottaa verkkoa
// sen hakemiseksi. Cache-first: käytä välimuistia jos löytyy, nouda verkosta
// (ja tallenna välimuistiin) vain jos ei. Tämä on myös se korjaus 2026-08-04
// tehtyyn jumiutumisbugiin: aiemmin Leaflet ladattiin ulkoisesta CDN:stä
// network-first-strategialla, joten QUARTET-verkossa (ei internetiä) sivu jäi
// roikkumaan verkkopyynnön aikakatkaisuun asti ennen kuin mitään näkyi.
// Nyt Leaflet on itse-isännöity samasta originista, joten "verkkopyyntö"
// menee aina Pi:lle itselleen ja onnistuu nopeasti riippumatta internetistä.
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/vendor/')) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        if (cached) return cached;
        return fetch(event.request).then((response) => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          return response;
        });
      })
    );
    return;
  }

  // Network-first for the app shell (get the newest version when internet is
  // available), falling back to the cached copy when offline (boat WiFi).
  // Map tile requests (openstreetmap.org etc.) are NOT cached here on purpose --
  // they need a live connection (WiFi-1's own network has no internet, so tiles
  // only load when there's real internet, e.g. via the LTE Pi sharing its
  // connection, or before leaving the dock).
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
