// Service Worker for Chilli Care PWA
// Version: 2.4.3 - Cache update

const CACHE_NAME = 'chilli-care-v9';
const RUNTIME_CACHE = 'chilli-care-runtime-v9';
const IMAGE_CACHE = 'chilli-care-images-v9';

// App Shell - Critical resources to cache immediately
const APP_SHELL = [
    '/',
    '/static/css/style.css',
    '/static/css/admin_dashboard.css',
    '/static/css/diseases.css',
    '/static/css/analytics.css',
    '/static/css/pwa.css',
    '/static/js/main.js',
    '/static/js/admin_dashboard.js',
    '/static/js/diseases.js',
    '/static/js/analytics.js',
    '/static/js/notifications.js',
    '/static/js/pwa.js',
    '/static/images/Chilli Care Logo.png',
    '/static/images/Site icon.png',
    '/static/images/background.jpg',
    // Disease images
    '/static/images/Chilli __Whitefly.jpg',
    '/static/images/Chilli __Yellowish.jpg',
    '/static/images/Chilli__Anthacnose.jpg',
    '/static/images/Chilli__Leaf_Curl_Virus.jpg',
    '/static/images/Chilli___healthy.jpg',
    // Pages
    '/about',
    '/diseases',
    '/contact',
    '/analytics',
    '/privacy',
    '/terms',
    '/faqs',
    // Offline fallback
    '/static/offline.html'
];

// All disease detail images
const DISEASE_IMAGES = [
    '/static/images/diseases/whitefly.jpg',
    '/static/images/diseases/tomato-spotted-wilt-virus.jpg',
    '/static/images/diseases/tobacco-mosaic-virus.jpg',
    '/static/images/diseases/tip-burn.jpg',
    '/static/images/diseases/sunscald.jpg',
    '/static/images/diseases/stem-rot.jpg',
    '/static/images/diseases/spider-mites.jpg',
    '/static/images/diseases/powdery-mildew.jpg',
    '/static/images/diseases/phytophthora-blight.jpg',
    '/static/images/diseases/pepper-mild-mottle-virus.jpg',
    '/static/images/diseases/nitrogen-deficiency.jpg',
    '/static/images/diseases/mealybug.jpg',
    '/static/images/diseases/leaf-curl-virus.jpg',
    '/static/images/diseases/groundnut-bud-necrosis-virus.jpg',
    '/static/images/diseases/fruit-rot.jpg',
    '/static/images/diseases/damping-off.jpg',
    '/static/images/diseases/cucumber-mosaic-virus.jpg',
    '/static/images/diseases/cercospora-leaf-spot.jpg',
    '/static/images/diseases/bacterial-wilt.jpg',
    '/static/images/diseases/bacterial-spot.jpg',
    '/static/images/diseases/bacterial-leaf-spot.jpg',
    '/static/images/diseases/aphids.jpg',
    '/static/images/diseases/anthracnose.jpg'
];

// ============================================
// INSTALL EVENT - Cache App Shell
// ============================================
self.addEventListener('install', (event) => {
    console.log('[Service Worker] Installing...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[Service Worker] Caching app shell');
                return cache.addAll(APP_SHELL);
            })
            .then(() => {
                // Cache disease images separately
                return caches.open(IMAGE_CACHE);
            })
            .then((cache) => {
                console.log('[Service Worker] Caching disease images');
                // Add images with error handling
                return Promise.all(
                    DISEASE_IMAGES.map(url => {
                        return cache.add(url).catch(err => {
                            console.warn(`[Service Worker] Failed to cache ${url}:`, err);
                        });
                    })
                );
            })
            .then(() => {
                console.log('[Service Worker] App shell and images cached');
                return self.skipWaiting(); // Activate immediately
            })
            .catch((error) => {
                console.error('[Service Worker] Installation failed:', error);
            })
    );
});

// ============================================
// ACTIVATE EVENT - Clean up old caches
// ============================================
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Activating...');
    
    const currentCaches = [CACHE_NAME, RUNTIME_CACHE, IMAGE_CACHE];
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (!currentCaches.includes(cacheName)) {
                            console.log('[Service Worker] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('[Service Worker] Activated');
                return self.clients.claim(); // Take control immediately
            })
    );
});

// ============================================
// FETCH EVENT - Serve from cache or network
// ============================================
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip chrome extensions and other protocols
    if (!url.protocol.startsWith('http')) {
        return;
    }
    
    // Auth API - Always go to network, never serve from cache (prevents stale session data)
    if (url.pathname.startsWith('/api/auth/')) {
        return;
    }

    // User data API - Network first to ensure fresh data per authenticated user
    if (url.pathname.startsWith('/api/user/')) {
        event.respondWith(networkFirstStrategy(request));
        return;
    }

    // Other API requests - Stale-While-Revalidate
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(staleWhileRevalidate(request));
        return;
    }
    
    // Images - Cache first, network as fallback
    if (request.destination === 'image' || url.pathname.includes('/images/')) {
        event.respondWith(cacheFirstStrategy(request, IMAGE_CACHE));
        return;
    }
    
    // Static assets (CSS, JS, fonts) - Cache first
    if (
        request.destination === 'style' ||
        request.destination === 'script' ||
        request.destination === 'font' ||
        url.pathname.includes('/static/')
    ) {
        event.respondWith(cacheFirstStrategy(request, CACHE_NAME));
        return;
    }
    
    // HTML pages - Network first with cache fallback
    if (request.destination === 'document' || request.headers.get('accept')?.includes('text/html')) {
        event.respondWith(networkFirstStrategy(request));
        return;
    }
    
    // Default: Network first
    event.respondWith(networkFirstStrategy(request));
});

// ============================================
// CACHING STRATEGIES
// ============================================

/**
 * Cache First Strategy
 * Good for: Static assets, images
 */
async function cacheFirstStrategy(request, cacheName = CACHE_NAME) {
    try {
        // Try to get from cache first
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {
            console.log('[Service Worker] Cache hit:', request.url);
            return cachedResponse;
        }
        
        // Not in cache, fetch from network
        console.log('[Service Worker] Cache miss, fetching:', request.url);
        const networkResponse = await fetch(request);
        
        // Cache the new response
        if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('[Service Worker] Cache first strategy failed:', error);
        
        // Try to return from cache anyway
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page for HTML requests
        if (request.destination === 'document') {
            return caches.match('/static/offline.html');
        }
        
        throw error;
    }
}

/**
 * Network First Strategy
 * Good for: HTML pages, frequently updated content
 */
async function networkFirstStrategy(request) {
    try {
        // Try network first
        const networkResponse = await fetch(request);
        
        // Cache successful responses
        if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(RUNTIME_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('[Service Worker] Network failed, trying cache:', request.url);
        
        // Network failed, try cache
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page for HTML requests
        if (request.destination === 'document' || request.headers.get('accept')?.includes('text/html')) {
            return caches.match('/static/offline.html');
        }
        
        throw error;
    }
}

/**
 * Stale While Revalidate Strategy
 * Good for: API calls, dynamic data
 */
async function staleWhileRevalidate(request) {
    const cache = await caches.open(RUNTIME_CACHE);
    const cachedResponse = await cache.match(request);
    
    // Fetch from network in background
    const fetchPromise = fetch(request).then((networkResponse) => {
        // Update cache with new data
        if (networkResponse && networkResponse.status === 200) {
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    }).catch((error) => {
        console.log('[Service Worker] Fetch failed for:', request.url);
        return null;
    });
    
    // Return cached version immediately if available
    // Otherwise wait for network
    return cachedResponse || fetchPromise;
}

// ============================================
// BACKGROUND SYNC (Optional - for future use)
// ============================================
self.addEventListener('sync', (event) => {
    console.log('[Service Worker] Sync event:', event.tag);
    
    if (event.tag === 'sync-predictions') {
        event.waitUntil(syncPredictions());
    }
});

async function syncPredictions() {
    // Placeholder for syncing predictions when back online
    console.log('[Service Worker] Syncing predictions...');
}

// ============================================
// PUSH NOTIFICATIONS (Optional - for future use)
// ============================================
self.addEventListener('push', (event) => {
    console.log('[Service Worker] Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'New notification',
        icon: '/static/images/Site icon.png',
        badge: '/static/images/Site icon.png',
        vibrate: [200, 100, 200],
        tag: 'chilli-care-notification'
    };
    
    event.waitUntil(
        self.registration.showNotification('Chilli Care', options)
    );
});

// ============================================
// MESSAGE HANDLER
// ============================================
self.addEventListener('message', (event) => {
    console.log('[Service Worker] Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_URLS') {
        const urls = event.data.urls;
        event.waitUntil(
            caches.open(RUNTIME_CACHE)
                .then(cache => cache.addAll(urls))
        );
    }
});

console.log('[Service Worker] Loaded successfully');
