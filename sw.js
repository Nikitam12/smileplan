// SmilePlan service worker.
// При изменении любого файла из SHELL увеличьте номер в CACHE.
const CACHE = 'smileplan-v13';
const SHELL = [
  '/smileplan/',
  '/smileplan/index.html',
  '/smileplan/assets/index-ios4.js',
  '/smileplan/assets/index-DQE2z3t7.css',
  '/smileplan/assets/ios-v2.css',
  '/smileplan/manifest.json',
  '/smileplan/tooth.svg',
  '/smileplan/icon-192.png',
  '/smileplan/icon-512.png',
  '/smileplan/apple-touch-icon.png',
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Внешние запросы (Telegram, Groq, шрифты для PDF) не трогаем.
  if (url.origin !== self.location.origin) return;

  // Навигация: сначала сеть, при отсутствии сети — закэшированная оболочка (SPA).
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req).catch(() =>
        caches.match('/smileplan/').then(r => r || caches.match('/smileplan/index.html'))
      )
    );
    return;
  }

  // Статика: из кэша сразу, в фоне обновляем (stale-while-revalidate).
  e.respondWith(
    caches.open(CACHE).then(cache =>
      cache.match(req).then(cached => {
        const network = fetch(req)
          .then(res => {
            if (res && res.ok) cache.put(req, res.clone());
            return res;
          })
          .catch(() => cached || new Response('', { status: 504 }));
        return cached || network;
      })
    )
  );
});
