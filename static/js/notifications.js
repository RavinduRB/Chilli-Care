// Notification System JavaScript
// Handles fetching, displaying, and managing notifications

document.addEventListener('DOMContentLoaded', function() {
    // Notification Elements
    const notificationSection = document.getElementById('notificationSection');
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationDropdown = document.getElementById('notificationDropdown');
    const notificationBadge = document.getElementById('notificationBadge');
    const notificationList = document.getElementById('notificationList');
    const markAllReadBtn = document.getElementById('markAllReadBtn');
    const viewAllBtn = document.getElementById('viewAllBtn');
    
    // Mobile Notification Elements
    const mobileNotificationBtn = document.getElementById('mobileNotificationBtn');
    const mobileNotificationBadge = document.getElementById('mobileNotificationBadge');
    
    // Notification Modal Elements
    const notificationModal = document.getElementById('notificationModal');
    const closeNotificationModal = document.getElementById('closeNotificationModal');
    const allNotificationsList = document.getElementById('allNotificationsList');
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    // Notification Detail Modal Elements
    const notificationDetailModal = document.getElementById('notificationDetailModal');
    const closeNotificationDetailModal = document.getElementById('closeNotificationDetailModal');
    const notificationDetailTitle = document.getElementById('notificationDetailTitle');
    const notificationDetailType = document.getElementById('notificationDetailType');
    const notificationDetailTime = document.getElementById('notificationDetailTime');
    const notificationDetailMessage = document.getElementById('notificationDetailMessage');
    
    let currentFilter = 'all';
    let notificationCheckInterval = null;
    
    // ============================================
    // Notification Functions
    // ============================================
    
    // Check if user is logged in
    async function isUserLoggedIn() {
        try {
            const response = await fetch('/api/auth/status');
            const data = await response.json();
            return data.authenticated ? data.user : false;
        } catch (error) {
            console.error('Error checking auth status:', error);
            return false;
        }
    }
    
    // Initialize notification system
    async function initNotifications() {
        const user = await isUserLoggedIn();
        const loggedIn = !!user;
        
        if (loggedIn) {
            // Don't show notification bell for admin users
            if (user.user_type === 'admin') return;
            
            // Show notification bell
            if (notificationSection) {
                notificationSection.classList.remove('hidden');
            }
            
            // Load initial notifications
            await loadNotifications();
            await updateNotificationCount();
            
            // Start periodic checking (every 30 seconds)
            notificationCheckInterval = setInterval(async () => {
                await updateNotificationCount();
            }, 30000);
        } else {
            // Hide notification bell
            if (notificationSection) {
                notificationSection.classList.add('hidden');
            }
        }
    }
    
    // Fetch notification count
    async function updateNotificationCount() {
        try {
            const response = await fetch('/api/notifications/count');
            const data = await response.json();
            
            if (data.success) {
                const count = data.unread_count;
                
                // Update desktop badge
                if (notificationBadge) {
                    if (count > 0) {
                        notificationBadge.textContent = count > 99 ? '99+' : count;
                        notificationBadge.classList.remove('hidden');
                    } else {
                        notificationBadge.classList.add('hidden');
                    }
                }
                
                // Update mobile badge
                if (mobileNotificationBadge) {
                    if (count > 0) {
                        mobileNotificationBadge.textContent = count > 99 ? '99+' : count;
                        mobileNotificationBadge.classList.remove('hidden');
                    } else {
                        mobileNotificationBadge.classList.add('hidden');
                    }
                }
            }
        } catch (error) {
            console.error('Error fetching notification count:', error);
        }
    }
    
    // Load notifications
    async function loadNotifications(limit = 10, filter = null) {
        try {
            let url = `/api/notifications?limit=${limit}`;
            if (filter && filter !== 'all') {
                if (filter === 'unread') {
                    url += '&unread_only=true';
                } else if (filter === 'admin' || filter === 'system') {
                    const type = filter === 'admin' ? 'admin_reply' : 'system_update';
                    url += `&type=${type}`;
                }
            }
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success) {
                displayNotifications(data.notifications, notificationList);
                return data.notifications;
            }
        } catch (error) {
            console.error('Error loading notifications:', error);
            if (notificationList) {
                notificationList.innerHTML = `
                    <div class="notification-empty">
                        <i class="fas fa-exclamation-circle"></i>
                        <p>Failed to load notifications</p>
                    </div>
                `;
            }
        }
    }
    
    // Load all notifications for modal
    async function loadAllNotifications(filter = 'all') {
        try {
            let url = '/api/notifications?limit=50';
            if (filter === 'unread') {
                url += '&unread_only=true';
            } else if (filter === 'admin' || filter === 'system') {
                const type = filter === 'admin' ? 'admin_reply' : 'system_update';
                url += `&type=${type}`;
            }
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success) {
                displayNotifications(data.notifications, allNotificationsList);
            }
        } catch (error) {
            console.error('Error loading all notifications:', error);
            if (allNotificationsList) {
                allNotificationsList.innerHTML = `
                    <div class="notification-empty">
                        <i class="fas fa-exclamation-circle"></i>
                        <p>Failed to load notifications</p>
                    </div>
                `;
            }
        }
    }
    
    // Display notifications in a container
    function displayNotifications(notifications, container) {
        if (!container) return;
        
        if (notifications.length === 0) {
            container.innerHTML = `
                <div class="notification-empty">
                    <i class="fas fa-bell-slash"></i>
                    <p>No notifications</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = '';
        
        notifications.forEach(notification => {
            const notifElement = createNotificationElement(notification);
            container.appendChild(notifElement);
        });
    }
    
    // Create notification element
    function createNotificationElement(notification) {
        const div = document.createElement('div');
        div.className = `notification-item ${notification.read ? '' : 'unread'}`;
        div.dataset.notificationId = notification._id;
        
        // Determine icon based on type
        const iconClass = notification.type === 'admin_reply' ? 'admin' : 'system';
        const icon = notification.type === 'admin_reply' ? 'fa-reply' : 'fa-bell';
        
        // Format time
        const timeAgo = formatTimeAgo(notification.created_at);
        
        // Truncate message preview
        const previewMessage = notification.message.length > 80
            ? notification.message.substring(0, 80) + '...'
            : notification.message;
        
        div.innerHTML = `
            <div class="notification-item-content">
                <div class="notification-icon ${iconClass}">
                    <i class="fas ${icon}"></i>
                </div>
                <div class="notification-text">
                    <div class="notification-title">${escapeHtml(notification.title)}</div>
                    <div class="notification-message">${escapeHtml(previewMessage)}</div>
                    <div class="notification-time">${timeAgo}</div>
                </div>
                <div class="notification-read-btn" title="Read message">
                    <i class="fas fa-chevron-right"></i>
                </div>
            </div>
        `;
        
        // Open detail modal when clicked
        div.addEventListener('click', async () => {
            // Mark as read
            if (!notification.read) {
                await markNotificationAsRead(notification._id);
                div.classList.remove('unread');
                notification.read = true;
                await updateNotificationCount();
            }
            
            // Open detail modal
            openNotificationDetail(notification);
        });
        
        return div;
    }
    
    // Open notification detail modal
    function openNotificationDetail(notification) {
        if (!notificationDetailModal) return;
        
        const typeLabel = notification.type === 'admin_reply' ? 'Admin Reply' : 'System Update';
        const timeFormatted = new Date(notification.created_at).toLocaleString('en-US', {
            year: 'numeric', month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
        
        // Populate detail modal
        if (notificationDetailTitle) {
            notificationDetailTitle.innerHTML = `<i class="fas fa-envelope-open"></i> ${escapeHtml(notification.title)}`;
        }
        if (notificationDetailType) {
            notificationDetailType.textContent = typeLabel;
            notificationDetailType.className = `notification-detail-type ${notification.type === 'admin_reply' ? 'type-admin' : 'type-system'}`;
        }
        if (notificationDetailTime) {
            notificationDetailTime.textContent = timeFormatted;
        }
        if (notificationDetailMessage) {
            notificationDetailMessage.textContent = notification.message;
        }
        
        notificationDetailModal.classList.remove('hidden');
    }
    
    // Mark notification as read
    async function markNotificationAsRead(notificationId) {
        try {
            await fetch(`/api/notifications/${notificationId}/read`, {
                method: 'POST'
            });
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }
    
    // Mark all notifications as read
    async function markAllAsRead() {
        try {
            const response = await fetch('/api/notifications/mark-all-read', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Reload notifications
                await loadNotifications();
                await updateNotificationCount();
                
                // Show success message
                console.log('All notifications marked as read');
            }
        } catch (error) {
            console.error('Error marking all as read:', error);
        }
    }
    
    // Format time ago
    function formatTimeAgo(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);
        
        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`;
        
        return date.toLocaleDateString();
    }
    
    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // ============================================
    // Event Listeners
    // ============================================
    
    // Toggle notification dropdown
    if (notificationBtn) {
        notificationBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            notificationDropdown.classList.toggle('hidden');
            
            // Close profile dropdown if open
            const profileDropdown = document.getElementById('profileDropdown');
            if (profileDropdown) {
                profileDropdown.classList.add('hidden');
            }
            
            // Reload notifications when opened
            if (!notificationDropdown.classList.contains('hidden')) {
                await loadNotifications();
            }
        });
    }
    
    // Mark all as read
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            await markAllAsRead();
        });
    }
    
    // View all notifications
    if (viewAllBtn) {
        viewAllBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            notificationModal.classList.remove('hidden');
            notificationDropdown.classList.add('hidden');
            loadAllNotifications(currentFilter);
        });
    }
    
    // Mobile notification button
    if (mobileNotificationBtn) {
        mobileNotificationBtn.addEventListener('click', () => {
            // Close mobile menu first
            const mobileMenu = document.getElementById('mobileMenu');
            const mobileMenuToggle = document.getElementById('mobileMenuToggle');
            if (mobileMenu) mobileMenu.classList.remove('active');
            if (mobileMenuToggle) {
                const icon = mobileMenuToggle.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
            
            // Open notification modal
            notificationModal.classList.remove('hidden');
            loadAllNotifications(currentFilter);
        });
    }
    
    // Close notification modal
    if (closeNotificationModal) {
        closeNotificationModal.addEventListener('click', () => {
            notificationModal.classList.add('hidden');
        });
    }
    
    // Close notification modal when clicking backdrop
    if (notificationModal) {
        notificationModal.addEventListener('click', (e) => {
            if (e.target === notificationModal) {
                notificationModal.classList.add('hidden');
            }
        });
    }
    
    // Close notification detail modal
    if (closeNotificationDetailModal) {
        closeNotificationDetailModal.addEventListener('click', () => {
            notificationDetailModal.classList.add('hidden');
        });
    }
    
    // Close detail modal when clicking backdrop
    if (notificationDetailModal) {
        notificationDetailModal.addEventListener('click', (e) => {
            if (e.target === notificationDetailModal) {
                notificationDetailModal.classList.add('hidden');
            }
        });
    }
    
    // Filter buttons
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Get filter value
            currentFilter = btn.dataset.filter;
            
            // Reload notifications with filter
            loadAllNotifications(currentFilter);
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (notificationDropdown && !notificationDropdown.contains(e.target) && !notificationBtn.contains(e.target)) {
            notificationDropdown.classList.add('hidden');
        }
    });
    
    // Show notification bell for logged-in users
    function showNotificationBell() {
        if (notificationSection) {
            notificationSection.classList.remove('hidden');
        }
        
        // Load notifications and start checking
        loadNotifications();
        updateNotificationCount();
        
        // Start periodic checking if not already running
        if (!notificationCheckInterval) {
            notificationCheckInterval = setInterval(async () => {
                await updateNotificationCount();
            }, 30000);
        }
    }
    
    // Hide notification bell for logged-out users
    function hideNotificationBell() {
        if (notificationSection) {
            notificationSection.classList.add('hidden');
        }
        
        // Stop periodic checking
        if (notificationCheckInterval) {
            clearInterval(notificationCheckInterval);
            notificationCheckInterval = null;
        }
    }
    
    // Expose functions to window so main.js can access them
    window.showNotificationBell = showNotificationBell;
    window.hideNotificationBell = hideNotificationBell;
    
    // Initialize on page load
    initNotifications();
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (notificationCheckInterval) {
            clearInterval(notificationCheckInterval);
        }
    });
});
