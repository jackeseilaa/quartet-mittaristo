// Quartet Mittaristo -- offline-cache service worker.
// Kasvata CACHE_NAME-versiota aina kun index.html muuttuu merkittävästi,
// niin selain hakee uuden version seuraavalla kerralla kun nettiä on.
const CACHE_NAME = 'quartet-mittaristo-v1';
const APP_SHELL = ['./index.html', './manifest.json'];

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

// Network-first for index.html (get the newest version when internet is available),
// falling back to the cached copy when offline (e.g. on the boat's local WiFi).
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
