// Quartet -- offline-cache service worker (mittaristo + kartta).
// Kasvata CACHE_NAME-versiota aina kun sovellus muuttuu merkittävästi,
// niin selain hakee uuden version seuraavalla kerralla kun nettiä on.
const CACHE_NAME = 'quartet-v2';
const APP_SHELL = [
  './index.html',
  './kartta.html',
  './manifest.json',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js'
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

// Network-first for the app shell (get the newest version when internet is
// available), falling back to the cached copy when offline (boat WiFi).
// Map tile requests (openstreetmap.org etc.) are NOT cached here on purpose --
// they need a live connection (WiFi-1's own network has no internet, so tiles
// only load when there's real internet, e.g. via the LTE Pi sharing its
// connection, or before leaving the dock).
self.addEventListener('fetch', (event) => {
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
