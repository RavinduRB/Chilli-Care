// ChilliDoc AI - Main JavaScript
// Industry-level frontend logic

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const selectFileBtn = document.getElementById('selectFileBtn');
    const previewArea = document.getElementById('previewArea');
    const imagePreview = document.getElementById('imagePreview');
    const removeImageBtn = document.getElementById('removeImageBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingState = document.getElementById('loadingState');
    const resultsSection = document.getElementById('resultsSection');
    const newAnalysisBtn = document.getElementById('newAnalysisBtn');
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const ctaStartBtn = document.getElementById('ctaStartBtn');
    
    // Camera Elements
    const openCameraBtn = document.getElementById('openCameraBtn');
    const cameraModal = document.getElementById('cameraModal');
    const cameraOverlay = document.getElementById('cameraOverlay');
    const closeCameraBtn = document.getElementById('closeCameraBtn');
    const cancelCameraBtn = document.getElementById('cancelCameraBtn');
    const cameraVideo = document.getElementById('cameraVideo');
    const cameraCanvas = document.getElementById('cameraCanvas');
    const captureBtn = document.getElementById('captureBtn');
    const switchCameraBtn = document.getElementById('switchCameraBtn');
    
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
    
    // Mobile Menu Elements
    const mobileMenu = document.getElementById('mobileMenu');
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
    
    let selectedFile = null;
    let isAuthenticated = false;
    let currentUser = null;
    let cameraStream = null;
    let currentFacingMode = 'environment'; // 'user' for front camera, 'environment' for back camera

    // ============================================
    // Authentication Functions
    // ============================================
    
    // Check authentication status on page load
    async function checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status');
            const data = await response.json();
            
            if (data.authenticated) {
                isAuthenticated = true;
                currentUser = data.user;
                updateAuthUI(true);
            } else {
                isAuthenticated = false;
                currentUser = null;
                updateAuthUI(false);
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
            isAuthenticated = false;
            updateAuthUI(false);
        }
    }
    
    // Update UI based on authentication status
    function updateAuthUI(authenticated) {
        const dashboardBtn = document.getElementById('dashboardBtn');
        
        if (authenticated && currentUser) {
            // Desktop UI
            if (guestProfileSection) guestProfileSection.classList.add('hidden');
            if (profileSection) profileSection.classList.remove('hidden');
            if (userEmail) userEmail.textContent = currentUser.email;
            if (userEmailDropdown) userEmailDropdown.textContent = currentUser.email;
            
            // Show dashboard button only for admin users
            if (dashboardBtn) {
                if (currentUser.user_type === 'admin') {
                    dashboardBtn.classList.remove('hidden');
                } else {
                    dashboardBtn.classList.add('hidden');
                }
            }
            
            // Mobile UI
            if (mobileAuthButtons) mobileAuthButtons.classList.add('hidden');
            if (mobileProfileSection) mobileProfileSection.classList.remove('hidden');
            if (mobileUserEmail) mobileUserEmail.textContent = currentUser.email;
        } else {
            // Desktop UI
            if (guestProfileSection) guestProfileSection.classList.remove('hidden');
            if (profileSection) profileSection.classList.add('hidden');
            
            // Hide dashboard button
            if (dashboardBtn) dashboardBtn.classList.add('hidden');
            
            // Mobile UI
            if (mobileAuthButtons) mobileAuthButtons.classList.remove('hidden');
            if (mobileProfileSection) mobileProfileSection.classList.add('hidden');
        }
    }
    
    // Show login modal
    function showLoginModal() {
        loginModal.classList.remove('hidden');
        signupModal.classList.add('hidden');
        loginError.classList.add('hidden');
        loginForm.reset();
    }
    
    // Show signup modal
    function showSignupModal() {
        signupModal.classList.remove('hidden');
        loginModal.classList.add('hidden');
        signupError.classList.add('hidden');
        signupForm.reset();
    }
    
    // Hide all modals
    function hideAuthModals() {
        loginModal.classList.add('hidden');
        signupModal.classList.add('hidden');
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
                    isAuthenticated = true;
                    currentUser = data.user;
                    updateAuthUI(true);
                    hideAuthModals();
                    showToast('Login successful! Welcome back.', 'success');
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
            const passwordConfirm = document.getElementById('signupPasswordConfirm').value;
            
            // Validate passwords match
            if (password !== passwordConfirm) {
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
                    isAuthenticated = true;
                    currentUser = data.user;
                    updateAuthUI(true);
                    hideAuthModals();
                    showToast('Account created successfully! Welcome.', 'success');
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
    
    // Logout handler
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async function() {
            try {
                const response = await fetch('/api/auth/logout', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    isAuthenticated = false;
                    currentUser = null;
                    updateAuthUI(false);
                    profileDropdown.classList.add('hidden');
                    showToast('Logged out successfully', 'success');
                }
            } catch (error) {
                console.error('Logout error:', error);
                showToast('Logout failed. Please try again.', 'error');
            }
        });
    }
    
    // Delete account handler
    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', async function() {
            if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
                return;
            }
            
            try {
                const response = await fetch('/api/auth/delete-account', {
                    method: 'DELETE'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    isAuthenticated = false;
                    currentUser = null;
                    updateAuthUI(false);
                    profileDropdown.classList.add('hidden');
                    showToast('Account deleted successfully', 'success');
                } else {
                    showToast(data.error || 'Failed to delete account', 'error');
                }
            } catch (error) {
                console.error('Delete account error:', error);
                showToast('Failed to delete account. Please try again.', 'error');
            }
        });
    }
    
    // Mobile logout handler
    if (mobileLogoutBtn) {
        mobileLogoutBtn.addEventListener('click', async function() {
            try {
                const response = await fetch('/api/auth/logout', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    isAuthenticated = false;
                    currentUser = null;
                    updateAuthUI(false);
                    // Close mobile menu
                    if (mobileMenu) mobileMenu.classList.remove('active');
                    if (mobileMenuToggle) {
                        const icon = mobileMenuToggle.querySelector('i');
                        icon.classList.remove('fa-times');
                        icon.classList.add('fa-bars');
                    }
                    showToast('Logged out successfully', 'success');
                }
            } catch (error) {
                console.error('Logout error:', error);
                showToast('Logout failed. Please try again.', 'error');
            }
        });
    }
    
    // Mobile delete account handler
    if (mobileDeleteAccountBtn) {
        mobileDeleteAccountBtn.addEventListener('click', async function() {
            if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
                return;
            }
            
            try {
                const response = await fetch('/api/auth/delete-account', {
                    method: 'DELETE'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    isAuthenticated = false;
                    currentUser = null;
                    updateAuthUI(false);
                    // Close mobile menu
                    if (mobileMenu) mobileMenu.classList.remove('active');
                    if (mobileMenuToggle) {
                        const icon = mobileMenuToggle.querySelector('i');
                        icon.classList.remove('fa-times');
                        icon.classList.add('fa-bars');
                    }
                    showToast('Account deleted successfully', 'success');
                } else {
                    showToast(data.error || 'Failed to delete account', 'error');
                }
            } catch (error) {
                console.error('Delete account error:', error);
                showToast('Failed to delete account. Please try again.', 'error');
            }
        });
    }
    
    // Modal event listeners
    // Guest profile dropdown buttons
    if (dropdownLoginBtn) {
        dropdownLoginBtn.addEventListener('click', function() {
            showLoginModal();
            if (guestProfileDropdown) guestProfileDropdown.classList.add('hidden');
        });
    }
    
    if (dropdownSignupBtn) {
        dropdownSignupBtn.addEventListener('click', function() {
            showSignupModal();
            if (guestProfileDropdown) guestProfileDropdown.classList.add('hidden');
        });
    }
    
    // Mobile authentication buttons
    if (mobileLoginBtn) {
        mobileLoginBtn.addEventListener('click', function() {
            showLoginModal();
            // Close mobile menu
            if (mobileMenu) {
                mobileMenu.classList.remove('active');
                const icon = mobileMenuToggle.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }
    
    if (mobileSignupBtn) {
        mobileSignupBtn.addEventListener('click', function() {
            showSignupModal();
            // Close mobile menu
            if (mobileMenu) {
                mobileMenu.classList.remove('active');
                const icon = mobileMenuToggle.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }
    
    if (closeLoginModal) {
        closeLoginModal.addEventListener('click', hideAuthModals);
    }
    
    if (closeSignupModal) {
        closeSignupModal.addEventListener('click', hideAuthModals);
    }
    
    if (switchToSignup) {
        switchToSignup.addEventListener('click', function(e) {
            e.preventDefault();
            showSignupModal();
        });
    }
    
    if (switchToLogin) {
        switchToLogin.addEventListener('click', function(e) {
            e.preventDefault();
            showLoginModal();
        });
    }
    
    // Profile dropdown toggle
    if (profileBtn) {
        profileBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            profileDropdown.classList.toggle('hidden');
        });
    }
    
    // Guest profile dropdown toggle
    if (guestProfileBtn) {
        guestProfileBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            guestProfileDropdown.classList.toggle('hidden');
        });
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (profileBtn && !profileBtn.contains(e.target) && !profileDropdown.contains(e.target)) {
            profileDropdown.classList.add('hidden');
        }
        if (guestProfileBtn && !guestProfileBtn.contains(e.target) && !guestProfileDropdown.contains(e.target)) {
            guestProfileDropdown.classList.add('hidden');
        }
    });
    
    // Close modals when clicking overlay
    if (loginModal) {
        loginModal.addEventListener('click', function(e) {
            if (e.target === loginModal) {
                hideAuthModals();
            }
        });
    }
    
    if (signupModal) {
        signupModal.addEventListener('click', function(e) {
            if (e.target === signupModal) {
                hideAuthModals();
            }
        });
    }
    
    // Initialize authentication check
    checkAuthStatus();

    // ============================================
    // File Upload Handlers
    // ============================================
    
    // Click to select file
    if (selectFileBtn) {
        selectFileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });
    }

    // Upload area click handler
    if (uploadArea) {
        uploadArea.addEventListener('click', (e) => {
            // Trigger file input when clicking on upload area (but not on button)
            if (e.target === uploadArea || e.target.closest('.upload-icon') || e.target.closest('.upload-content h3')) {
                fileInput.click();
            }
        });
    }

    // File input change
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                handleFileSelect(file);
            }
        });
    }

    // Drag and drop
    if (uploadArea) {
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', function() {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                handleFileSelect(file);
            } else {
                showToast('Please upload a valid image file', 'error');
            }
        });
    }

    // Remove image
    if (removeImageBtn) {
        removeImageBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            resetUpload();
        });
    }

    // Analyze button
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', function() {
            // Check authentication before allowing analysis
            if (!isAuthenticated) {
                showToast('Please log in to analyze images', 'error');
                showLoginModal();
                return;
            }
            
            if (selectedFile) {
                analyzeImage(selectedFile);
            }
        });
    }

    // New analysis button
    if (newAnalysisBtn) {
        newAnalysisBtn.addEventListener('click', function() {
            resetUpload();
            resultsSection.classList.add('hidden');
            document.getElementById('uploadSection').classList.remove('hidden');
            document.getElementById('uploadSection').scrollIntoView({ behavior: 'smooth' });
        });
    }

    // CTA Start Button - Smart scroll to results or upload section
    if (ctaStartBtn) {
        ctaStartBtn.addEventListener('click', function() {
            // Check if results section is visible
            if (resultsSection && !resultsSection.classList.contains('hidden')) {
                // Scroll to the new analysis button at the top of results
                newAnalysisBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                // No results yet, scroll to upload section
                document.getElementById('uploadSection').scrollIntoView({ behavior: 'smooth' });
            }
        });
    }

    // ============================================
    // Camera Capture Handlers
    // ============================================

    // Open camera
    if (openCameraBtn) {
        openCameraBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            openCamera();
        });
    }

    // Close camera modal
    if (closeCameraBtn) {
        closeCameraBtn.addEventListener('click', function() {
            closeCamera();
        });
    }

    if (cancelCameraBtn) {
        cancelCameraBtn.addEventListener('click', function() {
            closeCamera();
        });
    }

    // Close camera when clicking overlay
    if (cameraOverlay) {
        cameraOverlay.addEventListener('click', function() {
            closeCamera();
        });
    }

    // Capture photo
    if (captureBtn) {
        captureBtn.addEventListener('click', function() {
            capturePhoto();
        });
    }

    // Switch camera (front/back)
    if (switchCameraBtn) {
        switchCameraBtn.addEventListener('click', function() {
            switchCamera();
        });
    }

    // Mobile menu toggle
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            mobileMenu.classList.toggle('active');
            
            // Change icon
            const icon = mobileMenuToggle.querySelector('i');
            if (mobileMenu.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (mobileMenu && mobileMenu.classList.contains('active')) {
                if (!e.target.closest('.nav-wrapper') && !e.target.closest('.mobile-menu')) {
                    mobileMenu.classList.remove('active');
                    const icon = mobileMenuToggle.querySelector('i');
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
        });
        
        // Close menu when clicking a nav link
        document.querySelectorAll('.mobile-nav-item').forEach(item => {
            item.addEventListener('click', function() {
                mobileMenu.classList.remove('active');
                const icon = mobileMenuToggle.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            });
        });
    }
    
    // Touch-friendly improvements for mobile
    if ('ontouchstart' in window) {
        // Add touch class to body for CSS targeting
        document.body.classList.add('touch-device');
        
        // Prevent click delay on buttons
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.98)';
            });
            btn.addEventListener('touchend', function() {
                this.style.transform = '';
            });
        });
    }
    
    // Viewport resize handler for responsive adjustments
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // Adjust upload area on orientation change
            if (window.innerWidth < 768 && uploadArea) {
                uploadArea.style.minHeight = '250px';
            } else if (uploadArea) {
                uploadArea.style.minHeight = '';
            }
        }, 250);
    });

    // ============================================
    // Core Functions
    // ============================================

    function handleFileSelect(file) {
        // Log for debugging
        console.log('File selected:', {
            name: file.name,
            type: file.type,
            size: file.size,
            lastModified: file.lastModified
        });

        // Validate file type
        if (!file.type.startsWith('image/')) {
            showToast('Please select an image file', 'error');
            return;
        }

        // Validate file size (16MB max)
        if (file.size > 16 * 1024 * 1024) {
            showToast('File size must be less than 16MB', 'error');
            return;
        }

        // Process and optimize the image before preview
        processAndPreviewImage(file);
    }

    function processAndPreviewImage(file) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const img = new Image();
            
            img.onload = function() {
                // Create canvas for image processing
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                
                // Calculate dimensions (max 1920px on longest side for consistency)
                const maxDimension = 1920;
                let width = img.width;
                let height = img.height;
                
                if (width > maxDimension || height > maxDimension) {
                    const scale = Math.min(maxDimension / width, maxDimension / height);
                    width = Math.round(width * scale);
                    height = Math.round(height * scale);
                }
                
                // Set canvas size
                canvas.width = width;
                canvas.height = height;
                
                // Draw and compress image
                ctx.drawImage(img, 0, 0, width, height);
                
                // Convert to blob
                canvas.toBlob(function(blob) {
                    if (!blob) {
                        // Fallback to original file
                        console.warn('Failed to process image, using original');
                        displayImagePreview(e.target.result);
                        selectedFile = file;
                        showToast('Image loaded successfully!', 'success');
                        return;
                    }
                    
                    // Create optimized file
                    const optimizedFile = new File([blob], file.name, {
                        type: 'image/jpeg',
                        lastModified: Date.now()
                    });
                    
                    console.log('Image optimized:', {
                        originalSize: file.size,
                        optimizedSize: optimizedFile.size,
                        dimensions: `${width}x${height}`,
                        reduction: `${((1 - optimizedFile.size / file.size) * 100).toFixed(1)}%`
                    });
                    
                    // Store optimized file
                    selectedFile = optimizedFile;
                    
                    // Show preview
                    displayImagePreview(canvas.toDataURL('image/jpeg', 0.92));
                    
                    showToast('Image loaded successfully!', 'success');
                }, 'image/jpeg', 0.92);
            };
            
            img.onerror = function() {
                console.error('Failed to load image');
                showToast('Failed to load image. Please try again.', 'error');
            };
            
            img.src = e.target.result;
        };
        
        reader.onerror = function(e) {
            console.error('FileReader error:', e);
            showToast('Failed to load image. Please try again.', 'error');
        };
        
        reader.readAsDataURL(file);
    }

    function displayImagePreview(dataUrl) {
        imagePreview.src = dataUrl;
        uploadArea.classList.add('hidden');
        previewArea.classList.remove('hidden');
    }

    function resetUpload() {
        selectedFile = null;
        fileInput.value = '';
        imagePreview.src = '';
        uploadArea.classList.remove('hidden');
        previewArea.classList.add('hidden');
        loadingState.classList.add('hidden');
    }

    // ============================================
    // Camera Functions
    // ============================================

    async function openCamera() {
        try {
            console.log('Opening camera...');
            
            // Check if getUserMedia is supported
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                showToast('Camera not supported on this device', 'error');
                return;
            }

            // Show camera modal
            cameraModal.classList.remove('hidden');

            // Request camera access
            await startCameraStream();

        } catch (error) {
            console.error('Error opening camera:', error);
            handleCameraError(error);
        }
    }

    async function startCameraStream() {
        try {
            // Stop any existing stream
            if (cameraStream) {
                stopCameraStream();
            }

            // Request camera with specific facing mode
            const constraints = {
                video: {
                    facingMode: currentFacingMode,
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                },
                audio: false
            };

            console.log('Requesting camera with constraints:', constraints);

            cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // Set video source
            cameraVideo.srcObject = cameraStream;
            
            // Wait for video to be ready
            await new Promise((resolve) => {
                cameraVideo.onloadedmetadata = () => {
                    cameraVideo.play();
                    resolve();
                };
            });

            console.log('Camera stream started successfully');
            showToast('Camera ready!', 'success');

        } catch (error) {
            console.error('Error starting camera stream:', error);
            throw error;
        }
    }

    function stopCameraStream() {
        if (cameraStream) {
            cameraStream.getTracks().forEach(track => {
                track.stop();
            });
            cameraStream = null;
            cameraVideo.srcObject = null;
            console.log('Camera stream stopped');
        }
    }

    function closeCamera() {
        stopCameraStream();
        cameraModal.classList.add('hidden');
        console.log('Camera modal closed');
    }

    async function switchCamera() {
        try {
            // Toggle facing mode
            currentFacingMode = currentFacingMode === 'environment' ? 'user' : 'environment';
            console.log('Switching to camera:', currentFacingMode);
            
            // Restart stream with new facing mode
            await startCameraStream();
            
            showToast(`Switched to ${currentFacingMode === 'user' ? 'front' : 'back'} camera`, 'success');
        } catch (error) {
            console.error('Error switching camera:', error);
            // Revert facing mode on error
            currentFacingMode = currentFacingMode === 'environment' ? 'user' : 'environment';
            showToast('Could not switch camera', 'error');
        }
    }

    function capturePhoto() {
        try {
            console.log('Capturing photo...');

            // Get video dimensions
            const videoWidth = cameraVideo.videoWidth;
            const videoHeight = cameraVideo.videoHeight;

            if (!videoWidth || !videoHeight) {
                showToast('Camera not ready. Please try again.', 'error');
                return;
            }

            // Set canvas dimensions to match video
            cameraCanvas.width = videoWidth;
            cameraCanvas.height = videoHeight;

            // Draw video frame to canvas
            const ctx = cameraCanvas.getContext('2d');
            ctx.drawImage(cameraVideo, 0, 0, videoWidth, videoHeight);

            // Convert canvas to blob
            cameraCanvas.toBlob(function(blob) {
                if (!blob) {
                    showToast('Failed to capture photo', 'error');
                    return;
                }

                // Create file from blob
                const timestamp = new Date().getTime();
                const capturedFile = new File([blob], `chilli_capture_${timestamp}.jpg`, {
                    type: 'image/jpeg',
                    lastModified: timestamp
                });

                console.log('Photo captured:', {
                    size: capturedFile.size,
                    dimensions: `${videoWidth}x${videoHeight}`,
                    type: capturedFile.type
                });

                // Close camera modal
                closeCamera();

                // Process the captured image
                processAndPreviewImage(capturedFile);

                showToast('Photo captured successfully!', 'success');

            }, 'image/jpeg', 0.92);

        } catch (error) {
            console.error('Error capturing photo:', error);
            showToast('Failed to capture photo. Please try again.', 'error');
        }
    }

    function handleCameraError(error) {
        let errorMessage = 'Camera access denied or unavailable';

        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            errorMessage = 'Camera permission denied. Please allow camera access.';
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
            errorMessage = 'No camera found on this device.';
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
            errorMessage = 'Camera is already in use by another application.';
        } else if (error.name === 'OverconstrainedError') {
            errorMessage = 'Camera does not meet requirements.';
        } else if (error.name === 'SecurityError') {
            errorMessage = 'Camera access blocked for security reasons.';
        }

        console.error('Camera error:', error.name, error.message);
        showToast(errorMessage, 'error');
        closeCamera();
    }

    async function analyzeImage(file) {
        try {
            console.log('Starting analysis for:', {
                name: file.name,
                type: file.type,
                size: file.size
            });

            // Show loading state
            previewArea.classList.add('hidden');
            loadingState.classList.remove('hidden');

            // Create form data
            const formData = new FormData();
            formData.append('file', file);

            console.log('Sending request to /api/predict...');

            // Make API request
            const response = await fetch('/api/predict', {
                method: 'POST',
                body: formData
            });

            console.log('Response received:', {
                status: response.status,
                statusText: response.statusText,
                ok: response.ok
            });

            if (!response.ok) {
                let errorData;
                try {
                    errorData = await response.json();
                } catch (e) {
                    const errorText = await response.text();
                    console.error('Server error:', errorText);
                    throw new Error(`Prediction failed: ${response.statusText}`);
                }
                
                // Handle validation errors (invalid image)
                if (errorData.error === 'Invalid Image') {
                    console.warn('Image validation failed:', errorData.message);
                    
                    // Show detailed error message with suggestion
                    showValidationError(errorData);
                    
                    loadingState.classList.add('hidden');
                    previewArea.classList.remove('hidden');
                    return;
                }
                
                console.error('Server error:', errorData);
                throw new Error(errorData.error || 'Prediction failed');
            }

            const data = await response.json();
            console.log('Prediction data:', data);

            if (data.success) {
                displayResults(data);
                showToast('Analysis complete!', 'success');
            } else {
                throw new Error(data.error || 'Unknown error');
            }

        } catch (error) {
            console.error('Analysis error:', error);
            showToast('Error analyzing image. Please try again.', 'error');
            loadingState.classList.add('hidden');
            previewArea.classList.remove('hidden');
        }
    }

    function displayResults(data) {
        const prediction = data.prediction;
        const diseaseInfo = data.disease_info;

        // Hide loading, hide upload section, show results
        loadingState.classList.add('hidden');
        document.getElementById('uploadSection').classList.add('hidden');
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth' });

        // Update severity badge
        const severityBadge = document.getElementById('severityBadge');
        const severityText = document.getElementById('severityText');
        const severity = diseaseInfo.severity || 'Unknown';
        
        severityText.textContent = `${severity} Severity`;
        severityBadge.className = 'result-badge';
        
        if (severity === 'High' || severity === 'Very High') {
            severityBadge.style.background = 'rgba(239, 68, 68, 0.2)';
        } else if (severity === 'Medium') {
            severityBadge.style.background = 'rgba(245, 158, 11, 0.2)';
        } else if (severity === 'None') {
            severityBadge.style.background = 'rgba(16, 185, 129, 0.2)';
        }

        // Update disease name
        document.getElementById('diseaseName').textContent = prediction.predicted_class;

        // Update confidence
        const confidence = prediction.confidence;
        document.getElementById('confidenceFill').style.width = `${confidence}%`;
        document.getElementById('confidenceValue').textContent = `${confidence.toFixed(2)}%`;

        // Update description
        document.getElementById('diseaseDescription').textContent = diseaseInfo.description || 'No description available';

        // Update symptoms
        updateList('symptomsList', diseaseInfo.symptoms || []);

        // Update treatment
        updateList('treatmentList', diseaseInfo.treatment || []);

        // Update prevention
        updateList('preventionList', diseaseInfo.prevention || []);

        // Update organic solutions
        updateList('organicList', diseaseInfo.organic_solutions || []);

        // Update probability chart
        updateProbabilityChart(prediction.all_probabilities);

        // Add animation
        resultsSection.classList.add('fade-in');
    }

    function updateList(elementId, items) {
        const list = document.getElementById(elementId);
        list.innerHTML = '';
        
        if (items.length === 0) {
            list.innerHTML = '<li>No information available</li>';
            return;
        }

        items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            list.appendChild(li);
        });
    }

    function updateProbabilityChart(probabilities) {
        const chartContainer = document.getElementById('probabilityChart');
        chartContainer.innerHTML = '';

        // Sort probabilities
        const sortedProbs = Object.entries(probabilities).sort((a, b) => b[1] - a[1]);

        sortedProbs.forEach(([disease, probability]) => {
            const item = document.createElement('div');
            item.className = 'probability-item';
            
            item.innerHTML = `
                <div class="probability-label">${disease}</div>
                <div class="probability-bar">
                    <div class="probability-fill" style="width: ${probability}%"></div>
                </div>
                <div class="probability-value">${probability.toFixed(2)}%</div>
            `;
            
            chartContainer.appendChild(item);
        });
    }

    // ============================================
    // Toast Notifications
    // ============================================
    
    function showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        const toastIcon = toast.querySelector('i');

        toastMessage.textContent = message;

        // Update icon based on type
        if (type === 'error') {
            toastIcon.className = 'fas fa-exclamation-circle';
            toastIcon.style.color = '#ef4444';
        } else if (type === 'warning') {
            toastIcon.className = 'fas fa-exclamation-triangle';
            toastIcon.style.color = '#f59e0b';
        } else {
            toastIcon.className = 'fas fa-check-circle';
            toastIcon.style.color = '#10b981';
        }

        // Show toast
        toast.classList.remove('hidden');
        toast.classList.add('show');

        // Hide after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.classList.add('hidden');
            }, 300);
        }, 3000);
    }

    function showValidationError(errorData) {
        // Show detailed toast message
        const message = errorData.message || 'This does not appear to be a chilli plant image.';
        const suggestion = errorData.suggestion || 'Please upload a clear image of a chilli plant leaf.';
        
        // Show error toast with more detail
        showToast(`❌ ${message} ${suggestion}`, 'error');
        
        // Automatically reset upload after showing error
        setTimeout(() => {
            resetUpload();
        }, 3500);
    }

    // ============================================
    // Smooth Scrolling
    // ============================================
    
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');

            // ❗ skip invalid "#"
            if (!targetId || targetId === "#") return;

            e.preventDefault();

            const target = document.querySelector(targetId);

            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ============================================
    // Intersection Observer for Animations
    // ============================================
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
        observer.observe(card);
    });

    // ============================================
    // Performance Monitoring
    // ============================================
    
    // Log performance metrics
    window.addEventListener('load', () => {
        const perfData = performance.timing;
        const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        console.log(`Page Load Time: ${pageLoadTime}ms`);
    });

    // ============================================
    // Service Worker Registration (PWA)
    // ============================================
    
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('ServiceWorker registered:', registration);
                })
                .catch(error => {
                    console.log('ServiceWorker registration failed:', error);
                });
        });
    }

    // ============================================
    // Keyboard Shortcuts
    // ============================================
    
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + U: Upload new image
        if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
            e.preventDefault();
            fileInput.click();
        }
        
        // Escape: Reset upload
        if (e.key === 'Escape') {
            if (!resultsSection.classList.contains('hidden')) {
                resetUpload();
                resultsSection.classList.add('hidden');
                document.getElementById('uploadSection').classList.remove('hidden');
            }
            // Close camera if open
            if (!cameraModal.classList.contains('hidden')) {
                closeCamera();
            }
        }
        
        // Ctrl/Cmd + C: Open camera
        if ((e.ctrlKey || e.metaKey) && e.key === 'c' && openCameraBtn) {
            e.preventDefault();
            openCamera();
        }
    });

    // Cleanup camera stream on page unload
    window.addEventListener('beforeunload', () => {
        if (cameraStream) {
            stopCameraStream();
        }
    });

    // Handle visibility change (tab switching)
    document.addEventListener('visibilitychange', () => {
        if (document.hidden && cameraStream) {
            console.log('Page hidden, stopping camera');
            closeCamera();
        }
    });

    console.log('ChilliDoc AI initialized successfully! 🌶️');
});

// ============================================
// Utility Functions
// ============================================

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Check if device is mobile
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// Get user's location (for future features)
async function getUserLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation not supported'));
        } else {
            navigator.geolocation.getCurrentPosition(
                position => resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                }),
                error => reject(error)
            );
        }
    });
}

// ============================================
// Chatbot Functionality
// ============================================

// Chatbot knowledge base
const chatbotKnowledge = {
    greetings: ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
    
    responses: {
        // Disease Prevention
        'prevent|prevention|stop|avoid': {
            keywords: ['disease', 'problem', 'infection'],
            answer: `🛡️ **Disease Prevention Tips:**

• Use disease-free seeds and seedlings
• Maintain proper spacing between plants
• Ensure good air circulation
• Avoid overhead watering
• Remove infected plant parts immediately
• Practice crop rotation
• Apply organic fungicides preventively
• Keep the field clean and weed-free`
        },
        
        // Fertilizer
        'fertilizer|fertiliser|nutrients|feeding': {
            keywords: ['best', 'good', 'recommended', 'use', 'apply'],
            answer: `🌱 **Fertilizer Recommendations:**

• **NPK Ratio:** Use 19:19:19 during vegetative stage
• **Flowering Stage:** Switch to 13:0:45
• **Organic Options:** Compost, vermicompost, neem cake
• **Micronutrients:** Zinc, Boron, Magnesium
• **Application:** Apply every 15-20 days
• **Foliar Spray:** Weekly with micronutrients

💡 Avoid over-fertilization to prevent disease susceptibility`
        },
        
        // Watering
        'water|watering|irrigation': {
            keywords: ['schedule', 'how often', 'frequency', 'much', 'amount'],
            answer: `💧 **Watering Guide:**

• **Frequency:** Water every 3-4 days in summer
• **Winter:** Reduce to once a week
• **Best Time:** Early morning or evening
• **Amount:** Keep soil moist, not waterlogged
• **Method:** Drip irrigation is best
• **Mulching:** Apply to retain moisture

⚠️ Over-watering causes root rot and fungal diseases`
        },
        
        // Pest Control
        'pest|insect|bug': {
            keywords: ['control', 'identify', 'problem', 'attack', 'damage'],
            answer: `🐛 **Pest Management:**

• **Common Pests:** Aphids, Thrips, Whitefly, Mites
• **Signs:** Curled leaves, sticky residue, tiny insects
• **Organic Control:** Neem oil, garlic spray
• **Chemical:** Use only when necessary
• **Natural Predators:** Ladybugs, lacewings
• **Prevention:** Yellow sticky traps, companion planting

🔍 Upload an image for accurate pest identification!`
        },
        
        // Anthracnose
        'anthracnose|anthracnosis': {
            keywords: ['treatment', 'cure', 'control', 'manage'],
            answer: `🍂 **Anthracnose Treatment:**

• Remove and destroy infected fruits/leaves
• Apply copper-based fungicides
• Use Mancozeb or Chlorothalonil
• Improve air circulation
• Avoid overhead irrigation
• Harvest mature fruits promptly
• Practice crop rotation

📝 This disease thrives in humid conditions`
        },
        
        // Leaf Curl
        'leaf curl|curl virus': {
            keywords: ['treatment', 'cure', 'control', 'manage'],
            answer: `🦠 **Leaf Curl Virus Management:**

• Remove infected plants immediately
• Control whitefly vectors with neem oil
• Use yellow sticky traps
• Apply imidacloprid if severe
• Plant resistant varieties
• Use virus-free seedlings
• Maintain plant nutrition

⚠️ Viral diseases cannot be cured, only managed`
        },
        
        // Whitefly
        'whitefly|white fly': {
            keywords: ['control', 'remove', 'kill', 'get rid'],
            answer: `🦟 **Whitefly Control:**

• Spray neem oil (5ml/liter water)
• Use yellow sticky traps
• Apply insecticidal soap
• Chemical: Imidacloprid or Thiamethoxam
• Natural predators: Encarsia formosa
• Remove heavily infested leaves
• Avoid excess nitrogen fertilizer

✅ Monitor plants twice weekly`
        },
        
        // Healthy Plants
        'healthy|no disease|normal': {
            keywords: ['keep', 'maintain', 'grow', 'care'],
            answer: `✨ **Maintaining Healthy Plants:**

• Regular monitoring for early detection
• Balanced nutrition and watering
• Proper spacing and pruning
• Mulching to suppress weeds
• Organic matter for soil health
• Beneficial insects for pest control
• Remove dead/diseased plant parts
• Clean tools to prevent spread

🎯 Prevention is always better than cure!`
        },
        
        // Yellowish
        'yellow|yellowing': {
            keywords: ['leaves', 'plant', 'problem', 'cause'],
            answer: `🍃 **Yellowing Leaves:**

**Causes:**
• Nitrogen deficiency
• Over-watering or poor drainage
• Pest damage (mites, aphids)
• Viral infection
• pH imbalance

**Solutions:**
• Apply nitrogen-rich fertilizer
• Improve drainage
• Check for pests
• Test and adjust soil pH (6.0-6.8)
• Provide adequate sunlight`
        },
        
        // Planting/Growing
        'plant|grow|growing|cultivation': {
            keywords: ['how', 'tips', 'guide', 'start', 'begin'],
            answer: `🌿 **Chilli Growing Guide:**

• **Climate:** 20-30°C temperature
• **Soil:** Well-drained, pH 6.0-6.8
• **Spacing:** 45cm between plants
• **Sunlight:** 6-8 hours daily
• **Germination:** 7-14 days
• **Harvest:** 60-90 days after transplant

📚 Start with healthy seeds or seedlings!`
        },
        
        // Default farming advice
        'default': {
            answer: `I'm here to help with:

🌱 Disease prevention & management
💧 Watering and irrigation
🧪 Fertilization schedules
🐛 Pest identification & control
🌾 Growing tips & best practices

Please ask a specific question, or use the quick reply buttons below!

📸 **Tip:** Upload a plant image for disease diagnosis using the main form.`
        }
    }
};

class FarmerChatbot {
    constructor() {
        this.chatbotToggle = document.getElementById('chatbotToggle');
        this.chatbotModal = document.getElementById('chatbotModal');
        this.chatbotClose = document.getElementById('chatbotClose');
        this.chatbotMessages = document.getElementById('chatbotMessages');
        this.chatbotInput = document.getElementById('chatbotInput');
        this.chatbotSend = document.getElementById('chatbotSend');
        this.quickReplies = document.querySelectorAll('.quick-reply-btn');
        
        this.init();
    }
    
    init() {
        // Toggle chatbot
        if (this.chatbotToggle) {
            this.chatbotToggle.addEventListener('click', () => this.toggleChat());
        }
        
        if (this.chatbotClose) {
            this.chatbotClose.addEventListener('click', () => this.closeChat());
        }
        
        // Send message
        if (this.chatbotSend) {
            this.chatbotSend.addEventListener('click', () => this.sendMessage());
        }
        
        if (this.chatbotInput) {
            this.chatbotInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
        }
        
        // Quick replies
        this.quickReplies.forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.getAttribute('data-message');
                this.sendMessage(message);
            });
        });
    }
    
    toggleChat() {
        if (this.chatbotModal.classList.contains('hidden')) {
            this.openChat();
        } else {
            this.closeChat();
        }
    }
    
    openChat() {
        this.chatbotModal.classList.remove('hidden');
        this.chatbotToggle.style.display = 'none';
        this.chatbotInput.focus();
    }
    
    closeChat() {
        this.chatbotModal.classList.add('hidden');
        this.chatbotToggle.style.display = 'flex';
    }
    
    sendMessage(predefinedMessage = null) {
        const message = predefinedMessage || this.chatbotInput.value.trim();
        
        if (!message) return;
        
        // Add user message
        this.addMessage(message, 'user');
        
        // Clear input
        if (!predefinedMessage) {
            this.chatbotInput.value = '';
        }
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Get bot response after delay
        setTimeout(() => {
            this.removeTypingIndicator();
            const response = this.generateResponse(message);
            this.addMessage(response, 'bot');
        }, 1000 + Math.random() * 1000);
    }
    
    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const time = new Date().toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>
            </div>
            <div class="message-content">
                <p>${this.formatMessage(text)}</p>
                <span class="message-time">${time}</span>
            </div>
        `;
        
        this.chatbotMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(text) {
        // Convert markdown-style formatting
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
    }
    
    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message bot-message typing-message';
        indicator.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        this.chatbotMessages.appendChild(indicator);
        this.scrollToBottom();
    }
    
    removeTypingIndicator() {
        const indicator = this.chatbotMessages.querySelector('.typing-message');
        if (indicator) {
            indicator.remove();
        }
    }
    
    generateResponse(userMessage) {
        const message = userMessage.toLowerCase();
        
        // Check for greetings
        if (chatbotKnowledge.greetings.some(greeting => message.includes(greeting))) {
            return `Hello! 👋 I'm your agricultural assistant. I can help you with chilli plant diseases, pest control, fertilizers, and growing tips. What would you like to know?`;
        }
        
        // Check for thank you
        if (message.includes('thank') || message.includes('thanks')) {
            return `You're welcome! 😊 Feel free to ask if you have more questions. Happy farming! 🌱`;
        }
        
        // Search knowledge base
        for (const [pattern, data] of Object.entries(chatbotKnowledge.responses)) {
            if (pattern === 'default') continue;
            
            const regex = new RegExp(pattern, 'i');
            if (regex.test(message)) {
                // Check if related keywords are present
                if (!data.keywords || data.keywords.some(kw => message.includes(kw))) {
                    return data.answer;
                }
            }
        }
        
        // Default response
        return chatbotKnowledge.responses.default.answer;
    }
    
    scrollToBottom() {
        this.chatbotMessages.scrollTop = this.chatbotMessages.scrollHeight;
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new FarmerChatbot();
});
