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
    const manualRefreshBtn = document.getElementById('manualRefreshBtn');
    
    // Stats Elements
    const totalFarmersEl = document.getElementById('totalFarmers');
    const totalPredictionsEl = document.getElementById('totalPredictions');
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
        // Update total farmers (only farmers, not admin) - no animation, just direct value
        if (totalFarmersEl) {
            totalFarmersEl.textContent = stats.total_farmers || 0;
        }
        
        // Update total predictions (all predictions made by farmers)
        if (totalPredictionsEl) {
            totalPredictionsEl.textContent = stats.total_predictions || 0;
        }
        
        // Update total places (unique locations based on IP addresses)
        if (totalPlacesEl) {
            totalPlacesEl.textContent = stats.unique_locations || 0;
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
                'analytics': 'Analytics',
                'messages': 'Messages Management'
            };
            
            if (pageTitle && sectionTitles[sectionName]) {
                pageTitle.textContent = sectionTitles[sectionName];
            }
            
            // Load data for specific sections when switched
            if (sectionName === 'users' && allUsers.length === 0) {
                // Load users for the first time
                initUserManagement();
            } else if (sectionName === 'users') {
                // Refresh users to get latest data
                loadUsers();
            } else if (sectionName === 'predictions' && allPredictions.length === 0) {
                // Load predictions for the first time
                initPredictionManagement();
            } else if (sectionName === 'predictions') {
                // Refresh predictions to get latest data
                loadPredictions(currentPredictionPage);
            } else if (sectionName === 'messages') {
                // Load messages when switching to messages section
                loadAllMessages();
            } else if (sectionName === 'analytics') {
                // Load analytics when switching to analytics section
                loadAnalyticsData();
            } else if (sectionName === 'mapping') {
                // Load mapping when switching to mapping section
                loadMappingData();
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
    // LOGOUT FUNCTIONALITY
    // ============================================
    
    // DOM Elements for logout confirmation
    const userProfileBtn = document.getElementById('userProfileBtn');
    const logoutConfirmModal = document.getElementById('logoutConfirmModal');
    const closeLogoutModal = document.getElementById('closeLogoutModal');
    const cancelLogoutBtn = document.getElementById('cancelLogoutBtn');
    const confirmLogoutBtn = document.getElementById('confirmLogoutBtn');
    
    // Function to show logout confirmation modal
    function showLogoutConfirmation() {
        if (logoutConfirmModal) {
            logoutConfirmModal.classList.add('active');
        }
    }
    
    // Function to hide logout confirmation modal
    function hideLogoutConfirmation() {
        if (logoutConfirmModal) {
            logoutConfirmModal.classList.remove('active');
        }
    }
    
    // Function to perform logout
    async function performLogout() {
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
    }
    
    // User profile click handler (sidebar)
    if (userProfileBtn) {
        userProfileBtn.addEventListener('click', function() {
            showLogoutConfirmation();
        });
        
        // Also handle keyboard accessibility
        userProfileBtn.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                showLogoutConfirmation();
            }
        });
    }
    
    // Close modal button
    if (closeLogoutModal) {
        closeLogoutModal.addEventListener('click', function() {
            hideLogoutConfirmation();
        });
    }
    
    // Cancel button
    if (cancelLogoutBtn) {
        cancelLogoutBtn.addEventListener('click', function() {
            hideLogoutConfirmation();
        });
    }
    
    // Confirm logout button
    if (confirmLogoutBtn) {
        confirmLogoutBtn.addEventListener('click', async function() {
            hideLogoutConfirmation();
            await performLogout();
        });
    }
    
    // Close modal when clicking outside
    if (logoutConfirmModal) {
        logoutConfirmModal.addEventListener('click', function(e) {
            if (e.target === logoutConfirmModal) {
                hideLogoutConfirmation();
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
            
            // Refresh user table if user management section is active
            const usersSection = document.getElementById('usersSection');
            if (usersSection && usersSection.classList.contains('active')) {
                await loadUsers();
            }
            
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
            
            // Also refresh user table if user management section is active
            const usersSection = document.getElementById('usersSection');
            if (usersSection && usersSection.classList.contains('active')) {
                loadUsers();
            }
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
        if (updateIndicator) {
            const now = new Date();
            const timeAgo = lastUpdateTime ? formatTimeAgo(lastUpdateTime.toISOString()) : 'just now';
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
            
            // Also refresh user table if user management section is active
            const usersSection = document.getElementById('usersSection');
            if (usersSection && usersSection.classList.contains('active')) {
                loadUsers();
            }
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
    
    let currentToastTimeout = null;
    
    function showToast(message, type = 'success', duration = 3000) {
        const toast = document.getElementById('toast');
        if (!toast) return;
        
        // Clear any existing timeout
        if (currentToastTimeout) {
            clearTimeout(currentToastTimeout);
        }
        
        // Add close button for info type toasts
        let toastContent = message;
        if (type === 'info') {
            toastContent = `
                <div class="toast-content">
                    <div class="toast-body">${message}</div>
                    <button class="toast-close" onclick="closeToast()" title="Close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
        }
        
        toast.innerHTML = toastContent;
        toast.className = 'toast show ' + type;
        
        // Auto-close after duration only for non-info toasts
        if (type !== 'info') {
            currentToastTimeout = setTimeout(() => {
                closeToast();
            }, duration);
        }
    }
    
    function handleToastClickOutside(event) {
        const toast = document.getElementById('toast');
        if (!toast) return;
        
        // Check if click is outside the toast
        if (!toast.contains(event.target) && !event.target.closest('.btn-view')) {
            closeToast();
        }
    }
    
    window.closeToast = function() {
        const toast = document.getElementById('toast');
        if (!toast) return;
        
        toast.classList.remove('show');
        
        // Remove click outside listener
        document.removeEventListener('click', handleToastClickOutside);
        
        // Clear timeout
        if (currentToastTimeout) {
            clearTimeout(currentToastTimeout);
            currentToastTimeout = null;
        }
    };
    
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
    // PREDICTION HISTORY FUNCTIONALITY
    // ============================================
    
    let allPredictions = [];
    let filteredPredictions = [];
    let currentPredictionPage = 1;
    const predictionsPerPage = 20;
    
    async function loadPredictions(page = 1) {
        try {
            // Get filter values
            const diseaseFilter = document.getElementById('diseaseFilter')?.value || '';
            const userTypeFilter = document.getElementById('userTypeFilter')?.value || '';
            const confidenceFilter = document.getElementById('confidenceFilter')?.value || '';
            const searchQuery = document.getElementById('predictionSearchInput')?.value || '';
            
            // Build query parameters
            const params = new URLSearchParams({
                page: page,
                limit: predictionsPerPage
            });
            
            if (diseaseFilter) params.append('disease', diseaseFilter);
            if (userTypeFilter) params.append('user_type', userTypeFilter);
            if (confidenceFilter) params.append('confidence', confidenceFilter);
            if (searchQuery) params.append('search', searchQuery);
            
            // Show loading state
            const tableBody = document.getElementById('predictionTableBody');
            if (tableBody) {
                tableBody.innerHTML = `
                    <tr class="loading-row">
                        <td colspan="7" class="text-center">
                            <i class="fas fa-spinner fa-spin"></i> Loading predictions...
                        </td>
                    </tr>
                `;
            }
            
            const response = await fetch(`/api/admin/predictions?${params}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                allPredictions = data.predictions || [];
                currentPredictionPage = page;
                
                // Update statistics
                if (data.statistics) {
                    updatePredictionStatistics(data.statistics);
                }
                
                // Display predictions
                displayPredictions(data.predictions || []);
                
                // Update pagination
                if (data.pagination) {
                    updatePredictionPagination(data.pagination);
                }
            } else {
                showToast(data.error || 'Failed to load predictions', 'error');
                if (tableBody) {
                    tableBody.innerHTML = `
                        <tr class="no-data-row">
                            <td colspan="7" class="text-center">
                                <i class="fas fa-exclamation-triangle"></i>
                                <p>${data.error || 'Failed to load predictions'}</p>
                            </td>
                        </tr>
                    `;
                }
            }
        } catch (error) {
            console.error('Error loading predictions:', error);
            showToast('Failed to load predictions: ' + error.message, 'error');
            const tableBody = document.getElementById('predictionTableBody');
            if (tableBody) {
                tableBody.innerHTML = `
                    <tr class="no-data-row">
                        <td colspan="7" class="text-center">
                            <i class="fas fa-exclamation-triangle"></i>
                            <p>Error loading predictions. Please try again.</p>
                        </td>
                    </tr>
                `;
            }
        }
    }
    
    function updatePredictionStatistics(stats) {
        const totalCountEl = document.getElementById('predictionTotalCount');
        const avgConfidenceEl = document.getElementById('predictionAvgConfidence');
        const healthyCountEl = document.getElementById('predictionHealthyCount');
        const diseaseCountEl = document.getElementById('predictionDiseaseCount');
        
        if (totalCountEl) totalCountEl.textContent = (stats.total_predictions || 0).toLocaleString();
        if (avgConfidenceEl) avgConfidenceEl.textContent = Math.round(stats.avg_confidence || 0) + '%';
        if (healthyCountEl) healthyCountEl.textContent = (stats.healthy_count || 0).toLocaleString();
        if (diseaseCountEl) diseaseCountEl.textContent = (stats.diseased_count || 0).toLocaleString();
    }
    
    function displayPredictions(predictions) {
        const tableBody = document.getElementById('predictionTableBody');
        if (!tableBody) return;
        
        if (predictions.length === 0) {
            tableBody.innerHTML = `
                <tr class="no-data-row">
                    <td colspan="7" class="text-center">
                        <i class="fas fa-inbox"></i>
                        <p>No predictions found</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        let html = '';
        predictions.forEach(prediction => {
            const date = new Date(prediction.timestamp);
            const formattedDate = date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });
            const formattedTime = date.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit'
            });
            
            // Format disease name
            const diseaseName = formatDiseaseName(prediction.predicted_disease);
            
            // Confidence badge color
            const confidenceValue = Math.round(prediction.confidence);
            let confidenceBadge = 'badge-success';
            if (confidenceValue < 70) {
                confidenceBadge = 'badge-danger';
            } else if (confidenceValue < 90) {
                confidenceBadge = 'badge-warning';
            }
            
            // Validation badge
            let validationBadge = 'badge-secondary';
            let validationText = prediction.validation_method || 'None';
            if (validationText.toLowerCase().includes('gemini')) {
                validationBadge = 'badge-primary';
            } else if (validationText.toLowerCase().includes('blip')) {
                validationBadge = 'badge-info';
            }
            
            // User type badge
            const userEmail = prediction.user_email || 'Anonymous';
            const userType = prediction.user_type || 'guest';
            const userTypeBadge = userType === 'farmer' ? 'badge-success' : 'badge-secondary';
            
            // Location display
            const location = prediction.location || 'Unknown';
            
            html += `
                <tr>
                    <td>
                        <div class="prediction-date">
                            <div class="date-main">${formattedDate}</div>
                            <div class="date-time">${formattedTime}</div>
                        </div>
                    </td>
                    <td>
                        <div class="user-info-cell">
                            <div class="user-email">${userEmail}</div>
                            <span class="badge ${userTypeBadge}">${userType}</span>
                        </div>
                    </td>
                    <td>
                        <div class="disease-cell">
                            <span class="disease-name">${diseaseName}</span>
                        </div>
                    </td>
                    <td>
                        <span class="confidence-badge ${confidenceBadge}">
                            ${confidenceValue}%
                        </span>
                    </td>
                    <td>
                        <div class="location-cell">
                            <i class="fas fa-map-marker-alt"></i>
                            ${location}
                        </div>
                    </td>
                    <td>
                        <span class="validation-badge ${validationBadge}">
                            ${validationText}
                        </span>
                    </td>
                </tr>
            `;
        });
        
        tableBody.innerHTML = html;
    }
    
    function formatDiseaseName(disease) {
        // Convert database format to display format
        const diseaseMap = {
            'Chilli___healthy': 'Healthy',
            'Chilli __Whitefly': 'Whitefly',
            'Chilli__Anthacnose': 'Anthacnose',
            'Chilli __Yellowish': 'Yellowish',
            'Chilli__Leaf_Curl_Virus': 'Leaf Curl Virus',
            // Also handle space-separated format
            'Chilli healthy': 'Healthy',
            'Chilli Whitefly': 'Whitefly',
            'Chilli Anthacnose': 'Anthacnose',
            'Chilli Yellowish': 'Yellowish',
            'Chilli Leaf Curl Virus': 'Leaf Curl Virus'
        };
        return diseaseMap[disease] || disease;
    }
    
    function updatePredictionPagination(pagination) {
        const pageInfo = document.getElementById('predictionPageInfo');
        const prevBtn = document.getElementById('predictionPrevPageBtn');
        const nextBtn = document.getElementById('predictionNextPageBtn');
        
        if (pageInfo) {
            pageInfo.textContent = `Page ${pagination.page} of ${pagination.pages}`;
        }
        
        if (prevBtn) {
            prevBtn.disabled = pagination.page <= 1;
        }
        
        if (nextBtn) {
            nextBtn.disabled = pagination.page >= pagination.pages;
        }
    }
    
    async function populateDiseaseFilter() {
        try {
            const diseaseFilter = document.getElementById('diseaseFilter');
            if (!diseaseFilter) return;
            
            // Get all predictions to extract unique diseases
            const response = await fetch('/api/admin/predictions?page=1&limit=1000');
            if (!response.ok) return;
            
            const data = await response.json();
            if (!data.success || !data.predictions) return;
            
            // Extract unique disease names
            const diseases = [...new Set(data.predictions.map(p => p.predicted_disease))].sort();
            
            // Populate the filter (keep "All Diseases" option)
            let options = '<option value="">All Diseases</option>';
            diseases.forEach(disease => {
                const displayName = formatDiseaseName(disease);
                options += `<option value="${disease}">${displayName}</option>`;
            });
            
            diseaseFilter.innerHTML = options;
        } catch (error) {
            console.error('Error populating disease filter:', error);
            // Keep default options if error occurs
        }
    }
    
    function initPredictionManagement() {
        // Load initial predictions
        loadPredictions(1);
        
        // Populate disease filter dynamically
        populateDiseaseFilter();
        
        // Set up filter event listeners
        const diseaseFilter = document.getElementById('diseaseFilter');
        const userTypeFilter = document.getElementById('userTypeFilter');
        const confidenceFilter = document.getElementById('confidenceFilter');
        const searchInput = document.getElementById('predictionSearchInput');
        
        if (diseaseFilter) {
            diseaseFilter.addEventListener('change', () => loadPredictions(1));
        }
        
        if (userTypeFilter) {
            userTypeFilter.addEventListener('change', () => loadPredictions(1));
        }
        
        if (confidenceFilter) {
            confidenceFilter.addEventListener('change', () => loadPredictions(1));
        }
        
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    loadPredictions(1);
                }, 500);
            });
        }
        
        // Set up pagination buttons
        const prevBtn = document.getElementById('predictionPrevPageBtn');
        const nextBtn = document.getElementById('predictionNextPageBtn');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (currentPredictionPage > 1) {
                    loadPredictions(currentPredictionPage - 1);
                }
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                loadPredictions(currentPredictionPage + 1);
            });
        }
    }
    
    // View prediction details
    window.viewPredictionDetails = function(predictionId) {
        const prediction = allPredictions.find(p => p._id === predictionId);
        if (!prediction) {
            showToast('Prediction not found', 'error');
            return;
        }
        
        // Format timestamp
        const timestamp = prediction.timestamp ? new Date(prediction.timestamp).toLocaleString() : 'N/A';
        
        // Format confidence
        const confidence = Math.round(prediction.confidence);
        
        // Show prediction details in a toast or modal
        let detailsMessage = `
            <div style="text-align: left;">
                <strong style="font-size: 1.1em;">📊 Prediction Details</strong><br><br>
                <strong>🦠 Disease:</strong> ${formatDiseaseName(prediction.predicted_disease)}<br>
                <strong>📈 Confidence:</strong> ${confidence}%<br>
                <strong>👤 User:</strong> ${prediction.user_email || 'Anonymous'}<br>
                <strong>👥 User Type:</strong> ${prediction.user_type || 'guest'}<br>
                <strong>📍 Location:</strong> ${prediction.location || 'Unknown'}<br>
                <strong>✅ Validation:</strong> ${prediction.validation_method || 'None'}<br>
                <strong>🕒 Time:</strong> ${timestamp}
        `;
        
        if (prediction.validation_message) {
            detailsMessage += `<br><strong>💬 Message:</strong> ${prediction.validation_message}`;
        }
        
        if (prediction.top_3_predictions && prediction.top_3_predictions.length > 0) {
            detailsMessage += '<br><br><strong>🏆 Top 3 Predictions:</strong><br>';
            prediction.top_3_predictions.forEach((pred, idx) => {
                const predConfidence = Math.round(pred[1]);
                detailsMessage += `&nbsp;&nbsp;${idx + 1}. ${formatDiseaseName(pred[0])}: <strong>${predConfidence}%</strong><br>`;
            });
        }
        
        detailsMessage += '</div>';
        
        showToast(detailsMessage, 'info', 10000);
    };
    
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
            
            
            // Update the last refresh time indicator
            lastUpdateTime = new Date();
            updateLastRefreshTime();
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
                // Use actual login status from database
                const isLoggedIn = user.is_logged_in === true;
                const statusClass = isLoggedIn ? 'status-online' : 'status-offline';
                const statusText = isLoggedIn ? 'Login' : 'Logout';
                
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
            
            // Status filter - use actual login status
            let matchesStatus = true;
            if (statusValue === 'online') {
                matchesStatus = user.is_logged_in === true;
            } else if (statusValue === 'offline') {
                matchesStatus = user.is_logged_in !== true;
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
    
    // ============================================
    // DISEASE MODAL
    // ============================================
    
    // Track current disease and edit mode
    let currentDiseaseData = null;
    let isEditMode = false;
    
    // Make functions global
    window.openDiseaseModal = async function(diseaseType) {
        const modal = document.getElementById('diseaseModal');
        
        // Map disease types to full names
        const diseaseNameMap = {
            'healthy': 'Chilli healthy',
            'whitefly': 'Chilli Whitefly',
            'anthacnose': 'Chilli Anthacnose',
            'yellowish': 'Chilli Yellowish',
            'leafcurl': 'Chilli Leaf Curl Virus'
        };
        
        const diseaseName = diseaseNameMap[diseaseType];
        
        if (!diseaseName) {
            console.error('Disease type not found:', diseaseType);
            showToast('Disease not found', 'error');
            return;
        }
        
        try {
            // Show loading
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            
            // Show loading state
            document.getElementById('diseaseModalTitle').textContent = 'Loading...';
            document.getElementById('diseaseModalName').textContent = 'Loading...';
            
            // Fetch disease data from API
            const response = await fetch(`/api/admin/diseases/${encodeURIComponent(diseaseName)}`);
            
            // Log for debugging
            console.log('Fetch status:', response.status, 'URL:', `/api/admin/diseases/${encodeURIComponent(diseaseName)}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('API Error:', response.status, errorText);
                showToast(`Failed to load disease data (${response.status})`, 'error');
                closeDiseaseModal();
                return;
            }
            
            const result = await response.json();
            
            if (!result.success) {
                showToast(result.error || 'Failed to load disease data', 'error');
                closeDiseaseModal();
                return;
            }
            
            const data = result.disease;
            currentDiseaseData = data;
            isEditMode = false;
            
            // Update modal content
            updateModalContent(data, false);
            
        } catch (error) {
            console.error('Error fetching disease data:', error);
            showToast('Failed to load disease data', 'error');
            closeDiseaseModal();
        }
    };
    
    function updateModalContent(data, editMode) {
        // Update title and name
        document.getElementById('diseaseModalTitle').textContent = data.name;
        document.getElementById('diseaseModalName').textContent = data.name;
        
        // Update image
        const imageEl = document.getElementById('diseaseModalImage');
        const imageMap = {
            'Chilli healthy': '/static/images/Chilli___healthy.jpg',
            'Chilli Whitefly': '/static/images/Chilli%20__Whitefly.jpg',
            'Chilli Anthacnose': '/static/images/Chilli__Anthacnose.jpg',
            'Chilli Yellowish': '/static/images/Chilli%20__Yellowish.jpg',
            'Chilli Leaf Curl Virus': '/static/images/Chilli__Leaf_Curl_Virus.jpg'
        };
        imageEl.src = imageMap[data.name] || '';
        imageEl.alt = data.name;
        
        if (editMode) {
            // Make fields editable
            document.getElementById('diseaseModalDescription').innerHTML = 
                `<textarea class="edit-textarea" id="editDescription">${data.description || ''}</textarea>`;
            
            document.getElementById('diseaseModalSeverity').innerHTML = 
                `<input type="text" class="edit-input" id="editSeverity" value="${data.severity || ''}">`;
            
            // Editable lists
            document.getElementById('diseaseModalCauses').innerHTML = 
                createEditableList(data.causes || [], 'editCauses');
            
            document.getElementById('diseaseModalSolutions').innerHTML = 
                createEditableList(data.organic_solutions || [], 'editSolutions');
            
            document.getElementById('diseaseModalSymptoms').innerHTML = 
                createEditableList(data.symptoms || [], 'editSymptoms');
            
            document.getElementById('diseaseModalTreatment').innerHTML = 
                createEditableList(data.treatment || [], 'editTreatment');
            
            // Show save button, hide edit button
            document.querySelector('.btn-modal-edit').style.display = 'none';
            document.querySelector('.btn-modal-save').style.display = 'block';
            
        } else {
            // Display mode (read-only)
            document.getElementById('diseaseModalDescription').innerHTML = 
                `<p>${data.description || '-'}</p>`;
            
            document.getElementById('diseaseModalSeverity').innerHTML = 
                `<p>${data.severity || '-'}</p>`;
            
            // Display lists
            document.getElementById('diseaseModalCauses').innerHTML = 
                (data.causes || []).map(item => `<li>${item}</li>`).join('');
            
            document.getElementById('diseaseModalSolutions').innerHTML = 
                (data.organic_solutions || []).map(item => `<li>${item}</li>`).join('');
            
            document.getElementById('diseaseModalSymptoms').innerHTML = 
                (data.symptoms || []).map(item => `<li>${item}</li>`).join('');
            
            document.getElementById('diseaseModalTreatment').innerHTML = 
                (data.treatment || []).map(item => `<li>${item}</li>`).join('');
            
            // Show edit button, hide save button
            document.querySelector('.btn-modal-edit').style.display = 'flex';
            document.querySelector('.btn-modal-save').style.display = 'none';
        }
    }
    
    function createEditableList(items, listId) {
        let html = '';
        items.forEach((item, index) => {
            html += `<li><input type="text" class="edit-list-item" data-index="${index}" value="${item}"></li>`;
        });
        // Add button to add new item - use data attribute to find parent list
        html += `<li><button class="btn-add-item" onclick="addListItemByButton(this)"><i class="fas fa-plus"></i> Add Item</button></li>`;
        return html;
    }
    
    window.addListItemByButton = function(button) {
        // Find the parent list element
        const listEl = button.closest('ol');
        if (!listEl) return;
        
        const items = listEl.querySelectorAll('.edit-list-item');
        const newIndex = items.length;
        
        // Insert before the add button
        const addButton = button.parentElement;
        const newLi = document.createElement('li');
        newLi.innerHTML = `<input type="text" class="edit-list-item" data-index="${newIndex}" value="" placeholder="Enter new item">`;
        listEl.insertBefore(newLi, addButton);
        
        // Focus on new input
        newLi.querySelector('input').focus();
    };
    
    // Toggle edit mode
    window.toggleEditMode = function() {
        if (!currentDiseaseData) return;
        
        isEditMode = !isEditMode;
        updateModalContent(currentDiseaseData, isEditMode);
    };
    
    // Save changes
    window.saveDiseaseChanges = async function() {
        if (!currentDiseaseData) return;
        
        try {
            // Collect edited data
            const editedData = {
                description: document.getElementById('editDescription')?.value || '',
                severity: document.getElementById('editSeverity')?.value || '',
                causes: collectListData('diseaseModalCauses'),
                organic_solutions: collectListData('diseaseModalSolutions'),
                symptoms: collectListData('diseaseModalSymptoms'),
                treatment: collectListData('diseaseModalTreatment')
            };
            
            // Show loading
            const saveBtn = document.querySelector('.btn-modal-save');
            const originalText = saveBtn.innerHTML;
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            saveBtn.disabled = true;
            
            // Send to API
            const response = await fetch(`/api/admin/diseases/${encodeURIComponent(currentDiseaseData.name)}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(editedData)
            });
            
            const result = await response.json();
            
            saveBtn.innerHTML = originalText;
            saveBtn.disabled = false;
            
            if (result.success) {
                showToast('Disease updated successfully', 'success');
                
                // Update current data
                currentDiseaseData = result.disease;
                isEditMode = false;
                
                // Switch back to display mode
                updateModalContent(currentDiseaseData, false);
            } else {
                showToast(result.error || 'Failed to save changes', 'error');
            }
            
        } catch (error) {
            console.error('Error saving disease:', error);
            showToast('Failed to save changes', 'error');
            
            // Reset button
            const saveBtn = document.querySelector('.btn-modal-save');
            saveBtn.innerHTML = 'Save';
            saveBtn.disabled = false;
        }
    };
    
    function collectListData(listId) {
        const listEl = document.getElementById(listId);
        
        // Check if element exists
        if (!listEl) {
            console.error('List element not found:', listId);
            return [];
        }
        
        const items = listEl.querySelectorAll('.edit-list-item');
        const data = [];
        
        items.forEach(item => {
            const value = item.value.trim();
            if (value) {
                data.push(value);
            }
        });
        
        return data;
    }
    
    window.closeDiseaseModal = function() {
        const modal = document.getElementById('diseaseModal');
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
        
        // Reset state
        currentDiseaseData = null;
        isEditMode = false;
    };
    
    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeDiseaseModal();
        }
    });
    
    // Setup edit button
    const editBtn = document.querySelector('.btn-modal-edit');
    if (editBtn) {
        editBtn.addEventListener('click', toggleEditMode);
    }
    
    // Setup save button
    const saveBtn = document.querySelector('.btn-modal-save');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveDiseaseChanges);
        saveBtn.style.display = 'none'; // Hidden by default
    }

    // ============================================
    // MESSAGES MANAGEMENT
    // ============================================
    
    // Messages Elements
    const conversationsList = document.getElementById('conversationsList');
    const conversationEmpty = document.getElementById('conversationEmpty');
    const conversationView = document.getElementById('conversationView');
    const conversationMessages = document.getElementById('conversationMessages');
    const conversationUserName = document.getElementById('conversationUserName');
    const conversationUserEmail = document.getElementById('conversationUserEmail');
    const replyForm = document.getElementById('replyForm');
    const replyMessage = document.getElementById('replyMessage');
    const refreshMessagesBtn = document.getElementById('refreshMessagesBtn');
    const closeConversationBtn = document.getElementById('closeConversationBtn');
    const messagesSearchInput = document.getElementById('messagesSearchInput');
    
    let allConversations = [];
    let currentConversationEmail = null;
    
    // Load all messages
    async function loadAllMessages() {
        try {
            if (conversationsList) {
                conversationsList.innerHTML = `
                    <div class="loading-conversations">
                        <i class="fas fa-spinner fa-spin"></i>
                        <p>Loading conversations...</p>
                    </div>
                `;
            }
            
            const response = await fetch('/api/admin/messages');
            const data = await response.json();
            
            if (data.success) {
                allConversations = data.conversations;
                displayConversations(allConversations);
            } else {
                showToast(data.error || 'Failed to load messages', 'error');
                if (conversationsList) {
                    conversationsList.innerHTML = `
                        <div class="messages-empty">
                            <i class="fas fa-exclamation-circle"></i>
                            <h3>Failed to Load</h3>
                            <p>Could not load messages</p>
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error('Error loading messages:', error);
            showToast('Failed to load messages', 'error');
        }
    }
    
    // Display conversations list
    function displayConversations(conversations) {
        if (!conversationsList) return;
        
        if (conversations.length === 0) {
            conversationsList.innerHTML = `
                <div class="messages-empty">
                    <i class="fas fa-inbox"></i>
                    <h3>No Messages</h3>
                    <p>No user messages yet</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        conversations.forEach(conv => {
            const lastMessage = conv.messages[0];
            const timeAgo = formatTimeAgo(conv.last_message_time);
            const preview = lastMessage ? lastMessage.message.substring(0, 50) : 'No message';
            const unreadBadge = conv.unread_count > 0 ? `<span class="conversation-badge">${conv.unread_count}</span>` : '';
            
            html += `
                <div class="conversation-item" data-email="${conv.email}">
                    <div class="conversation-item-header">
                        <div style="flex: 1; min-width: 0;">
                            <div class="conversation-user-name">${escapeHtml(conv.name)}</div>
                            <div class="conversation-user-email">${escapeHtml(conv.email)}</div>
                            <div class="conversation-preview">${escapeHtml(preview)}</div>
                        </div>
                        <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 4px;">
                            <div class="conversation-time">${timeAgo}</div>
                            ${unreadBadge}
                        </div>
                    </div>
                </div>
            `;
        });
        
        conversationsList.innerHTML = html;
        
        // Add click event listeners
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.addEventListener('click', function() {
                const email = this.getAttribute('data-email');
                loadConversation(email);
                
                // Mark as active
                document.querySelectorAll('.conversation-item').forEach(i => i.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }
    
    // Load specific conversation
    async function loadConversation(email) {
        try {
            currentConversationEmail = email;
            
            // Show loading in conversation view
            if (conversationMessages) {
                conversationMessages.innerHTML = `
                    <div style="text-align: center; padding: 40px;">
                        <i class="fas fa-spinner fa-spin" style="font-size: 32px; color: #9ca3af;"></i>
                    </div>
                `;
            }
            
            // Hide empty state and show conversation view
            if (conversationEmpty) conversationEmpty.style.display = 'none';
            if (conversationView) conversationView.classList.remove('hidden');
            
            const response = await fetch(`/api/admin/messages/${encodeURIComponent(email)}`);
            const data = await response.json();
            
            if (data.success) {
                displayConversation(data.messages, email);
                
                // Mark messages as read
                data.messages.forEach(msg => {
                    if (msg.status === 'new' && msg.type !== 'admin_reply') {
                        markMessageAsRead(msg._id);
                    }
                });
                
                // Update conversation unread count in sidebar
                const conversationItem = document.querySelector(`.conversation-item[data-email="${email}"]`);
                if (conversationItem) {
                    const badge = conversationItem.querySelector('.conversation-badge');
                    if (badge) badge.remove();
                }
            } else {
                showToast(data.error || 'Failed to load conversation', 'error');
            }
        } catch (error) {
            console.error('Error loading conversation:', error);
            showToast('Failed to load conversation', 'error');
        }
    }
    
    // Display conversation messages
    function displayConversation(messages, email) {
        if (!conversationMessages || !conversationUserName || !conversationUserEmail) return;
        
        // Update header - find the user's actual name (not "Admin")
        if (messages.length > 0) {
            // Find first non-admin message to get user's real name
            const userMessage = messages.find(msg => msg.type !== 'admin_reply');
            const userName = userMessage ? userMessage.name : messages[0].name;
            conversationUserName.textContent = userName;
            conversationUserEmail.textContent = email;
        }
        
        // Display messages
        let html = '';
        messages.forEach(msg => {
            const isAdminReply = msg.type === 'admin_reply';
            const messageClass = isAdminReply ? 'admin-message' : 'user-message';
            const timeFormatted = formatMessageTime(msg.timestamp);
            const statusBadge = msg.status ? `<span class="message-status ${msg.status}">${msg.status}</span>` : '';
            
            html += `
                <div class="message-bubble ${messageClass}">
                    <div class="message-content">
                        <div class="message-header">
                            <span class="message-sender">${escapeHtml(msg.name)}</span>
                            <span class="message-time">${timeFormatted}</span>
                        </div>
                        ${msg.subject && !isAdminReply ? `<div class="message-subject">${escapeHtml(msg.subject)}</div>` : ''}
                        <div class="message-text">${escapeHtml(msg.message)}</div>
                        ${!isAdminReply ? statusBadge : ''}
                    </div>
                </div>
            `;
        });
        
        conversationMessages.innerHTML = html;
        
        // Scroll to bottom
        conversationMessages.scrollTop = conversationMessages.scrollHeight;
    }
    
    // Mark message as read
    async function markMessageAsRead(messageId) {
        try {
            await fetch(`/api/admin/messages/${messageId}/mark-read`, {
                method: 'POST'
            });
        } catch (error) {
            console.error('Error marking message as read:', error);
        }
    }
    
    // Send reply
    if (replyForm) {
        replyForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!currentConversationEmail) {
                showToast('No conversation selected', 'error');
                return;
            }
            
            const message = replyMessage.value.trim();
            if (!message) {
                showToast('Please enter a message', 'error');
                return;
            }
            
            try {
                // Disable form
                replyMessage.disabled = true;
                const submitBtn = replyForm.querySelector('.whatsapp-send-btn');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                }
                
                const response = await fetch(`/api/admin/messages/${encodeURIComponent(currentConversationEmail)}/reply`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showToast('Reply sent successfully', 'success');
                    
                    // Clear form
                    replyMessage.value = '';
                    
                    // Reset textarea height
                    replyMessage.style.height = 'auto';
                    
                    // Reload conversation to show new message
                    await loadConversation(currentConversationEmail);
                    
                    // Reload conversations list to update preview
                    await loadAllMessages();
                } else {
                    showToast(data.error || 'Failed to send reply', 'error');
                }
            } catch (error) {
                console.error('Error sending reply:', error);
                showToast('Failed to send reply', 'error');
            } finally {
                // Re-enable form
                replyMessage.disabled = false;
                const submitBtn = replyForm.querySelector('.whatsapp-send-btn');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
                }
            }
        });
    }
    
    // Refresh messages button
    if (refreshMessagesBtn) {
        refreshMessagesBtn.addEventListener('click', async function() {
            this.querySelector('i').classList.add('fa-spin');
            await loadAllMessages();
            this.querySelector('i').classList.remove('fa-spin');
        });
    }
    
    // Close conversation button
    if (closeConversationBtn) {
        closeConversationBtn.addEventListener('click', function() {
            if (conversationView) conversationView.classList.add('hidden');
            if (conversationEmpty) conversationEmpty.style.display = 'flex';
            currentConversationEmail = null;
            
            // Remove active class from all conversation items
            document.querySelectorAll('.conversation-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // On mobile, show the sidebar again
            if (window.innerWidth <= 768) {
                const sidebar = document.querySelector('.whatsapp-sidebar');
                if (sidebar) {
                    sidebar.classList.remove('hide-mobile');
                }
            }
        });
    }
    
    // Search conversations
    if (messagesSearchInput) {
        messagesSearchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            if (searchTerm === '') {
                displayConversations(allConversations);
            } else {
                const filtered = allConversations.filter(conv => {
                    return conv.name.toLowerCase().includes(searchTerm) ||
                           conv.email.toLowerCase().includes(searchTerm) ||
                           conv.messages.some(msg => msg.message.toLowerCase().includes(searchTerm));
                });
                displayConversations(filtered);
            }
        });
    }
    
    // Format time ago
    function formatTimeAgo(timestamp) {
        if (!timestamp) return 'Unknown';
        
        const date = new Date(timestamp);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);
        
        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
        
        return date.toLocaleDateString();
    }
    
    // Format message time
    function formatMessageTime(timestamp) {
        if (!timestamp) return '';
        
        const date = new Date(timestamp);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    // Escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ============================================
    // EMOJI PICKER
    // ============================================
    
    const emojiPickerBtn = document.getElementById('emojiPickerBtn');
    const emojiPicker = document.getElementById('emojiPicker');
    const emojiPickerContent = document.getElementById('emojiPickerContent');
    const emojiSearch = document.getElementById('emojiSearch');
    const replyMessageInput = document.getElementById('replyMessage');
    
    // Comprehensive emoji collection by category
    const emojis = {
        smileys: ['😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃', '😉', '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '😚', '😙', '😋', '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '🤫', '🤔', '🤐', '🤨', '😐', '😑', '😶', '😏', '😒', '🙄', '😬', '🤥', '😌', '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕', '🤢', '🤮', '🤧', '🥵', '🥶', '😶‍🌫️', '😵', '😵‍💫', '🤯', '🤠', '🥳', '😎', '🤓', '🧐', '😕', '😟', '🙁', '☹️', '😮', '😯', '😲', '😳', '🥺', '😦', '😧', '😨', '😰', '😥', '😢', '😭', '😱', '😖', '😣', '😞', '😓', '😩', '😫', '🥱'],
        gestures: ['👋', '🤚', '🖐️', '✋', '🖖', '👌', '🤏', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉', '👆', '🖕', '👇', '☝️', '👍', '👎', '✊', '👊', '🤛', '🤜', '👏', '🙌', '👐', '🤲', '🤝', '🙏', '✍️', '💪', '🦾', '🦿', '🦵', '🦶', '👂', '🦻', '👃', '🧠', '🦷', '🦴', '👀', '👁️', '👅', '👄', '💋', '🩸'],
        animals: ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐷', '🐸', '🐵', '🐔', '🐧', '🐦', '🐤', '🦆', '🦅', '🦉', '🦇', '🐺', '🐗', '🐴', '🦄', '🐝', '🐛', '🦋', '🐌', '🐞', '🐜', '🦟', '🦗', '🕷️', '🦂', '🐢', '🐍', '🦎', '🦖', '🦕', '🐙', '🦑', '🦐', '🦞', '🦀', '🐡', '🐠', '🐟', '🐬', '🐳', '🐋', '🦈', '🐊', '🐅', '🐆', '🦓', '🦍', '🦧', '🐘', '🦛', '🦏', '🐪', '🐫', '🦒', '🦘', '🐃', '🐄', '🐎', '🐖', '🐏', '🐑', '🦙', '🐐', '🦌', '🐕', '🐩', '🦮', '🐕‍🦺', '🐈', '🐓', '🦃', '🦚', '🦜', '🦢', '🦩', '🕊️', '🐇', '🦝', '🦨', '🦡', '🦦', '🦥', '🐁', '🐀', '🐿️', '🦔'],
        food: ['🍕', '🍔', '🍟', '🌭', '🍿', '🧈', '🥓', '🥚', '🍳', '🧇', '🥞', '🧈', '🍞', '🥐', '🥨', '🥯', '🥖', '🧀', '🥗', '🥙', '🥪', '🌮', '🌯', '🥫', '🍝', '🍜', '🍲', '🍛', '🍣', '🍱', '🥟', '🦪', '🍤', '🍙', '🍚', '🍘', '🍥', '🥠', '🥮', '🍢', '🍡', '🍧', '🍨', '🍦', '🥧', '🧁', '🍰', '🎂', '🍮', '🍭', '🍬', '🍫', '🍿', '🍩', '🍪', '🌰', '🥜', '🍯', '🥛', '🍼', '☕', '🍵', '🧃', '🥤', '🍶', '🍺', '🍻', '🥂', '🍷', '🥃', '🍸', '🍹', '🧉', '🍾', '🧊', '🥄', '🍴', '🍽️', '🥢', '🥡'],
        travel: ['✈️', '🛫', '🛬', '🪂', '💺', '🚁', '🚟', '🚠', '🚡', '🛰️', '🚀', '🛸', '🚉', '🚊', '🚝', '🚞', '🚋', '🚌', '🚍', '🚎', '🚐', '🚑', '🚒', '🚓', '🚔', '🚕', '🚖', '🚗', '🚘', '🚙', '🛻', '🚚', '🚛', '🚜', '🏎️', '🏍️', '🛵', '🦽', '🦼', '🛴', '🚲', '🛹', '🛼', '🚏', '🛣️', '🛤️', '🛢️', '⛽', '🚨', '🚥', '🚦', '🛑', '🚧', '⚓', '⛵', '🛶', '🚤', '🛳️', '⛴️', '🛥️', '🚢', '🗿', '🗽', '🗼', '🏰', '🏯', '🏟️', '🎡', '🎢', '🎠', '⛲', '⛱️', '🏖️', '🏝️', '🏜️', '🌋', '⛰️', '🏔️', '🗻', '🏕️', '⛺', '🏠', '🏡', '🏘️', '🏚️', '🏗️', '🏭', '🏢', '🏬', '🏣', '🏤', '🏥', '🏦', '🏨', '🏪', '🏫', '🏩', '💒', '🏛️', '⛪', '🕌', '🕍', '🛕'],
        activities: ['⚽', '🏀', '🏈', '⚾', '🥎', '🎾', '🏐', '🏉', '🥏', '🎱', '🪀', '🏓', '🏸', '🏒', '🏑', '🥍', '🏏', '🥅', '⛳', '🪁', '🏹', '🎣', '🤿', '🥊', '🥋', '🎽', '🛹', '🛷', '⛸️', '🥌', '🎿', '⛷️', '🏂', '🪂', '🏋️', '🤸', '🤺', '🤾', '🏌️', '🏇', '🧘', '🏊', '🤽', '🚣', '🧗', '🚵', '🚴', '🏆', '🥇', '🥈', '🥉', '🏅', '🎖️', '🏵️', '🎗️', '🎫', '🎟️', '🎪', '🤹', '🎭', '🩰', '🎨', '🎬', '🎤', '🎧', '🎼', '🎹', '🥁', '🎷', '🎺', '🎸', '🪕', '🎻', '🎲', '♟️', '🎯', '🎳', '🎮', '🎰', '🧩'],
        objects: ['💡', '🔦', '🏮', '🪔', '📱', '💻', '⌨️', '🖥️', '🖨️', '🖱️', '🖲️', '💾', '📀', '🧮', '🎥', '📹', '📷', '📸', '📼', '🔍', '🔎', '🕯️', '💡', '🔦', '🏮', '🪔', '📔', '📕', '📖', '📗', '📘', '📙', '📚', '📓', '📒', '📃', '📜', '📄', '📰', '🗞️', '📑', '🔖', '🏷️', '💰', '💴', '💵', '💶', '💷', '💸', '💳', '🧾', '✉️', '📧', '📨', '📩', '📤', '📥', '📦', '📫', '📪', '📬', '📭', '📮', '🗳️', '✏️', '✒️', '🖊️', '🖋️', '🖌️', '🖍️', '📝', '💼', '📁', '📂', '🗂️', '📅', '📆', '🗒️', '🗓️', '📇', '📈', '📉', '📊', '📋', '📌', '📍', '📎', '🖇️', '📏', '📐', '✂️', '🗃️', '🗄️', '🗑️'],
        symbols: ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '☮️', '✝️', '☪️', '🕉️', '☸️', '✡️', '🔯', '🕎', '☯️', '☦️', '🛐', '⛎', '♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓', '🆔', '⚛️', '🉑', '☢️', '☣️', '📴', '📳', '🈶', '🈚', '🈸', '🈺', '🈷️', '✴️', '🆚', '💮', '🉐', '㊙️', '㊗️', '🈴', '🈵', '🈹', '🈲', '🅰️', '🅱️', '🆎', '🆑', '🅾️', '🆘', '❌', '⭕', '🛑', '⛔', '📛', '🚫', '💯', '💢', '♨️', '🚷', '🚯', '🚳', '🚱', '🔞', '📵', '🚭', '❗', '❕', '❓', '❔', '‼️', '⁉️', '🔅', '🔆', '〽️', '⚠️', '🚸', '🔱', '⚜️', '🔰', '♻️', '✅', '🈯', '💹', '❇️', '✳️', '❎', '🌐', '💠', '➿', '🌀', '♠️', '♣️', '♥️', '♦️', '🃏', '🎴', '🀄', '🔇', '🔈', '🔉', '🔊', '🔔', '🔕', '🎵', '🎶', '🏧', '🚮', '🚰', '♿', '🚹', '🚺', '🚻', '🚼', '⏩', '⏭️', '⏯️', '⏸️', '⏹️', '⏺️', '⏏️', '🔀', '🔁', '🔂', '▶️', '◀️', '🔼', '🔽', '⏫', '⏬', '➡️', '⬅️', '⬆️', '⬇️', '↗️', '↘️', '↙️', '↖️', '↕️', '↔️', '🔄', '↪️', '↩️', '⤴️', '⤵️', '🔃', '#️⃣', '*️⃣', '0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '🔠', '🔡', '🔢', '🔣', '🔤', '🅰️', '🆎', '🅱️', '🆑', '🆒', '🆓', 'ℹ️', '🆔', 'Ⓜ️', '🆕', '🆖', '🅾️', '🆗', '🅿️', '🆘', '🆙', '🆚', '🈁', '🈂️', '🈷️', '🈶', '🈯', '🉐', '🈹', '🈚', '🈲', '🉑', '🈸', '🈴', '🈳', '㊗️', '㊙️', '🈺', '🈵']
    };
    
    // Initialize emoji picker
    function initializeEmojiPicker() {
        if (!emojiPickerContent) return;
        
        // Load default category (smileys)
        loadEmojiCategory('smileys');
        
        // Add category button listeners
        document.querySelectorAll('.emoji-category').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.emoji-category').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                const category = this.getAttribute('data-category');
                loadEmojiCategory(category);
            });
        });
        
        // Emoji search
        if (emojiSearch) {
            emojiSearch.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                if (searchTerm === '') {
                    const activeCategory = document.querySelector('.emoji-category.active')?.getAttribute('data-category') || 'smileys';
                    loadEmojiCategory(activeCategory);
                } else {
                    searchEmojis(searchTerm);
                }
            });
        }
    }
    
    // Load emoji category
    function loadEmojiCategory(category) {
        if (!emojiPickerContent || !emojis[category]) return;
        
        let html = '';
        emojis[category].forEach(emoji => {
            html += `<div class="emoji-item" data-emoji="${emoji}">${emoji}</div>`;
        });
        
        emojiPickerContent.innerHTML = html;
        
        // Add click listeners to emoji items
        document.querySelectorAll('.emoji-item').forEach(item => {
            item.addEventListener('click', function() {
                insertEmoji(this.getAttribute('data-emoji'));
            });
        });
    }
    
    // Emoji keyword map for search
    const emojiKeywords = {
        '😀':'grinning happy smile','😃':'happy smile big eyes','😄':'happy smile laugh','😁':'grin beam happy','😆':'laugh squint lol','😅':'sweat smile nervous','🤣':'rolling laughing floor lol','😂':'joy tears laughing cry','🙂':'slightly smile','🙃':'upside down smile','😉':'wink','😊':'blush smile happy','😇':'halo innocent angel','🥰':'hearts love adore','😍':'heart eyes love','🤩':'star eyes excited','😘':'kiss blow love','😗':'kiss','😚':'kiss closed eyes','😙':'kiss smile','😋':'yum tongue delicious','😛':'tongue playful','😜':'wink tongue crazy','🤪':'crazy zany','😝':'tongue squint','🤑':'money rich dollar','🤗':'hugs embrace','🤭':'hand mouth oops','🤫':'shush quiet secret','🤔':'thinking hmm','🤐':'zipper mouth quiet','🤨':'raised eyebrow suspicious','😐':'neutral expressionless','😑':'expressionless blank','😶':'no mouth silent','😏':'smirk','😒':'unamused annoyed','🙄':'eye roll','😬':'grimace nervous','🤥':'lying pinocchio','😌':'relieved calm','😔':'pensive sad','😪':'sleepy tired','🤤':'drool hungry','😴':'sleeping zzz tired','😷':'mask sick ill','🤒':'sick thermometer ill','🤕':'injured hurt head','🤢':'nauseous sick green','🤮':'vomit sick','🤧':'sneeze sick','🥵':'hot fever','🥶':'cold freeze','😵':'dizzy dead','🤯':'exploding mind blown','🤠':'cowboy hat','🥳':'party celebrate','😎':'sunglasses cool','🤓':'nerd glasses','🧐':'monocle curious','😕':'confused','😟':'worried sad','🙁':'sad frown','☹️':'sad frown','😮':'surprised open mouth','😯':'hushed surprised','😲':'astonished shocked','😳':'flushed embarrassed','🥺':'pleading puppy eyes','😦':'frowning open mouth','😧':'anguished','😨':'fearful scared','😰':'anxious sweat scared','😥':'sad disappointed','😢':'cry tear sad','😭':'crying loud sob','😱':'scream fear','😖':'confounded','😣':'persevere struggle','😞':'disappointed sad','😓':'downcast sweat','😩':'weary tired','😫':'tired exhausted','🥱':'yawn bored tired',
        '👋':'wave hello hi','🤚':'raised back hand','🖐️':'hand stop five','✋':'hand raised stop','🖖':'vulcan spock','👌':'ok perfect','🤏':'pinch small','✌️':'peace victory','🤞':'fingers crossed luck','🤟':'love you sign','🤘':'rock metal','🤙':'call shaka hang loose','👈':'point left','👉':'point right','👆':'point up','👇':'point down','☝️':'index point up','👍':'thumbs up like good','👎':'thumbs down dislike bad','✊':'fist raised','👊':'punch fist','🤛':'left fist bump','🤜':'right fist bump','👏':'clap applause','🙌':'raising hands celebrate','👐':'open hands','🤲':'palms together','🤝':'handshake agreement','🙏':'pray please thank you folded','✍️':'writing pen','💪':'muscle strong flex','🧠':'brain mind smart',
        '🐶':'dog puppy pet','🐱':'cat kitten pet','🐭':'mouse','🐹':'hamster','🐰':'rabbit bunny','🦊':'fox','🐻':'bear','🐼':'panda','🐨':'koala','🐯':'tiger','🦁':'lion','🐮':'cow','🐷':'pig','🐸':'frog','🐵':'monkey','🐔':'chicken','🐧':'penguin','🐦':'bird','🦆':'duck','🦅':'eagle','🦉':'owl','🐺':'wolf','🐴':'horse','🦄':'unicorn','🐝':'bee','🦋':'butterfly','🐌':'snail','🐞':'ladybug','🐜':'ant','🐢':'turtle','🐍':'snake','🦎':'lizard','🐙':'octopus','🦑':'squid','🦀':'crab','🐡':'fish','🐬':'dolphin','🐳':'whale','🦈':'shark','🐊':'crocodile','🐅':'tiger','🐘':'elephant','🦒':'giraffe','🐕':'dog','🐈':'cat',
        '🍕':'pizza','🍔':'burger hamburger','🍟':'fries french','🌭':'hotdog sausage','🍿':'popcorn movie','🥚':'egg','🍳':'frying pan egg cook','🥞':'pancake breakfast','🍞':'bread','🥐':'croissant','🧀':'cheese','🥗':'salad','🌮':'taco','🌯':'burrito wrap','🍝':'spaghetti pasta','🍜':'noodles ramen','🍣':'sushi','🍱':'bento box','🍤':'fried shrimp','🍦':'ice cream soft serve','🍰':'cake slice','🎂':'birthday cake','🍭':'lolly candy','🍬':'candy sweet','🍫':'chocolate','🍩':'donut','🍪':'cookie','🍯':'honey','🥛':'milk','☕':'coffee hot drink','🍵':'tea hot','🍺':'beer mug','🍻':'beer cheers toast','🥂':'champagne toast','🍷':'wine red','🍸':'cocktail martini','🍹':'tropical drink',
        '✈️':'plane airplane flight travel','🚀':'rocket space launch','🚁':'helicopter','🚉':'train station','🚌':'bus','🚗':'car red automobile','🚕':'taxi cab','🚒':'fire truck','🚓':'police car','🚑':'ambulance','🚲':'bicycle bike','🛴':'scooter','⛵':'sailboat','🚢':'ship boat','🏖️':'beach sunny','🏝️':'island tropical','🏔️':'mountain snow','⛺':'tent camping','🏠':'house home','🏢':'office building','🌋':'volcano','🗼':'tokyo tower','🗽':'liberty statue',
        '⚽':'soccer football','🏀':'basketball','🏈':'football american','⚾':'baseball','🎾':'tennis','🏐':'volleyball','🏊':'swimming swim','🚴':'cycling bike','🏋️':'weightlifting gym','🤸':'gymnastics cartwheel','🏆':'trophy win champion','🥇':'gold medal first','🥈':'silver medal second','🥉':'bronze medal third','🎯':'target bullseye','🎮':'video game controller','🎲':'dice game','🎨':'art palette','🎤':'microphone sing','🎧':'headphones music','🎸':'guitar music','🎺':'trumpet music','🎻':'violin music','🥁':'drums music','🎹':'piano keyboard','🎭':'theatre drama','🎪':'circus tent',
        '💡':'light bulb idea','🔦':'torch flashlight','📱':'mobile phone','💻':'laptop computer','⌨️':'keyboard','🖥️':'desktop computer','🖨️':'printer','🖱️':'mouse computer','💾':'floppy disk save','📷':'camera photo','📸':'camera flash photo','🔍':'magnifying glass search','🔎':'magnifying glass','📚':'books library','📖':'open book reading','📝':'memo note write','✏️':'pencil write','✒️':'pen write','💼':'briefcase work business','📁':'folder files','📈':'chart up growth','📉':'chart down','📊':'bar chart','📌':'pushpin location','📎':'paperclip','✂️':'scissors cut','🗑️':'trash bin delete',
        '❤️':'heart love red','🧡':'orange heart','💛':'yellow heart','💚':'green heart','💙':'blue heart','💜':'purple heart','🖤':'black heart','🤍':'white heart','🤎':'brown heart','💔':'broken heart','💕':'two hearts love','💞':'revolving hearts','💓':'beating heart','💗':'growing heart','💖':'sparkling heart','💘':'heart arrow cupid','💝':'heart ribbon','☮️':'peace','✅':'check mark done','❌':'cross wrong no','⚠️':'warning caution','♻️':'recycle','💯':'100 perfect score','🔥':'fire hot flame','⭐':'star','🌟':'glowing star','✨':'sparkle','🎉':'party celebrate confetti','🎊':'confetti ball party','🎈':'balloon party','🏳️':'white flag','🏴':'black flag','❗':'exclamation alert','❓':'question mark','💤':'zzz sleep','💥':'boom explosion','💫':'dizzy star','💦':'sweat drops water','💨':'wind air','🕐':'clock time one','🔔':'bell notification alert','🔕':'no bell muted'
    };

    // Search emojis
    function searchEmojis(searchTerm) {
        const term = searchTerm.toLowerCase().trim();
        const allEmojis = Object.values(emojis).flat();
        const results = allEmojis.filter(emoji => {
            const keywords = emojiKeywords[emoji] || '';
            return keywords.includes(term);
        });
        
        let html = '';
        results.forEach(emoji => {
            html += `<div class="emoji-item" data-emoji="${emoji}">${emoji}</div>`;
        });
        
        if (html === '') {
            html = '<div style="grid-column: 1/-1; text-align: center; padding: 20px; color: #667781;">No emojis found</div>';
        }
        
        emojiPickerContent.innerHTML = html;
        
        // Add click listeners to emoji items
        document.querySelectorAll('.emoji-item').forEach(item => {
            item.addEventListener('click', function() {
                insertEmoji(this.getAttribute('data-emoji'));
            });
        });
    }
    
    // Insert emoji at cursor position
    function insertEmoji(emoji) {
        if (!replyMessageInput) return;
        
        const start = replyMessageInput.selectionStart;
        const end = replyMessageInput.selectionEnd;
        const text = replyMessageInput.value;
        
        replyMessageInput.value = text.substring(0, start) + emoji + text.substring(end);
        replyMessageInput.selectionStart = replyMessageInput.selectionEnd = start + emoji.length;
        replyMessageInput.focus();
        
        // Close emoji picker
        if (emojiPicker) {
            emojiPicker.classList.add('hidden');
        }
    }
    
    // Toggle emoji picker
    if (emojiPickerBtn) {
        emojiPickerBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            if (emojiPicker) {
                emojiPicker.classList.toggle('hidden');
            }
        });
    }
    
    // Close emoji picker when clicking outside
    document.addEventListener('click', function(e) {
        if (emojiPicker && !emojiPicker.contains(e.target) && e.target !== emojiPickerBtn) {
            emojiPicker.classList.add('hidden');
        }
    });
    
    // Initialize emoji picker on page load
    initializeEmojiPicker();
    
    // Auto-resize textarea
    if (replyMessageInput) {
        replyMessageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 100) + 'px';
        });
        
        // Reset on form submit
        if (replyForm) {
            replyForm.addEventListener('submit', function() {
                setTimeout(() => {
                    if (replyMessageInput) {
                        replyMessageInput.style.height = 'auto';
                    }
                }, 100);
            });
        }
    }
    
    // Mobile: hide sidebar when conversation is opened
    const originalLoadConversation = loadConversation;
    loadConversation = async function(email) {
        // On mobile, hide the sidebar when opening a conversation
        if (window.innerWidth <= 768) {
            const sidebar = document.querySelector('.whatsapp-sidebar');
            if (sidebar) {
                sidebar.classList.add('hide-mobile');
            }
        }
        // Call the original function
        return await originalLoadConversation(email);
    };

    // ============================================
    // ANALYTICS
    // ============================================
    
    // Analytics chart instances
    let diseaseDistributionChart = null;
    let diseaseComparisonChart = null;
    
    // Load analytics data
    window.loadAnalyticsData = async function() {
        const analyticsSection = document.getElementById('analyticsSection');
        const loadingOverlay = document.getElementById('analyticsLoadingOverlay');
        const errorState = document.getElementById('analyticsErrorState');
        
        try {
            // Show loading
            if (loadingOverlay) loadingOverlay.style.display = 'flex';
            if (errorState) errorState.style.display = 'none';
            
            // Get selected time period
            const timePeriod = document.getElementById('analyticsTimePeriod')?.value || '30';
            
            const response = await fetch(`/api/admin/analytics?period=${timePeriod}`);
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'Failed to load analytics');
            }
            
            const data = result.data;
            
            // Update statistics cards
            document.getElementById('analyticsTotalDiseases').textContent = data.total_detections || 0;
            document.getElementById('analyticsHealthyPlants').textContent = data.healthy_plants || 0;
            
            // Format disease names for display
            const formatDiseaseName = (name) => {
                if (!name || name === '-') return '-';
                // Convert "Chilli__Anthacnose" to "Anthacnose"
                return name.replace(/^Chilli[_\s]+/i, '').replace(/_/g, ' ');
            };
            
            document.getElementById('analyticsMostCommonDisease').textContent = 
                formatDiseaseName(data.most_common.disease);
            document.getElementById('analyticsMostCommonCount').textContent = 
                `${data.most_common.count} cases`;
            
            document.getElementById('analyticsLeastCommonDisease').textContent = 
                formatDiseaseName(data.least_common.disease);
            document.getElementById('analyticsLeastCommonCount').textContent = 
                `${data.least_common.count} cases`;
            
            // Update charts
            updateAnalyticsCharts(data.disease_distribution);
            
            // Update predictions table
            updateAnalyticsPredictionsTable(data.recent_predictions);
            
            // Hide loading
            if (loadingOverlay) loadingOverlay.style.display = 'none';
            
        } catch (error) {
            console.error('Error loading analytics:', error);
            
            // Hide loading
            if (loadingOverlay) loadingOverlay.style.display = 'none';
            
            // Show error
            if (errorState) {
                errorState.style.display = 'flex';
                const errorMessage = document.getElementById('analyticsErrorMessage');
                if (errorMessage) {
                    errorMessage.textContent = error.message || 'An error occurred while fetching analytics data.';
                }
            }
        }
    };
    
    // Update analytics charts
    function updateAnalyticsCharts(diseaseData) {
        const noDataMessage = document.getElementById('noDataMessage');
        const distributionCanvas = document.getElementById('diseaseDistributionChart');
        const comparisonCanvas = document.getElementById('diseaseComparisonChart');
        
        if (!diseaseData || diseaseData.length === 0) {
            // No data - show empty state
            if (noDataMessage) noDataMessage.style.display = 'flex';
            if (distributionCanvas) distributionCanvas.style.display = 'none';
            if (comparisonCanvas) comparisonCanvas.style.display = 'none';
            return;
        }
        
        // Hide empty state, show charts
        if (noDataMessage) noDataMessage.style.display = 'none';
        if (distributionCanvas) distributionCanvas.style.display = 'block';
        if (comparisonCanvas) comparisonCanvas.style.display = 'block';
        
        // Prepare chart data
        const labels = diseaseData.map(d => {
            const name = d.disease.replace(/^Chilli[_\s]+/i, '').replace(/_/g, ' ');
            return name;
        });
        const counts = diseaseData.map(d => d.count);
        
        // Color palette
        const colors = [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 206, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)'
        ];
        
        // Destroy existing charts
        if (diseaseDistributionChart) {
            diseaseDistributionChart.destroy();
        }
        if (diseaseComparisonChart) {
            diseaseComparisonChart.destroy();
        }
        
        // Create pie chart
        if (distributionCanvas) {
            const ctx = distributionCanvas.getContext('2d');
            diseaseDistributionChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: counts,
                        backgroundColor: colors,
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 15,
                                font: {
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // Create bar chart
        if (comparisonCanvas) {
            const ctx = comparisonCanvas.getContext('2d');
            diseaseComparisonChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Detection Count',
                        data: counts,
                        backgroundColor: colors,
                        borderWidth: 0,
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `Detections: ${context.parsed.y}`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Update predictions table
    function updateAnalyticsPredictionsTable(predictions) {
        const tableBody = document.getElementById('analyticsPredictionsTableBody');
        const emptyState = document.getElementById('analyticsEmptyState');
        
        if (!predictions || predictions.length === 0) {
            if (tableBody) {
                tableBody.innerHTML = '<tr><td colspan="4" class="analytics-table-empty">No predictions available</td></tr>';
            }
            return;
        }
        
        // Hide empty state
        if (emptyState) emptyState.style.display = 'none';
        
        // Build table rows
        let html = '';
        predictions.forEach(pred => {
            const diseaseName = pred.disease.replace(/^Chilli[_\s]+/i, '').replace(/_/g, ' ');
            // Handle confidence - if already > 1, it's a percentage; if <= 1, multiply by 100
            const confValue = pred.confidence > 1 ? pred.confidence : pred.confidence * 100;
            const confidence = confValue.toFixed(1) + '%';
            const date = pred.timestamp ? new Date(pred.timestamp).toLocaleDateString() : 'N/A';
            const location = pred.location || 'Unknown';
            
            // Color code based on disease type
            let diseaseClass = 'disease-tag';
            if (pred.disease.toLowerCase().includes('healthy')) {
                diseaseClass += ' disease-healthy';
            } else {
                diseaseClass += ' disease-sick';
            }
            
            html += `
                <tr>
                    <td><span class="${diseaseClass}">${diseaseName}</span></td>
                    <td>${confidence}</td>
                    <td>${location}</td>
                    <td>${date}</td>
                </tr>
            `;
        });
        
        if (tableBody) {
            tableBody.innerHTML = html;
        }
    }
    
    // Analytics time period change handler
    const analyticsTimePeriod = document.getElementById('analyticsTimePeriod');
    if (analyticsTimePeriod) {
        analyticsTimePeriod.addEventListener('change', function() {
            loadAnalyticsData();
        });
    }
    
    // Refresh analytics button
    const refreshAnalyticsBtn = document.getElementById('refreshAnalyticsBtn');
    if (refreshAnalyticsBtn) {
        refreshAnalyticsBtn.addEventListener('click', function() {
            this.querySelector('i').classList.add('fa-spin');
            loadAnalyticsData().finally(() => {
                this.querySelector('i').classList.remove('fa-spin');
            });
        });
    }

    // ============================================
    // DISTRICT MAPPING
    // ============================================
    
    // Map instance
    let predictionMap = null;
    let markerCluster = null;
    let currentMappingData = null;
    
    // Load mapping data
    window.loadMappingData = async function() {
        const mappingSection = document.getElementById('mappingSection');
        const loadingOverlay = document.getElementById('mappingLoadingOverlay');
        const errorState = document.getElementById('mappingErrorState');
        
        try {
            // Show loading
            if (loadingOverlay) loadingOverlay.style.display = 'flex';
            if (errorState) errorState.style.display = 'none';
            
            // Get filter values
            const countryFilter = document.getElementById('countryFilter')?.value || '';
            const regionFilter = document.getElementById('regionFilter')?.value || '';
            const cityFilter = document.getElementById('cityFilter')?.value || '';
            
            // Build query params
            const params = new URLSearchParams();
            if (countryFilter) params.append('country', countryFilter);
            if (regionFilter) params.append('region', regionFilter);
            if (cityFilter) params.append('city', cityFilter);
            
            const response = await fetch(`/api/admin/mapping?${params.toString()}`);
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'Failed to load mapping data');
            }
            
            const data = result.data;
            currentMappingData = data;
            
            // Update statistics
            document.getElementById('mappingTotalLocations').textContent = data.total_locations || 0;
            document.getElementById('mappingTotalPredictions').textContent = data.total_predictions || 0;
            document.getElementById('mappingCountriesCount').textContent = data.filters.countries.length || 0;
            document.getElementById('mappingCitiesCount').textContent = data.filters.cities.length || 0;
            
            // Update filters if they're empty (first load)
            updateMapFilters(data.filters);
            
            // Update map
            updateMap(data.locations);
            
            // Update table
            updateMappingTable(data.locations);
            
            // Hide loading
            if (loadingOverlay) loadingOverlay.style.display = 'none';
            
        } catch (error) {
            console.error('Error loading mapping data:', error);
            
            // Hide loading
            if (loadingOverlay) loadingOverlay.style.display = 'none';
            
            // Show error
            if (errorState) {
                errorState.style.display = 'flex';
                const errorMessage = document.getElementById('mappingErrorMessage');
                if (errorMessage) {
                    errorMessage.textContent = error.message || 'An error occurred while fetching location data.';
                }
            }
        }
    };
    
    // Update filter dropdowns
    function updateMapFilters(filters) {
        const countryFilter = document.getElementById('countryFilter');
        const regionFilter = document.getElementById('regionFilter');
        const cityFilter = document.getElementById('cityFilter');
        
        // Save current values
        const currentCountry = countryFilter?.value || '';
        const currentRegion = regionFilter?.value || '';
        const currentCity = cityFilter?.value || '';
        
        // Update countries
        if (countryFilter && filters.countries) {
            const countriesHTML = '<option value="">All Countries</option>' +
                filters.countries.map(c => `<option value="${c}" ${c === currentCountry ? 'selected' : ''}>${c}</option>`).join('');
            countryFilter.innerHTML = countriesHTML;
        }
        
        // Update regions
        if (regionFilter && filters.regions) {
            const regionsHTML = '<option value="">All Regions</option>' +
                filters.regions.map(r => `<option value="${r}" ${r === currentRegion ? 'selected' : ''}>${r}</option>`).join('');
            regionFilter.innerHTML = regionsHTML;
        }
        
        // Update cities
        if (cityFilter && filters.cities) {
            const citiesHTML = '<option value="">All Cities</option>' +
                filters.cities.map(c => `<option value="${c}" ${c === currentCity ? 'selected' : ''}>${c}</option>`).join('');
            cityFilter.innerHTML = citiesHTML;
        }
    }
    
    // Initialize map
    function initializeMap() {
        if (predictionMap) return; // Already initialized
        
        const mapElement = document.getElementById('predictionMap');
        if (!mapElement) return;
        
        // Create map centered on world view with scroll handling
        predictionMap = L.map('predictionMap', {
            scrollWheelZoom: false,  // Disable scroll wheel zoom by default
            tap: false,  // Disable tap for mobile
            touchZoom: true,  // Keep touch zoom enabled
            dragging: true,  // Keep dragging enabled
            zoomControl: true,  // Keep zoom controls
            doubleClickZoom: true,  // Keep double click zoom
            boxZoom: true  // Keep box zoom
        }).setView([20, 0], 2);
        
        // Enable scroll zoom only when map is focused
        predictionMap.on('focus', function() {
            predictionMap.scrollWheelZoom.enable();
        });
        
        predictionMap.on('blur', function() {
            predictionMap.scrollWheelZoom.disable();
        });
        
        // Enable scroll zoom when clicking on the map
        predictionMap.on('click', function() {
            predictionMap.scrollWheelZoom.enable();
        });
        
        // Disable scroll zoom when mouse leaves map
        mapElement.addEventListener('mouseleave', function() {
            if (predictionMap) {
                predictionMap.scrollWheelZoom.disable();
            }
        });
        
        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 18,
            minZoom: 2
        }).addTo(predictionMap);
        
        // Initialize marker cluster group
        markerCluster = L.markerClusterGroup({
            maxClusterRadius: 50,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false,
            zoomToBoundsOnClick: true
        });
        
        predictionMap.addLayer(markerCluster);
        
        // Add scroll hint message
        const scrollHint = L.control({position: 'topright'});
        scrollHint.onAdd = function() {
            const div = L.DomUtil.create('div', 'map-scroll-hint');
            div.innerHTML = '<small style="background: rgba(255,255,255,0.9); padding: 5px 10px; border-radius: 4px; font-size: 11px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">Click map to enable scroll zoom</small>';
            div.style.display = 'none';
            return div;
        };
        scrollHint.addTo(predictionMap);
        
        // Show hint when hovering over map
        mapElement.addEventListener('mouseenter', function() {
            const hint = document.querySelector('.map-scroll-hint');
            if (hint && !predictionMap.scrollWheelZoom.enabled()) {
                hint.style.display = 'block';
                setTimeout(() => {
                    hint.style.display = 'none';
                }, 2000);
            }
        });
    }
    
    // Update map with locations
    function updateMap(locations) {
        if (!predictionMap) {
            initializeMap();
        }
        
        if (!predictionMap || !markerCluster) return;
        
        // Clear existing markers
        markerCluster.clearLayers();
        
        if (!locations || locations.length === 0) {
            return;
        }
        
        // Add markers for each location
        locations.forEach(loc => {
            if (!loc.latitude || !loc.longitude) return;
            
            // Create custom icon with color based on prediction count
            const count = loc.count;
            let iconColor = '#4facfe';
            if (count > 20) iconColor = '#f5576c';
            else if (count > 10) iconColor = '#fa709a';
            else if (count > 5) iconColor = '#fbbf24';
            
            // Create marker
            const marker = L.marker([loc.latitude, loc.longitude], {
                icon: L.divIcon({
                    className: 'custom-map-marker',
                    html: `<div style="background: ${iconColor}; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 12px;">${count}</div>`,
                    iconSize: [30, 30],
                    iconAnchor: [15, 15]
                })
            });
            
            // Create popup content
            const topDisease = Object.entries(loc.diseases).sort((a, b) => b[1] - a[1])[0];
            const diseaseList = Object.entries(loc.diseases)
                .sort((a, b) => b[1] - a[1])
                .map(([disease, count]) => {
                    const name = disease.replace(/^Chilli[_\s]+/i, '').replace(/_/g, ' ');
                    return `<li>${name}: ${count}</li>`;
                })
                .join('');
            
            const popupContent = `
                <div class="map-popup">
                    <h4><i class="fas fa-map-marker-alt"></i> ${loc.city}</h4>
                    <p class="popup-location">${loc.region}, ${loc.country}</p>
                    <div class="popup-stats">
                        <div class="popup-stat">
                            <span class="popup-label">Total Predictions:</span>
                            <span class="popup-value">${loc.count}</span>
                        </div>
                    </div>
                    <div class="popup-diseases">
                        <strong>Diseases Detected:</strong>
                        <ul>${diseaseList}</ul>
                    </div>
                </div>
            `;
            
            marker.bindPopup(popupContent, {
                maxWidth: 300,
                className: 'custom-popup'
            });
            
            markerCluster.addLayer(marker);
        });
        
        // Fit map to markers if any exist
        if (locations.length > 0) {
            const bounds = markerCluster.getBounds();
            if (bounds.isValid()) {
                predictionMap.fitBounds(bounds, {
                    padding: [50, 50],
                    maxZoom: 10
                });
            }
        }
    }
    
    // Update mapping table
    function updateMappingTable(locations) {
        const tableBody = document.getElementById('mappingTableBody');
        const emptyState = document.getElementById('mappingEmptyState');
        
        if (!locations || locations.length === 0) {
            if (tableBody) {
                tableBody.innerHTML = '<tr><td colspan="5" class="mapping-table-empty">No location data available</td></tr>';
            }
            if (emptyState) emptyState.style.display = 'flex';
            return;
        }
        
        // Hide empty state
        if (emptyState) emptyState.style.display = 'none';
        
        // Sort by prediction count
        locations.sort((a, b) => b.count - a.count);
        
        // Build table rows
        let html = '';
        locations.forEach(loc => {
            // Find top disease
            const topDisease = Object.entries(loc.diseases).sort((a, b) => b[1] - a[1])[0];
            const diseaseName = topDisease ? topDisease[0].replace(/^Chilli[_\s]+/i, '').replace(/_/g, ' ') : 'N/A';
            const diseaseCount = topDisease ? topDisease[1] : 0;
            
            html += `
                <tr>
                    <td>${loc.city}</td>
                    <td>${loc.region}</td>
                    <td>${loc.country}</td>
                    <td><span class="prediction-count-badge">${loc.count}</span></td>
                    <td>${diseaseName} (${diseaseCount})</td>
                </tr>
            `;
        });
        
        if (tableBody) {
            tableBody.innerHTML = html;
        }
    }
    
    // Filter change handlers
    const countryFilter = document.getElementById('countryFilter');
    const regionFilter = document.getElementById('regionFilter');
    const cityFilter = document.getElementById('cityFilter');
    const resetFiltersBtn = document.getElementById('resetFiltersBtn');
    const refreshMappingBtn = document.getElementById('refreshMappingBtn');
    
    if (countryFilter) {
        countryFilter.addEventListener('change', function() {
            loadMappingData();
        });
    }
    
    if (regionFilter) {
        regionFilter.addEventListener('change', function() {
            loadMappingData();
        });
    }
    
    if (cityFilter) {
        cityFilter.addEventListener('change', function() {
            loadMappingData();
        });
    }
    
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', function() {
            if (countryFilter) countryFilter.value = '';
            if (regionFilter) regionFilter.value = '';
            if (cityFilter) cityFilter.value = '';
            loadMappingData();
        });
    }
    
    if (refreshMappingBtn) {
        refreshMappingBtn.addEventListener('click', function() {
            this.querySelector('i').classList.add('fa-spin');
            loadMappingData().finally(() => {
                this.querySelector('i').classList.remove('fa-spin');
            });
        });
    }

});
