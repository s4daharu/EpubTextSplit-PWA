const CACHE_NAME = 'streamlit-pwa-v4';
const BASE_PATH = self.location.pathname.replace(/\/service-worker\.js$/, '');

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll([
        `${BASE_PATH}/`,
        `${BASE_PATH}/static/manifest.json`,
        `${BASE_PATH}/static/icons/icon-192x192.png`,
        `${BASE_PATH}/static/icons/icon-512x512.png`
      ]);
    })
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // Streamlit API and static content handling
  if (url.pathname.startsWith(`${BASE_PATH}/static`) ||
      url.pathname.startsWith(`${BASE_PATH}/_stcore`) ||
      url.pathname === `${BASE_PATH}/`) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        return cached || fetch(event.request).then((response) => {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
          return response;
        });
      })
    );
  }
});