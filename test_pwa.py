#!/usr/bin/env python3
"""
PWA Implementation Test Script
Tests Progressive Web App functionality including service worker,
manifest, offline page, and caching strategies.
"""

import os
import json
import sys

def test_pwa_files_exist():
    """Test if all required PWA files exist."""
    print("=" * 60)
    print("TEST 1: PWA Files Existence")
    print("=" * 60)
    
    required_files = {
        'Service Worker': 'static/sw.js',
        'PWA Manifest': 'static/manifest.json',
        'Offline Page': 'static/offline.html',
        'PWA Script': 'static/js/pwa.js',
        'PWA Styles': 'static/css/pwa.css'
    }
    
    all_exist = True
    for name, path in required_files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✓ {name}: {path} ({size:,} bytes)")
        else:
            print(f"✗ {name}: {path} - NOT FOUND")
            all_exist = False
    
    print()
    return all_exist

def test_manifest_structure():
    """Test manifest.json structure and content."""
    print("=" * 60)
    print("TEST 2: Manifest Structure")
    print("=" * 60)
    
    try:
        with open('static/manifest.json', 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        required_fields = {
            'name': str,
            'short_name': str,
            'description': str,
            'start_url': str,
            'display': str,
            'theme_color': str,
            'background_color': str,
            'icons': list,
            'shortcuts': list
        }
        
        all_valid = True
        for field, expected_type in required_fields.items():
            if field in manifest:
                if isinstance(manifest[field], expected_type):
                    value = manifest[field]
                    if isinstance(value, (list, dict)):
                        count = len(value)
                        print(f"✓ {field}: {expected_type.__name__} ({count} items)")
                    elif isinstance(value, str) and len(value) < 60:
                        print(f"✓ {field}: \"{value}\"")
                    else:
                        print(f"✓ {field}: {expected_type.__name__}")
                else:
                    print(f"✗ {field}: Wrong type (expected {expected_type.__name__})")
                    all_valid = False
            else:
                print(f"✗ {field}: Missing")
                all_valid = False
        
        # Check icons
        if 'icons' in manifest:
            print(f"\nIcon Sizes:")
            for icon in manifest['icons']:
                print(f"  - {icon.get('sizes', 'unknown')}: {icon.get('src', 'no src')}")
        
        # Check shortcuts
        if 'shortcuts' in manifest:
            print(f"\nApp Shortcuts:")
            for shortcut in manifest['shortcuts']:
                print(f"  - {shortcut.get('name', 'unnamed')}: {shortcut.get('url', 'no url')}")
        
        print()
        return all_valid
    
    except Exception as e:
        print(f"✗ Error reading manifest: {e}\n")
        return False

def test_service_worker_structure():
    """Test service worker file structure."""
    print("=" * 60)
    print("TEST 3: Service Worker Structure")
    print("=" * 60)
    
    try:
        with open('static/sw.js', 'r', encoding='utf-8') as f:
            sw_content = f.read()
        
        required_patterns = {
            'CACHE_NAME': "Cache name constant",
            "addEventListener('install'": "Installation handler",
            "addEventListener('activate'": "Activation handler",
            "addEventListener('fetch'": "Fetch handler",
            'caches.open': "Cache API usage",
            'cacheFirstStrategy': "Cache-first strategy",
            'networkFirstStrategy': "Network-first strategy",
            'staleWhileRevalidate': "Stale-while-revalidate strategy"
        }
        
        all_found = True
        for pattern, description in required_patterns.items():
            if pattern in sw_content:
                print(f"✓ {description}: Found")
            else:
                print(f"✗ {description}: Not found (searching for '{pattern}')")
                all_found = False
        
        # Count cached resources
        app_shell_count = sw_content.count('.css') + sw_content.count('.js') + sw_content.count('.html')
        image_count = sw_content.count('.png') + sw_content.count('.jpg') + sw_content.count('.svg')
        
        print(f"\nResource Count:")
        print(f"  - Static files (approx): {app_shell_count}")
        print(f"  - Images (approx): {image_count}")
        
        print()
        return all_found
    
    except Exception as e:
        print(f"✗ Error reading service worker: {e}\n")
        return False

def test_template_integration():
    """Test if PWA is integrated into HTML templates."""
    print("=" * 60)
    print("TEST 4: Template Integration")
    print("=" * 60)
    
    templates = {
        'User Pages': 'templates/base.html',
        'Admin Pages': 'templates/admin_base.html'
    }
    
    all_integrated = True
    for name, template_path in templates.items():
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            checks = {
                'manifest.json': 'Manifest link',
                'theme-color': 'Theme color meta tag',
                'apple-touch-icon': 'Apple touch icon',
                'pwa.js': 'PWA script',
                'pwa.css': 'PWA styles'
            }
            
            print(f"\n{name} ({template_path}):")
            template_ok = True
            for pattern, description in checks.items():
                if pattern in content:
                    print(f"  ✓ {description}")
                else:
                    print(f"  ✗ {description}: Not found")
                    template_ok = False
            
            if not template_ok:
                all_integrated = False
        
        except Exception as e:
            print(f"  ✗ Error reading template: {e}")
            all_integrated = False
    
    print()
    return all_integrated

def test_offline_page():
    """Test offline fallback page."""
    print("=" * 60)
    print("TEST 5: Offline Page")
    print("=" * 60)
    
    try:
        with open('static/offline.html', 'r', encoding='utf-8') as f:
            offline_content = f.read()
        
        required_elements = {
            '<title>': 'Page title',
            'offline': 'Offline messaging',
            'retry': 'Retry functionality',
            'network': 'Network status',
            'addEventListener': 'Event handlers'
        }
        
        all_found = True
        for pattern, description in required_elements.items():
            # Don't convert to lowercase for addEventListener check
            if pattern == 'addEventListener':
                if pattern in offline_content:
                    print(f"✓ {description}: Present")
                else:
                    print(f"✗ {description}: Not found")
                    all_found = False
            else:
                if pattern in offline_content.lower():
                    print(f"✓ {description}: Present")
                else:
                    print(f"✗ {description}: Not found")
                    all_found = False
        
        print()
        return all_found
    
    except Exception as e:
        print(f"✗ Error reading offline page: {e}\n")
        return False

def test_image_files():
    """Test if image files exist."""
    print("=" * 60)
    print("TEST 6: Image Files")
    print("=" * 60)
    
    images_dir = 'static/images'
    if not os.path.exists(images_dir):
        print(f"✗ Images directory not found: {images_dir}\n")
        return False
    
    # Count images
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')
    
    main_images = []
    disease_images = []
    
    # Main images folder
    for item in os.listdir(images_dir):
        item_path = os.path.join(images_dir, item)
        if os.path.isfile(item_path) and item.lower().endswith(image_extensions):
            main_images.append(item)
    
    # Disease images subfolder
    diseases_dir = os.path.join(images_dir, 'diseases')
    if os.path.exists(diseases_dir):
        for item in os.listdir(diseases_dir):
            item_path = os.path.join(diseases_dir, item)
            if os.path.isfile(item_path) and item.lower().endswith(image_extensions):
                disease_images.append(item)
    
    print(f"Main Images ({len(main_images)}):")
    for img in sorted(main_images):
        size = os.path.getsize(os.path.join(images_dir, img))
        print(f"  - {img} ({size:,} bytes)")
    
    print(f"\nDisease Detail Images ({len(disease_images)}):")
    for img in sorted(disease_images)[:5]:  # Show first 5
        size = os.path.getsize(os.path.join(diseases_dir, img))
        print(f"  - {img} ({size:,} bytes)")
    
    if len(disease_images) > 5:
        print(f"  ... and {len(disease_images) - 5} more")
    
    total_images = len(main_images) + len(disease_images)
    print(f"\n✓ Total images found: {total_images}")
    print()
    return True

def test_pwa_features():
    """Test PWA features in pwa.js."""
    print("=" * 60)
    print("TEST 7: PWA Features")
    print("=" * 60)
    
    try:
        with open('static/js/pwa.js', 'r', encoding='utf-8') as f:
            pwa_content = f.read()
        
        features = {
            'serviceWorker.register': 'Service Worker registration',
            'beforeinstallprompt': 'Install prompt handler',
            'showInstallButton': 'Install button UI',
            'showUpdateNotification': 'Update notifications',
            'addEventListener(\'online\'': 'Online detection',
            'addEventListener(\'offline\'': 'Offline detection',
            'cacheImportantUrls': 'Manual cache function',
            'clearPWACache': 'Cache clearing utility',
            'isPWAInstalled': 'Installation detection'
        }
        
        all_found = True
        for pattern, description in features.items():
            if pattern in pwa_content:
                print(f"✓ {description}")
            else:
                print(f"✗ {description}: Not found")
                all_found = False
        
        print()
        return all_found
    
    except Exception as e:
        print(f"✗ Error reading pwa.js: {e}\n")
        return False

def run_all_tests():
    """Run all PWA tests."""
    print("\n" + "=" * 60)
    print(" PWA IMPLEMENTATION TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        ("Files Existence", test_pwa_files_exist),
        ("Manifest Structure", test_manifest_structure),
        ("Service Worker", test_service_worker_structure),
        ("Template Integration", test_template_integration),
        ("Offline Page", test_offline_page),
        ("Image Files", test_image_files),
        ("PWA Features", test_pwa_features)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test '{test_name}' failed with error: {e}\n")
            results.append((test_name, False))
    
    # Summary
    print("=" * 60)
    print(" TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! PWA implementation is complete.")
        print("\nNext steps:")
        print("1. Start the Flask app: python app.py")
        print("2. Open browser and navigate to your app")
        print("3. Check browser DevTools > Application > Service Workers")
        print("4. Test offline mode by disabling network in DevTools")
        print("5. Look for the 'Install App' button")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
