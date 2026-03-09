// Admin Dashboard JavaScript
// Handles dashboard data fetching, navigation, and interactions

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const loadingOverlay = document.getElementById('loadingOverlay');
    const mobileSidebarToggle = document.getElementById('mobileSidebarToggle');
    const sidebar = document.querySelector('.dashboard-sidebar');
    const navItems = document.querySelectorAll('.nav-item');
    const contentSections = document.querySelectorAll('.content-section');
    const pageTitle = document.getElementById('pageTitle');
    const adminLogoutBtn = document.getElementById('adminLogoutBtn');
    const manualRefreshBtn = document.getElementById('manualRefreshBtn');
    
    // Stats Elements
    const totalFarmersEl = document.getElementById('totalFarmers');
    const totalDiseasesEl = document.getElementById('totalDiseases');
    const totalPlacesEl = document.getElementById('totalPlaces');
    const activityListEl = document.getElementById('activityList');
    
    // Chart
    let aiUsageChart = null;
    
    // Real-time update variables
    let updateInterval = null;
    let lastUpdateTime = null;
    const UPDATE_INTERVAL = 30000; // 30 seconds
    
    // ============================================
    // INITIALIZATION
    // ============================================
    
    // Check authentication on load
    checkAuthStatus();
    
    // Start real-time updates after initial load
    startRealTimeUpdates();
    
    // ============================================
    // AUTHENTICATION
    // ============================================
    
    async function checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status');
            const data = await response.json();
            
            if (!data.authenticated) {
                // Not logged in, redirect to home
                window.location.href = '/';
                return;
            }
            
            if (data.user.user_type !== 'admin') {
                // Not an admin, redirect to home
                showToast('Unauthorized access - Admin only', 'error');
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
                return;
            }
            
            // User is authenticated as admin, load dashboard
            loadDashboardData();
        } catch (error) {
            console.error('Error checking auth status:', error);
            window.location.href = '/';
        }
    }
    
    // ============================================
    // DASHBOARD DATA
    // ============================================
    
    async function loadDashboardData(silent = false) {
        try {
            // Show loading only on initial load
            if (!silent) {
                showLoading();
            } else {
                updateLastRefreshTime();
            }
            
            const response = await fetch('/api/admin/dashboard');
            const data = await response.json();
            
            if (data.success) {
                // Update statistics
                updateStatistics(data.statistics);
                
                // Update disease stats
                updateDiseaseStats(data.disease_stats);
                
                // Update chart
                updateChart(data.statistics);
                
                // Update recent activity
                updateRecentActivity(data.recent_users);
                
                // Update last update time
                lastUpdateTime = new Date();
                updateLastRefreshTime();
                
                // Hide loading overlay
                if (!silent) {
                    hideLoading();
                }
            } else {
                showToast(data.error || 'Failed to load dashboard', 'error');
                if (!silent) {
                    hideLoading();
                }
            }
        } catch (error) {
            console.error('Error loading dashboard:', error);
            if (!silent) {
                showToast('Failed to load dashboard data', 'error');
                hideLoading();
            }
        }
    }
    
    function updateStatistics(stats) {
        // Update total farmers
        if (totalFarmersEl) {
            animateNumber(totalFarmersEl, stats.total_farmers || 0);
        }
        
        // Update total diseases (count unique diseases from disease_stats)
        if (totalDiseasesEl) {
            totalDiseasesEl.textContent = '12'; // Fixed value from design
        }
        
        // Update total places (placeholder)
        if (totalPlacesEl) {
            totalPlacesEl.textContent = '9'; // Fixed value from design
        }
    }
    
    function updateDiseaseStats(diseaseStats) {
        // Store disease stats for future use
        window.diseaseStats = diseaseStats;
    }
    
    function updateChart(stats) {
        const ctx = document.getElementById('aiUsageChart');
        if (!ctx) return;
        
        // Sample data based on the design (showing 4 weeks of data)
        const weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
        
        // Generate data based on actual stats with some variation
        const validationData = [5, 8, 14, 18];
        const chatbotData = [3, 5, 8, 11];
        
        // Destroy existing chart if it exists
        if (aiUsageChart) {
            aiUsageChart.destroy();
        }
        
        // Create new chart with responsive settings
        aiUsageChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: weeks,
                datasets: [
                    {
                        label: 'Validation',
                        data: validationData,
                        borderColor: '#fb923c',
                        backgroundColor: 'rgba(251, 146, 60, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        pointBackgroundColor: '#fb923c',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    },
                    {
                        label: 'Chatbot',
                        data: chatbotData,
                        borderColor: '#4ade80',
                        backgroundColor: 'rgba(74, 222, 128, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        pointBackgroundColor: '#4ade80',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: window.innerWidth < 768 ? 1.5 : 2.5,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: {
                            size: 14,
                            weight: 'bold'
                        },
                        bodyFont: {
                            size: 13
                        },
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#6b7280',
                            font: {
                                size: window.innerWidth < 768 ? 10 : 12
                            },
                            stepSize: 5
                        },
                        grid: {
                            color: '#e5e7eb',
                            drawBorder: false
                        }
                    },
                    x: {
                        ticks: {
                            color: '#6b7280',
                            font: {
                                size: window.innerWidth < 768 ? 10 : 12
                            }
                        },
                        grid: {
                            display: false,
                            drawBorder: false
                        }
                    }
                }
            }
        });
    }
    
    // Handle window resize for responsive chart
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            if (aiUsageChart) {
                // Update chart aspect ratio based on screen size
                aiUsageChart.options.aspectRatio = window.innerWidth < 768 ? 1.5 : 2.5;
                aiUsageChart.options.scales.y.ticks.font.size = window.innerWidth < 768 ? 10 : 12;
                aiUsageChart.options.scales.x.ticks.font.size = window.innerWidth < 768 ? 10 : 12;
                aiUsageChart.update();
            }
        }, 250);
    });
    
    function updateRecentActivity(recentUsers) {
        if (!activityListEl) return;
        
        if (!recentUsers || recentUsers.length === 0) {
            activityListEl.innerHTML = `
                <div class="activity-item">
                    <div class="activity-icon">
                        <i class="fas fa-info-circle"></i>
                    </div>
                    <div class="activity-info">
                        <p class="activity-text">No recent activity</p>
                    </div>
                </div>
            `;
            return;
        }
        
        // Display recent users
        const activityHTML = recentUsers.map(user => {
            const time = user.last_login ? formatTimeAgo(user.last_login) : 'Never';
            return `
                <div class="activity-item">
                    <div class="activity-icon">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="activity-info">
                        <p class="activity-text">User: ${user.email}</p>
                        <p class="activity-time">Last login: ${time}</p>
                    </div>
                </div>
            `;
        }).join('');
        
        activityListEl.innerHTML = activityHTML;
    }
    
    // ============================================
    // NAVIGATION
    // ============================================
    
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all items
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Get section name
            const sectionName = this.getAttribute('data-section');
            
            // Hide all sections
            contentSections.forEach(section => section.classList.remove('active'));
            
            // Show selected section
            const targetSection = document.getElementById(sectionName + 'Section');
            if (targetSection) {
                targetSection.classList.add('active');
            }
            
            // Update page title
            const sectionTitles = {
                'dashboard': 'Welcome, Chilli Care!',
                'users': 'User Management',
                'diseases': 'Disease Management',
                'predictions': 'Prediction History',
                'mapping': 'District Mapping',
                'analytics': 'Analytics'
            };
            
            if (pageTitle && sectionTitles[sectionName]) {
                pageTitle.textContent = sectionTitles[sectionName];
            }
            
            // Close mobile sidebar if open
            if (window.innerWidth <= 1024) {
                sidebar.classList.remove('active');
            }
        });
    });
    
    // Mobile sidebar toggle
    if (mobileSidebarToggle) {
        mobileSidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 1024) {
            if (!sidebar.contains(e.target) && !mobileSidebarToggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        }
    });
    
    // ============================================
    // LOGOUT
    // ============================================
    
    if (adminLogoutBtn) {
        adminLogoutBtn.addEventListener('click', async function() {
            try {
                const response = await fetch('/api/auth/logout', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showToast('Logged out successfully', 'success');
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1000);
                }
            } catch (error) {
                console.error('Logout error:', error);
                showToast('Logout failed', 'error');
            }
        });
    }
    
    // Manual refresh button handler
    if (manualRefreshBtn) {
        manualRefreshBtn.addEventListener('click', async function() {
            // Add spinning animation
            this.classList.add('spinning');
            
            // Refresh dashboard data
            await loadDashboardData(true);
            
            // Remove spinning animation after a short delay
            setTimeout(() => {
                this.classList.remove('spinning');
            }, 500);
            
            showToast('Dashboard refreshed', 'success');
        });
    }
    
    // ============================================
    // REAL-TIME UPDATES
    // ============================================
    
    function startRealTimeUpdates() {
        // Clear any existing interval
        if (updateInterval) {
            clearInterval(updateInterval);
        }
        
        // Set up interval for automatic updates
        updateInterval = setInterval(() => {
            loadDashboardData(true); // Silent update
        }, UPDATE_INTERVAL);
        
        console.log('Real-time updates started (refreshing every 30 seconds)');
    }
    
    function stopRealTimeUpdates() {
        if (updateInterval) {
            clearInterval(updateInterval);
            updateInterval = null;
            console.log('Real-time updates stopped');
        }
    }
    
    function updateLastRefreshTime() {
        const updateIndicator = document.querySelector('.update-indicator');
        if (updateIndicator && lastUpdateTime) {
            const timeAgo = formatTimeAgo(lastUpdateTime.toISOString());
            const timeText = updateIndicator.querySelector('.update-time');
            if (timeText) {
                timeText.textContent = `Updated ${timeAgo}`;
            }
        }
    }
    
    // Update the "last updated" text every 10 seconds
    setInterval(() => {
        updateLastRefreshTime();
    }, 10000);
    
    // Stop updates when page is not visible
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            stopRealTimeUpdates();
        } else {
            startRealTimeUpdates();
            loadDashboardData(true); // Refresh immediately when page becomes visible
        }
    });
    
    // ============================================
    // UTILITY FUNCTIONS
    // ============================================
    
    function showLoading() {
        if (loadingOverlay) {
            loadingOverlay.classList.remove('hidden');
        }
    }
    
    function hideLoading() {
        if (loadingOverlay) {
            loadingOverlay.classList.add('hidden');
        }
    }
    
    function showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        if (!toast) return;
        
        toast.textContent = message;
        toast.className = 'toast show ' + type;
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
    
    function animateNumber(element, target) {
        const duration = 1000;
        const steps = 30;
        const stepValue = target / steps;
        let current = 0;
        
        const timer = setInterval(() => {
            current += stepValue;
            if (current >= target) {
                element.textContent = Math.round(target);
                clearInterval(timer);
            } else {
                element.textContent = Math.round(current);
            }
        }, duration / steps);
    }
    
    function formatTimeAgo(timestamp) {
        try {
            const date = new Date(timestamp);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);
            
            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
            if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
            if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
            
            return date.toLocaleDateString();
        } catch (e) {
            return 'Unknown';
        }
    }
    
    // ============================================
    // USER MANAGEMENT FUNCTIONALITY
    // ============================================
    
    let currentPage = 1;
    let totalPages = 1;
    let usersPerPage = 10;
    let allUsers = [];
    let filteredUsers = [];
    
    async function loadUsers() {
        try {
            const response = await fetch('/api/admin/users');
            if (!response.ok) throw new Error('Failed to fetch users');
            
            const data = await response.json();
            allUsers = data.users || [];
            filteredUsers = [...allUsers];
            
            renderUserTable();
        } catch (error) {
            console.error('Error loading users:', error);
            showUserError('Failed to load users. Please try again.');
        }
    }
    
    function renderUserTable() {
        const tableBody = document.getElementById('userTableBody');
        if (!tableBody) return;
        
        // Calculate pagination
        totalPages = Math.ceil(filteredUsers.length / usersPerPage) || 1;
        currentPage = Math.min(currentPage, totalPages);
        
        const startIndex = (currentPage - 1) * usersPerPage;
        const endIndex = startIndex + usersPerPage;
        const pageUsers = filteredUsers.slice(startIndex, endIndex);
        
        if (pageUsers.length === 0) {
            tableBody.innerHTML = `
                <tr class="empty-state">
                    <td colspan="6">
                        <div class="empty-state">
                            <i class="fas fa-users"></i>
                            <h3>No Users Found</h3>
                            <p>No users match your search criteria</p>
                        </div>
                    </td>
                </tr>
            `;
        } else {
            tableBody.innerHTML = pageUsers.map((user, index) => {
                const userId = `#USR-${String(startIndex + index + 1).padStart(3, '0')}`;
                const userType = user.user_type || 'Farmer';
                const email = user.email || 'N/A';
                const lastLogin = user.last_login ? formatDate(user.last_login) : 'Never';
                const isOnline = isUserOnline(user.last_login);
                const statusClass = isOnline ? 'status-online' : 'status-offline';
                const statusText = isOnline ? 'Log In' : 'Log Out';
                
                return `
                    <tr>
                        <td><span class="user-id">${userId}</span></td>
                        <td><span class="user-type">${userType}</span></td>
                        <td><span class="user-email">${email}</span></td>
                        <td><span class="user-password">*******</span></td>
                        <td><span class="user-date">${lastLogin}</span></td>
                        <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                    </tr>
                `;
            }).join('');
        }
        
        updatePaginationControls();
    }
    
    function formatDate(timestamp) {
        try {
            const date = new Date(timestamp);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}/${month}/${day}`;
        } catch (e) {
            return 'N/A';
        }
    }
    
    function isUserOnline(lastLogin) {
        if (!lastLogin) return false;
        
        const now = new Date();
        const loginDate = new Date(lastLogin);
        const diffHours = (now - loginDate) / (1000 * 60 * 60);
        
        // Consider user online if last login was within 24 hours
        return diffHours < 24;
    }
    
    function updatePaginationControls() {
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');
        const pageInfo = document.getElementById('pageInfo');
        
        if (prevBtn) {
            prevBtn.disabled = currentPage <= 1;
        }
        
        if (nextBtn) {
            nextBtn.disabled = currentPage >= totalPages;
        }
        
        if (pageInfo) {
            pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
        }
    }
    
    function showUserError(message) {
        const tableBody = document.getElementById('userTableBody');
        if (tableBody) {
            tableBody.innerHTML = `
                <tr class="empty-state">
                    <td colspan="6">
                        <div class="empty-state">
                            <i class="fas fa-exclamation-circle"></i>
                            <h3>Error</h3>
                            <p>${message}</p>
                        </div>
                    </td>
                </tr>
            `;
        }
    }
    
    // Search and Filter
    function setupUserFilters() {
        const searchInput = document.getElementById('userSearchInput');
        const statusFilter = document.getElementById('userStatusFilter');
        
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                filterUsers();
            });
        }
        
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                filterUsers();
            });
        }
    }
    
    function filterUsers() {
        const searchInput = document.getElementById('userSearchInput');
        const statusFilter = document.getElementById('userStatusFilter');
        
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const statusValue = statusFilter ? statusFilter.value : 'all';
        
        filteredUsers = allUsers.filter(user => {
            // Search filter (search in date)
            const lastLogin = user.last_login ? formatDate(user.last_login) : '';
            const matchesSearch = lastLogin.includes(searchTerm) || 
                                 user.email.toLowerCase().includes(searchTerm) ||
                                 user.user_type.toLowerCase().includes(searchTerm);
            
            // Status filter
            let matchesStatus = true;
            if (statusValue === 'online') {
                matchesStatus = isUserOnline(user.last_login);
            } else if (statusValue === 'offline') {
                matchesStatus = !isUserOnline(user.last_login);
            }
            
            return matchesSearch && matchesStatus;
        });
        
        currentPage = 1; // Reset to first page when filtering
        renderUserTable();
    }
    
    // Pagination handlers
    function setupPagination() {
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (currentPage > 1) {
                    currentPage--;
                    renderUserTable();
                }
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (currentPage < totalPages) {
                    currentPage++;
                    renderUserTable();
                }
            });
        }
    }
    
    // Initialize user management when section is shown
    function initUserManagement() {
        setupUserFilters();
        setupPagination();
        loadUsers();
    }
    
    // Load users when user management tab is clicked
    const userManagementNav = document.querySelector('[data-section="users"]');
    if (userManagementNav) {
        userManagementNav.addEventListener('click', () => {
            // Small delay to ensure section is visible
            setTimeout(() => {
                if (allUsers.length === 0) {
                    initUserManagement();
                }
            }, 100);
        });
    }

});
