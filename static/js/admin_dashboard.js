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
            } else if (sectionName === 'messages') {
                // Load messages when switching to messages section
                loadAllMessages();
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
            const preview = lastMessage ? lastMessage.message.substring(0, 60) + '...' : 'No message';
            const unreadBadge = conv.unread_count > 0 ? `<span class="conversation-badge">${conv.unread_count}</span>` : '';
            
            html += `
                <div class="conversation-item" data-email="${conv.email}">
                    <div class="conversation-item-header">
                        <div>
                            <div class="conversation-user-name">${escapeHtml(conv.name)}</div>
                            <div class="conversation-user-email">${escapeHtml(conv.email)}</div>
                        </div>
                        <div class="conversation-time">${timeAgo}</div>
                    </div>
                    <div class="conversation-preview">${escapeHtml(preview)}</div>
                    ${unreadBadge}
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
                const submitBtn = replyForm.querySelector('.btn-send-reply');
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
                
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
                const submitBtn = replyForm.querySelector('.btn-send-reply');
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Reply';
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

});
