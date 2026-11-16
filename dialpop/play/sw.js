// Dial Pop web build: offline cache (build.py --web fills in VERSION and FILES).
// The page itself is network-first so a new upload shows up on the next visit; scripts and icons are
// cached up front, font slices only once the browser asks for them (Korean is split into ~130 slices
// and a player needs a few). Other sites (Firebase, ads) are never touched.
const VERSION = "44493bf4be04";
const FILES = ["./", "fonts.css", "game.html", "icons/icon-180.png", "icons/icon-192.png", "icons/icon-512.png", "icons/maskable-512.png", "manifest.webmanifest", "web.js"];
const CACHE = 'dialpop-' + VERSION;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k.startsWith('dialpop-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;
  if (r.mode === 'navigate') {
    e.respondWith(fetch(r).then(res => {
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(r, copy));
      return res;
    }).catch(() => caches.match(r, { ignoreSearch: true }).then(hit => hit || caches.match('./'))));
    return;
  }
  e.respondWith(caches.match(r).then(hit => hit || fetch(r).then(res => {
    if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(r, copy)); }
    return res;
  })));
});
