// PWA Service Worker Registration and Installation Handler
// Handles PWA installation, updates, and offline functionality

(function() {
    'use strict';

    // Check if service workers are supported
    if (!('serviceWorker' in navigator)) {
        console.warn('[PWA] Service Workers not supported in this browser');
        return;
    }

    // ============================================
    // SERVICE WORKER REGISTRATION
    // ============================================
    
    let deferredPrompt;
    let swRegistration = null;

    // Register service worker when page loads
    window.addEventListener('load', async () => {
        try {
            // Register the service worker
            swRegistration = await navigator.serviceWorker.register('/static/sw.js', {
                scope: '/'
            });

            console.log('[PWA] Service Worker registered successfully:', swRegistration.scope);

            // Check for updates every 30 minutes
            setInterval(() => {
                swRegistration.update();
            }, 30 * 60 * 1000);

            // Handle service worker updates
            swRegistration.addEventListener('updatefound', () => {
                const newWorker = swRegistration.installing;
                
                newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        // New service worker available
                        showUpdateNotification();
                    }
                });
            });

        } catch (error) {
            console.error('[PWA] Service Worker registration failed:', error);
        }

        // Initialize PWA install prompt
        initializeInstallPrompt();
    });

    // ============================================
    // PWA INSTALLATION PROMPT
    // ============================================
    
    function initializeInstallPrompt() {
        // Capture the install prompt event
        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('[PWA] Install prompt available');
            
            // Prevent the mini-infobar from appearing on mobile
            e.preventDefault();
            
            // Stash the event so it can be triggered later
            deferredPrompt = e;
            
            // Show custom install button
            showInstallButton();
        });

        // Handle successful installation
        window.addEventListener('appinstalled', () => {
            console.log('[PWA] App installed successfully');
            deferredPrompt = null;
            hideInstallButton();
            
            showToast('App installed successfully! You can now use Chilli Care offline.', 'success');
        });
    }

    function showInstallButton() {
        // Create install button if it doesn't exist
        let installBtn = document.getElementById('pwa-install-btn');
        
        if (!installBtn) {
            installBtn = document.createElement('button');
            installBtn.id = 'pwa-install-btn';
            installBtn.className = 'pwa-install-button';
            installBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                <span>Install App</span>
            `;
            
            installBtn.onclick = promptInstall;
            document.body.appendChild(installBtn);
        }
        
        installBtn.style.display = 'flex';
    }

    function hideInstallButton() {
        const installBtn = document.getElementById('pwa-install-btn');
        if (installBtn) {
            installBtn.style.display = 'none';
        }
    }

    async function promptInstall() {
        if (!deferredPrompt) {
            console.log('[PWA] Install prompt not available');
            return;
        }

        // Show the install prompt
        deferredPrompt.prompt();

        // Wait for the user to respond to the prompt
        const { outcome } = await deferredPrompt.userChoice;
        
        console.log(`[PWA] User response to install prompt: ${outcome}`);
        
        if (outcome === 'accepted') {
            console.log('[PWA] User accepted the install prompt');
        } else {
            console.log('[PWA] User dismissed the install prompt');
        }

        // Clear the deferredPrompt
        deferredPrompt = null;
        hideInstallButton();
    }

    // ============================================
    // UPDATE NOTIFICATION
    // ============================================
    
    function showUpdateNotification() {
        // Check if toast function exists
        if (typeof showToast === 'function') {
            showToast(
                'New version available! Refresh to update.',
                'info',
                7000
            );
        } else {
            // Fallback: create custom notification
            const notification = document.createElement('div');
            notification.className = 'pwa-update-notification';
            notification.innerHTML = `
                <div class="update-content">
                    <span>🎉 New version available!</span>
                    <button onclick="window.location.reload()" class="update-btn">
                        Refresh
                    </button>
                </div>
            `;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.display = 'flex';
            }, 100);
        }
    }

    // ============================================
    // NETWORK STATUS MONITORING
    // ============================================
    
    function initNetworkMonitoring() {
        window.addEventListener('online', () => {
            console.log('[PWA] Back online');
            
            if (typeof showToast === 'function') {
                showToast('You\'re back online!', 'success');
            }
            
            // Sync any pending data
            if (swRegistration && swRegistration.sync) {
                swRegistration.sync.register('sync-predictions');
            }
        });

        window.addEventListener('offline', () => {
            console.log('[PWA] Gone offline');
            
            if (typeof showToast === 'function') {
                showToast('You\'re offline. Some features may be limited.', 'warning', 5000);
            }
        });

        // Initial status check
        if (!navigator.onLine) {
            console.log('[PWA] Currently offline');
        }
    }

    // Initialize network monitoring
    initNetworkMonitoring();

    // ============================================
    // CACHE MANAGEMENT
    // ============================================
    
    // Function to manually cache important URLs
    window.cacheImportantUrls = async function(urls) {
        if (!swRegistration) {
            console.warn('[PWA] Service Worker not registered');
            return;
        }

        if (swRegistration.active) {
            swRegistration.active.postMessage({
                type: 'CACHE_URLS',
                urls: urls
            });
        }
    };

    // Function to clear caches (for debugging)
    window.clearPWACache = async function() {
        if ('caches' in window) {
            const cacheNames = await caches.keys();
            await Promise.all(
                cacheNames.map(cacheName => caches.delete(cacheName))
            );
            console.log('[PWA] All caches cleared');
            
            if (swRegistration) {
                await swRegistration.unregister();
                console.log('[PWA] Service Worker unregistered');
            }
            
            window.location.reload();
        }
    };

    // ============================================
    // UTILITY FUNCTIONS
    // ============================================
    
    // Check if app is installed
    window.isPWAInstalled = function() {
        return window.matchMedia('(display-mode: standalone)').matches ||
               window.navigator.standalone === true;
    };

    // Get installation status
    if (window.isPWAInstalled()) {
        console.log('[PWA] Running as installed app');
        // Add class to body for styling
        document.body.classList.add('pwa-installed');
    }

    // Log PWA capabilities
    console.log('[PWA] Capabilities:', {
        serviceWorker: 'serviceWorker' in navigator,
        cache: 'caches' in window,
        notifications: 'Notification' in window,
        pushManager: 'PushManager' in window,
        sync: 'sync' in (swRegistration || {}),
        installed: window.isPWAInstalled()
    });

})();
