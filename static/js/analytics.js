// Analytics Page JavaScript
// Customer Analytics Dashboard

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const authRequired = document.getElementById('authRequired');
    const authRequiredLoginBtn = document.getElementById('authRequiredLoginBtn');
    const analyticsContent = document.getElementById('analyticsContent');
    const loadingSection = document.getElementById('loadingSection');
    const emptyState = document.getElementById('emptyState');
    const loadMoreContainer = document.getElementById('loadMoreContainer');
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    const predictionsTableBody = document.getElementById('predictionsTableBody');
    
    // Mobile Menu
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    
    // Authentication Elements
    const guestProfileSection = document.getElementById('guestProfileSection');
    const guestProfileBtn = document.getElementById('guestProfileBtn');
    const guestProfileDropdown = document.getElementById('guestProfileDropdown');
    const dropdownLoginBtn = document.getElementById('dropdownLoginBtn');
    const dropdownSignupBtn = document.getElementById('dropdownSignupBtn');
    const profileSection = document.getElementById('profileSection');
    const profileBtn = document.getElementById('profileBtn');
    const profileDropdown = document.getElementById('profileDropdown');
    const userEmail = document.getElementById('userEmail');
    const userEmailDropdown = document.getElementById('userEmailDropdown');
    const logoutBtn = document.getElementById('logoutBtn');
    const deleteAccountBtn = document.getElementById('deleteAccountBtn');
    
    // Mobile Auth Elements
    const mobileAuthButtons = document.getElementById('mobileAuthButtons');
    const mobileProfileSection = document.getElementById('mobileProfileSection');
    const mobileLoginBtn = document.getElementById('mobileLoginBtn');
    const mobileSignupBtn = document.getElementById('mobileSignupBtn');
    const mobileLogoutBtn = document.getElementById('mobileLogoutBtn');
    const mobileDeleteAccountBtn = document.getElementById('mobileDeleteAccountBtn');
    const mobileUserEmail = document.getElementById('mobileUserEmail');
    
    // Modal Elements
    const loginModal = document.getElementById('loginModal');
    const signupModal = document.getElementById('signupModal');
    const closeLoginModal = document.getElementById('closeLoginModal');
    const closeSignupModal = document.getElementById('closeSignupModal');
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const loginError = document.getElementById('loginError');
    const signupError = document.getElementById('signupError');
    const switchToSignup = document.getElementById('switchToSignup');
    const switchToLogin = document.getElementById('switchToLogin');
    
    let isAuthenticated = false;
    let currentUser = null;
    let currentPage = 1;
    let hasMorePredictions = false;
    let diseaseDistributionChart = null;
    let confidenceChart = null;

    // ============================================
    // Authentication Functions
    // ============================================
    
    async function checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status');
            const data = await response.json();
            
            if (data.authenticated) {
                isAuthenticated = true;
                currentUser = data.user;
                updateAuthUI(true);
                loadAnalytics();
            } else {
                isAuthenticated = false;
                currentUser = null;
                updateAuthUI(false);
                showAuthRequired();
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
            isAuthenticated = false;
            updateAuthUI(false);
            showAuthRequired();
        }
    }
    
    function updateAuthUI(authenticated) {
        const dashboardBtn = document.getElementById('dashboardBtn');
        
        if (authenticated && currentUser) {
            // Desktop UI
            guestProfileSection.classList.add('hidden');
            profileSection.classList.remove('hidden');
            userEmail.textContent = currentUser.email;
            userEmailDropdown.textContent = currentUser.email;
            
            // Mobile UI
            mobileAuthButtons.classList.add('hidden');
            mobileProfileSection.classList.remove('hidden');
            mobileUserEmail.textContent = currentUser.email;
            
            // Show dashboard button for admin
            if (currentUser.user_type === 'admin') {
                dashboardBtn.classList.remove('hidden');
            } else {
                dashboardBtn.classList.add('hidden');
            }
        } else {
            // Desktop UI
            guestProfileSection.classList.remove('hidden');
            profileSection.classList.add('hidden');
            
            // Mobile UI
            mobileAuthButtons.classList.remove('hidden');
            mobileProfileSection.classList.add('hidden');
        }
    }
    
    function showAuthRequired() {
        loadingSection.classList.add('hidden');
        analyticsContent.classList.add('hidden');
        authRequired.classList.remove('hidden');
    }
    
    function showAnalytics() {
        loadingSection.classList.add('hidden');
        authRequired.classList.add('hidden');
        analyticsContent.classList.remove('hidden');
    }
    
    function showLoading() {
        authRequired.classList.add('hidden');
        analyticsContent.classList.add('hidden');
        loadingSection.classList.remove('hidden');
    }

    // ============================================
    // Analytics Functions
    // ============================================
    
    async function loadAnalytics() {
        showLoading();
        
        try {
            // Load statistics and predictions in parallel
            const [statsResponse, predictionsResponse] = await Promise.all([
                fetch('/api/user/statistics'),
                fetch(`/api/user/predictions?page=1&per_page=10`)
            ]);
            
            const statsData = await statsResponse.json();
            const predictionsData = await predictionsResponse.json();
            
            if (statsData.success && predictionsData.success) {
                // Update statistics
                updateStatistics(statsData);
                
                // Update charts
                updateCharts(statsData.disease_stats);
                
                // Update predictions table
                updatePredictionsTable(predictionsData.predictions);
                
                // Check if there are more predictions
                hasMorePredictions = predictionsData.page < predictionsData.total_pages;
                if (hasMorePredictions) {
                    loadMoreContainer.classList.remove('hidden');
                } else {
                    loadMoreContainer.classList.add('hidden');
                }
                
                // Show empty state if no predictions
                if (predictionsData.total === 0) {
                    emptyState.classList.remove('hidden');
                } else {
                    emptyState.classList.add('hidden');
                }
                
                showAnalytics();
            } else {
                throw new Error('Failed to load analytics data');
            }
        } catch (error) {
            console.error('Error loading analytics:', error);
            alert('Failed to load analytics. Please try again.');
        }
    }
    
    function updateStatistics(data) {
        // Total predictions
        document.getElementById('totalPredictions').textContent = data.total_predictions;
        
        // Diseases detected (unique diseases)
        document.getElementById('diseasesDetected').textContent = data.disease_stats.length;
        
        // Most common disease
        if (data.disease_stats.length > 0) {
            const mostCommon = data.disease_stats[0];
            document.getElementById('mostCommonDisease').textContent = formatDiseaseName(mostCommon.disease);
        } else {
            document.getElementById('mostCommonDisease').textContent = '-';
        }
        
        // Average confidence
        if (data.disease_stats.length > 0) {
            const totalConfidence = data.disease_stats.reduce((sum, stat) => sum + stat.avg_confidence, 0);
            const avgConfidence = totalConfidence / data.disease_stats.length;
            document.getElementById('avgConfidence').textContent = Math.round(avgConfidence) + '%';
        } else {
            document.getElementById('avgConfidence').textContent = '0%';
        }
    }
    
    function updateCharts(diseaseStats) {
        if (diseaseStats.length === 0) return;
        
        // Prepare data for charts
        const labels = diseaseStats.map(stat => formatDiseaseName(stat.disease));
        const counts = diseaseStats.map(stat => stat.count);
        const confidences = diseaseStats.map(stat => stat.avg_confidence);
        
        // Colors for charts
        const colors = [
            '#10b981', // Green
            '#f59e0b', // Amber
            '#ef4444', // Red
            '#3b82f6', // Blue
            '#8b5cf6', // Purple
            '#ec4899', // Pink
            '#14b8a6', // Teal
            '#f97316', // Orange
        ];
        
        // Disease Distribution Chart (Doughnut)
        const diseaseCtx = document.getElementById('diseaseDistributionChart');
        if (diseaseDistributionChart) {
            diseaseDistributionChart.destroy();
        }
        diseaseDistributionChart = new Chart(diseaseCtx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: counts,
                    backgroundColor: colors.slice(0, labels.length),
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
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
        
        // Confidence Levels Chart (Bar)
        const confidenceCtx = document.getElementById('confidenceChart');
        if (confidenceChart) {
            confidenceChart.destroy();
        }
        confidenceChart = new Chart(confidenceCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Average Confidence (%)',
                    data: confidences,
                    backgroundColor: colors.slice(0, labels.length).map(color => color + '80'),
                    borderColor: colors.slice(0, labels.length),
                    borderWidth: 2,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Confidence: ${context.parsed.y.toFixed(1)}%`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    function updatePredictionsTable(predictions) {
        predictions.forEach(prediction => {
            const row = createPredictionRow(prediction);
            predictionsTableBody.appendChild(row);
        });
    }
    
    function createPredictionRow(prediction) {
        const row = document.createElement('tr');
        
        // Parse timestamp
        const date = new Date(prediction.timestamp);
        const dateStr = date.toLocaleDateString();
        const timeStr = date.toLocaleTimeString();
        
        // Format disease name
        const diseaseName = formatDiseaseName(prediction.predicted_disease);
        
        // Confidence level
        const confidence = Math.round(prediction.confidence);
        let confidenceClass = 'confidence-low';
        if (confidence >= 80) confidenceClass = 'confidence-high';
        else if (confidence >= 60) confidenceClass = 'confidence-medium';
        
        // Status
        const isHealthy = prediction.predicted_disease.toLowerCase().includes('healthy');
        const statusClass = isHealthy ? 'status-healthy' : 'status-diseased';
        const statusIcon = isHealthy ? 'fa-check-circle' : 'fa-exclamation-triangle';
        const statusText = isHealthy ? 'Healthy' : 'Diseased';
        
        row.innerHTML = `
            <td data-label="Date">${dateStr}</td>
            <td data-label="Time">${timeStr}</td>
            <td data-label="Disease" class="disease-name">${diseaseName}</td>
            <td data-label="Confidence">
                <span class="confidence-badge ${confidenceClass}">${confidence}%</span>
            </td>
            <td data-label="Status">
                <span class="status-badge ${statusClass}">
                    <i class="fas ${statusIcon}"></i> ${statusText}
                </span>
            </td>
        `;
        
        return row;
    }
    
    function formatDiseaseName(disease) {
        // Remove "Chilli" prefix and clean up formatting
        return disease
            .replace(/Chilli_+/gi, '')
            .replace(/_+/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
    }
    
    // Load more predictions
    async function loadMorePredictions() {
        if (!hasMorePredictions) return;
        
        loadMoreBtn.disabled = true;
        loadMoreBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        
        try {
            currentPage++;
            const response = await fetch(`/api/user/predictions?page=${currentPage}&per_page=10`);
            const data = await response.json();
            
            if (data.success) {
                updatePredictionsTable(data.predictions);
                
                hasMorePredictions = data.page < data.total_pages;
                if (!hasMorePredictions) {
                    loadMoreContainer.classList.add('hidden');
                }
            }
        } catch (error) {
            console.error('Error loading more predictions:', error);
            alert('Failed to load more predictions');
        } finally {
            loadMoreBtn.disabled = false;
            loadMoreBtn.innerHTML = '<i class="fas fa-plus"></i> Load More';
        }
    }

    // ============================================
    // UI Event Handlers
    // ============================================
    
    // Mobile menu toggle
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            const icon = this.querySelector('i');
            if (mobileMenu.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }
    
    // Profile dropdowns
    if (guestProfileBtn) {
        guestProfileBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            guestProfileDropdown.classList.toggle('hidden');
        });
    }
    
    if (profileBtn) {
        profileBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            profileDropdown.classList.toggle('hidden');
        });
    }
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function() {
        if (guestProfileDropdown) guestProfileDropdown.classList.add('hidden');
        if (profileDropdown) profileDropdown.classList.add('hidden');
    });
    
    // Auth required login button
    if (authRequiredLoginBtn) {
        authRequiredLoginBtn.addEventListener('click', function() {
            openLoginModal();
        });
    }
    
    // Modal open/close handlers
    function openLoginModal() {
        loginModal.classList.remove('hidden');
        signupModal.classList.add('hidden');
        loginError.classList.add('hidden');
    }
    
    function openSignupModal() {
        signupModal.classList.remove('hidden');
        loginModal.classList.add('hidden');
        signupError.classList.add('hidden');
    }
    
    function closeModals() {
        loginModal.classList.add('hidden');
        signupModal.classList.add('hidden');
    }
    
    // Dropdown login/signup buttons
    if (dropdownLoginBtn) dropdownLoginBtn.addEventListener('click', openLoginModal);
    if (dropdownSignupBtn) dropdownSignupBtn.addEventListener('click', openSignupModal);
    if (mobileLoginBtn) mobileLoginBtn.addEventListener('click', openLoginModal);
    if (mobileSignupBtn) mobileSignupBtn.addEventListener('click', openSignupModal);
    
    // Modal close buttons
    if (closeLoginModal) closeLoginModal.addEventListener('click', closeModals);
    if (closeSignupModal) closeSignupModal.addEventListener('click', closeModals);
    
    // Modal switch links
    if (switchToSignup) {
        switchToSignup.addEventListener('click', function(e) {
            e.preventDefault();
            openSignupModal();
        });
    }
    
    if (switchToLogin) {
        switchToLogin.addEventListener('click', function(e) {
            e.preventDefault();
            openLoginModal();
        });
    }
    
    // Login form submission
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    closeModals();
                    window.location.reload();
                } else {
                    loginError.textContent = data.error || 'Login failed';
                    loginError.classList.remove('hidden');
                }
            } catch (error) {
                console.error('Login error:', error);
                loginError.textContent = 'An error occurred. Please try again.';
                loginError.classList.remove('hidden');
            }
        });
    }
    
    // Signup form submission
    if (signupForm) {
        signupForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('signupEmail').value;
            const password = document.getElementById('signupPassword').value;
            const confirmPassword = document.getElementById('signupConfirmPassword').value;
            
            if (password !== confirmPassword) {
                signupError.textContent = 'Passwords do not match';
                signupError.classList.remove('hidden');
                return;
            }
            
            try {
                const response = await fetch('/api/auth/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    closeModals();
                    window.location.reload();
                } else {
                    signupError.textContent = data.error || 'Signup failed';
                    signupError.classList.remove('hidden');
                }
            } catch (error) {
                console.error('Signup error:', error);
                signupError.textContent = 'An error occurred. Please try again.';
                signupError.classList.remove('hidden');
            }
        });
    }
    
    // Logout handlers
    const logoutHandlers = [logoutBtn, mobileLogoutBtn];
    logoutHandlers.forEach(btn => {
        if (btn) {
            btn.addEventListener('click', async function() {
                try {
                    const response = await fetch('/api/auth/logout', {
                        method: 'POST'
                    });
                    
                    const data = await response.json();
                    if (data.success) {
                        window.location.href = '/';
                    }
                } catch (error) {
                    console.error('Logout error:', error);
                }
            });
        }
    });
    
    // Delete account handlers
    const deleteHandlers = [deleteAccountBtn, mobileDeleteAccountBtn];
    deleteHandlers.forEach(btn => {
        if (btn) {
            btn.addEventListener('click', async function() {
                if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
                    try {
                        const response = await fetch('/api/auth/delete-account', {
                            method: 'DELETE'
                        });
                        
                        const data = await response.json();
                        if (data.success) {
                            alert('Account deleted successfully');
                            window.location.href = '/';
                        } else {
                            alert(data.error || 'Failed to delete account');
                        }
                    } catch (error) {
                        console.error('Delete account error:', error);
                        alert('An error occurred');
                    }
                }
            });
        }
    });
    
    // Load more button
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMorePredictions);
    }
    
    // Initialize
    checkAuthStatus();
});
