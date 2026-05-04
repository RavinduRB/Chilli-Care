"""
Test script to verify all user-facing pages are working properly
"""
import os
import sys

# Test if all templates exist
def test_templates():
    print("=" * 60)
    print("TESTING: User Templates Existence")
    print("=" * 60)
    
    templates_dir = "templates"
    required_templates = [
        'index.html',
        'about.html',
        'diseases.html',
        'contact.html',
        'analytics.html',
        'privacy.html',
        'terms.html',
        'faqs.html',
        'base.html',
        'camera-test.html',
        'responsive-test.html'
    ]
    
    missing = []
    existing = []
    
    for template in required_templates:
        path = os.path.join(templates_dir, template)
        if os.path.exists(path):
            existing.append(template)
            print(f"✓ {template} exists")
        else:
            missing.append(template)
            print(f"✗ {template} MISSING")
    
    print(f"\nSummary: {len(existing)}/{len(required_templates)} templates found")
    return len(missing) == 0

# Test if all static resources exist
def test_static_resources():
    print("\n" + "=" * 60)
    print("TESTING: Static Resources")
    print("=" * 60)
    
    resources = {
        'CSS Files': [
            'static/css/style.css',
            'static/css/diseases.css',
            'static/css/analytics.css'
        ],
        'JavaScript Files': [
            'static/js/main.js',
            'static/js/diseases.js',
            'static/js/analytics.js'
        ],
        'Images': [
            'static/images/Site icon.png',
            'static/images/Chilli Care Logo.png'
        ]
    }
    
    all_exist = True
    
    for category, files in resources.items():
        print(f"\n{category}:")
        for file_path in files:
            if os.path.exists(file_path):
                print(f"  ✓ {file_path}")
            else:
                print(f"  ✗ {file_path} MISSING")
                all_exist = False
    
    return all_exist

# Test if routes are defined
def test_routes():
    print("\n" + "=" * 60)
    print("TESTING: Routes Definition")
    print("=" * 60)
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_routes = [
        ("@app.route('/')", "Home page"),
        ("@app.route('/about')", "About page"),
        ("@app.route('/diseases')", "Diseases page"),
        ("@app.route('/contact')", "Contact page"),
        ("@app.route('/analytics')", "Analytics page"),
        ("@app.route('/privacy')", "Privacy page"),
        ("@app.route('/terms')", "Terms page"),
        ("@app.route('/faqs')", "FAQs page"),
        ("@app.route('/camera-test')", "Camera test page"),
        ("@app.route('/responsive-test')", "Responsive test page")
    ]
    
    all_exist = True
    
    for route, description in required_routes:
        if route in content:
            print(f"✓ {description}: {route}")
        else:
            print(f"✗ {description}: {route} MISSING")
            all_exist = False
    
    return all_exist

# Test if API endpoints exist
def test_api_endpoints():
    print("\n" + "=" * 60)
    print("TESTING: User API Endpoints")
    print("=" * 60)
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_apis = [
        ("@app.route('/api/auth/login'", "Login API"),
        ("@app.route('/api/auth/signup'", "Signup API"),
        ("@app.route('/api/auth/logout'", "Logout API"),
        ("@app.route('/api/auth/status'", "Auth status API"),
        ("@app.route('/api/predict'", "Prediction API"),
        ("@app.route('/api/validate-image'", "Image validation API"),
        ("@app.route('/api/diseases'", "Diseases list API"),
        ("@app.route('/api/notifications'", "Notifications API"),
        ("@app.route('/api/history'", "History API"),
        ("@app.route('/api/user/predictions'", "User predictions API"),
        ("@app.route('/api/user/statistics'", "User statistics API"),
        ("@app.route('/api/analytics/summary'", "Analytics summary API"),
        ("@app.route('/api/analytics/daily'", "Daily analytics API")
    ]
    
    all_exist = True
    
    for api_route, description in required_apis:
        if api_route in content:
            print(f"✓ {description}: {api_route}")
        else:
            print(f"✗ {description}: {api_route} MISSING")
            all_exist = False
    
    return all_exist

# Check JavaScript functionality
def test_javascript_features():
    print("\n" + "=" * 60)
    print("TESTING: JavaScript Features in main.js")
    print("=" * 60)
    
    js_file = 'static/js/main.js'
    
    if not os.path.exists(js_file):
        print(f"✗ {js_file} not found")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    features = [
        ('showToast', 'Toast notification function'),
        ('checkAuthStatus', 'Authentication check'),
        ('handleLogin', 'Login handler'),
        ('handleSignup', 'Signup handler'),
        ('handleLogout', 'Logout handler'),
        ('handlePredict', 'Prediction handler'),
        ('validateImage', 'Image validation'),
        ('password-toggle', 'Password visibility toggle'),
        ('loadNotifications', 'Notifications loader')
    ]
    
    all_exist = True
    
    for feature, description in features:
        if feature in content:
            print(f"✓ {description}: {feature}")
        else:
            print(f"✗ {description}: {feature} MISSING")
            all_exist = False
    
    return all_exist

# Check CSS responsive design
def test_responsive_css():
    print("\n" + "=" * 60)
    print("TESTING: Responsive Design in style.css")
    print("=" * 60)
    
    css_file = 'static/css/style.css'
    
    if not os.path.exists(css_file):
        print(f"✗ {css_file} not found")
        return False
    
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for media queries
    import re
    media_queries = re.findall(r'@media.*?\{', content)
    
    print(f"✓ Found {len(media_queries)} media queries for responsive design")
    
    # Check for important components
    components = [
        ('.navbar', 'Navigation bar'),
        ('.toast', 'Toast notifications'),
        ('.password-wrapper', 'Password field wrapper'),
        ('.modal', 'Modal dialogs'),
        ('.hero', 'Hero section'),
        ('.disease-card', 'Disease cards')
    ]
    
    all_exist = True
    
    for selector, description in components:
        if selector in content:
            print(f"✓ {description}: {selector}")
        else:
            print(f"✗ {description}: {selector} MISSING")
            all_exist = False
    
    return all_exist

# Main test runner
def run_all_tests():
    print("\n" + "=" * 60)
    print("CHILLI CARE - USER PAGES VERIFICATION TEST")
    print("=" * 60)
    
    results = {}
    
    results['Templates'] = test_templates()
    results['Static Resources'] = test_static_resources()
    results['Routes'] = test_routes()
    results['API Endpoints'] = test_api_endpoints()
    results['JavaScript Features'] = test_javascript_features()
    results['Responsive CSS'] = test_responsive_css()
    
    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n{passed}/{total} test categories passed")
    
    if passed == total:
        print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("All user-facing pages are properly configured!")
    else:
        print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("Please review the failures above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
