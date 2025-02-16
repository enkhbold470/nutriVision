// Import the main service worker functionality
importScripts('/static/serviceWorker.js');

// This file serves as the entry point for the service worker
console.log('[Service Worker] Main service worker loaded');

const CACHE_NAME = 'nutrivision-v1';
const CACHE_URLS = [
    '/',
    '/static/manifest.json',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
];

// Install event - cache static assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(CACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== CACHE_NAME) {
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    return response;
                }
                return fetch(event.request)
                    .then(response => {
                        // Don't cache API calls or video feed
                        if (!event.request.url.includes('/api/') && 
                            !event.request.url.includes('/video_feed')) {
                            return caches.open(CACHE_NAME)
                                .then(cache => {
                                    cache.put(event.request, response.clone());
                                    return response;
                                });
                        }
                        return response;
                    });
            })
    );
}); 