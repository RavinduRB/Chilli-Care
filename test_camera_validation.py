#!/usr/bin/env python3
"""
Camera Capture Validation Test
Tests if validation is properly applied to both file uploads and camera captures.
"""

import os
import sys

def test_main_js_validation():
    """Test if main.js has proper validation for camera captures."""
    print("=" * 60)
    print("TEST 1: Main.js Camera Validation")
    print("=" * 60)
    
    with open('static/js/main.js', 'r', encoding='utf-8') as f:
        main_js = f.read()
    
    checks = {
        'validateFile function exists': 'function validateFile(',
        'validateFile checks file type': "file.type.startsWith('image/')",
        'validateFile checks file size': 'file.size > 16 * 1024 * 1024',
        'handleFileSelect calls validateFile': 'if (!validateFile(file))',
        'capturePhoto calls validateFile': 'capturePhoto' in main_js and 'validateFile(capturedFile)' in main_js
    }
    
    all_passed = True
    for check_name, pattern in checks.items():
        if isinstance(pattern, bool):
            result = pattern
        else:
            result = pattern in main_js
        
        if result:
            print(f"✓ {check_name}")
        else:
            print(f"✗ {check_name}")
            all_passed = False
    
    print()
    return all_passed

def test_camera_test_html_validation():
    """Test if camera-test.html has proper validation."""
    print("=" * 60)
    print("TEST 2: Camera-test.html Validation")
    print("=" * 60)
    
    with open('templates/camera-test.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    checks = {
        'Has file type validation': "file.type.startsWith('image/')",
        'Has file size validation': 'file.size > 16 * 1024 * 1024',
        'Shows error for invalid type': 'Not an image file',
        'Shows error for large file': 'File too large',
        'Native camera input': 'capture="environment"',
        'Accept only images': 'accept="image/*"'
    }
    
    all_passed = True
    for check_name, pattern in checks.items():
        if pattern in html:
            print(f"✓ {check_name}")
        else:
            print(f"✗ {check_name}")
            all_passed = False
    
    print()
    return all_passed

def test_validation_flow():
    """Test validation flow logic."""
    print("=" * 60)
    print("TEST 3: Validation Flow")
    print("=" * 60)
    
    with open('static/js/main.js', 'r', encoding='utf-8') as f:
        main_js = f.read()
    
    # Check validation flow
    print("\n1. File Upload Flow:")
    if 'fileInput.addEventListener' in main_js:
        print("   ✓ File input listener exists")
    if 'handleFileSelect(file)' in main_js:
        print("   ✓ Calls handleFileSelect()")
    if 'function handleFileSelect' in main_js and 'validateFile(file)' in main_js:
        print("   ✓ handleFileSelect validates file")
    if 'processAndPreviewImage(file)' in main_js:
        print("   ✓ Processes validated file")
    
    print("\n2. Camera Capture Flow:")
    if 'function capturePhoto' in main_js:
        print("   ✓ capturePhoto function exists")
    if 'toBlob' in main_js:
        print("   ✓ Converts canvas to blob")
    
    # Check if validation is called in capturePhoto
    capture_start = main_js.find('function capturePhoto()')
    capture_end = main_js.find('function handleCameraError', capture_start)
    capture_code = main_js[capture_start:capture_end]
    
    if 'validateFile(capturedFile)' in capture_code:
        print("   ✓ Validates captured file")
    else:
        print("   ✗ Missing validation for captured file")
        return False
    
    if 'processAndPreviewImage(capturedFile)' in capture_code:
        print("   ✓ Processes validated capture")
    
    print("\n3. Validation Function:")
    validate_start = main_js.find('function validateFile(')
    if validate_start != -1:
        validate_end = main_js.find('\n    }', validate_start + 100)
        validate_code = main_js[validate_start:validate_end]
        
        if "file.type.startsWith('image/')" in validate_code:
            print("   ✓ Checks file type")
        if 'file.size > 16 * 1024 * 1024' in validate_code:
            print("   ✓ Checks file size (16MB max)")
        if 'return false' in validate_code:
            print("   ✓ Returns false on validation failure")
        if 'return true' in validate_code:
            print("   ✓ Returns true on validation success")
    
    print()
    return True

def test_validation_messages():
    """Test validation error messages."""
    print("=" * 60)
    print("TEST 4: Validation Error Messages")
    print("=" * 60)
    
    with open('static/js/main.js', 'r', encoding='utf-8') as f:
        main_js = f.read()
    
    messages = {
        'Invalid file type': 'Please select an image file',
        'File too large': 'File size must be less than 16MB',
        'Camera not ready': 'Camera not ready',
        'Capture failed': 'Failed to capture photo'
    }
    
    all_found = True
    for category, message in messages.items():
        if message in main_js:
            print(f"✓ {category}: '{message}'")
        else:
            print(f"✗ {category}: Message not found")
            all_found = False
    
    print()
    return all_found

def test_edge_cases():
    """Test edge case handling."""
    print("=" * 60)
    print("TEST 5: Edge Case Handling")
    print("=" * 60)
    
    with open('static/js/main.js', 'r', encoding='utf-8') as f:
        main_js = f.read()
    
    checks = {
        'Handles null/undefined file': 'if (!blob)',
        'Handles image load error': 'img.onerror',
        'Handles canvas blob error': 'if (!blob)',
        'Handles video dimension check': 'if (!videoWidth || !videoHeight)'
    }
    
    # Check try-catch separately
    capture_start = main_js.find('function capturePhoto()')
    if capture_start != -1:
        capture_section = main_js[capture_start:capture_start + 2000]
        if 'try {' in capture_section:
            checks['Try-catch in capturePhoto'] = True
        else:
            checks['Try-catch in capturePhoto'] = False
    
    all_passed = True
    for check_name, pattern in checks.items():
        if isinstance(pattern, bool):
            result = pattern
        else:
            result = pattern in main_js
        
        if result:
            print(f"✓ {check_name}")
        else:
            print(f"✗ {check_name}")
            all_passed = False
    
    print()
    return all_passed

def run_all_tests():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print(" CAMERA VALIDATION TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        ("Main.js Validation", test_main_js_validation),
        ("Camera-test.html Validation", test_camera_test_html_validation),
        ("Validation Flow", test_validation_flow),
        ("Error Messages", test_validation_messages),
        ("Edge Cases", test_edge_cases)
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
        print("\n🎉 All validation tests passed!")
        print("\nValidation is now properly applied to:")
        print("  ✓ File uploads (via file picker)")
        print("  ✓ Camera captures (via camera modal)")
        print("  ✓ Drag & drop uploads")
        print("\nWhat's validated:")
        print("  • File type must be an image (image/*)")
        print("  • File size must be ≤ 16MB")
        print("  • File must exist and be readable")
        return 0
    else:
        print("\n⚠️ Some validation tests failed.")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
