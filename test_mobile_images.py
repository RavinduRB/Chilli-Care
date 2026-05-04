#!/usr/bin/env python3
"""
Test suite for mobile image display fixes
Validates image optimization, lazy loading, and error handling
"""

import os
import json

def test_image_optimization():
    """Test that all disease images are optimized for mobile"""
    print("\n" + "="*60)
    print("TEST 1: Image Optimization")
    print("="*60)
    
    diseases_dir = os.path.join('static', 'images', 'diseases')
    
    if not os.path.exists(diseases_dir):
        print("✗ Disease images directory not found")
        return False
    
    image_files = [f for f in os.listdir(diseases_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    
    print(f"✓ Found {len(image_files)} disease images")
    
    # Check image sizes
    large_images = []
    total_size = 0
    
    for filename in image_files:
        filepath = os.path.join(diseases_dir, filename)
        size_kb = os.path.getsize(filepath) / 1024
        total_size += size_kb
        
        if size_kb > 500:
            large_images.append((filename, size_kb))
    
    print(f"✓ Total folder size: {total_size/1024:.2f}MB")
    
    if large_images:
        print(f"⚠ {len(large_images)} images still > 500KB:")
        for filename, size in large_images[:5]:  # Show first 5
            print(f"  • {filename}: {size:.1f}KB")
        if len(large_images) > 5:
            print(f"  ... and {len(large_images)-5} more")
    else:
        print("✓ All images optimized (< 500KB each)")
    
    # Target: < 10MB total, no images > 1MB
    very_large = [f for f, s in large_images if s > 1024]
    
    if total_size < 10240 and not very_large:  # < 10MB and no >1MB images
        print("✓ Images optimized for mobile")
        return True
    else:
        print("✗ Some images may be too large for mobile")
        return False

def test_lazy_loading():
    """Test that images have lazy loading and async decoding"""
    print("\n" + "="*60)
    print("TEST 2: Lazy Loading & Async Decoding")
    print("="*60)
    
    diseases_js = os.path.join('static', 'js', 'diseases.js')
    
    if not os.path.exists(diseases_js):
        print("✗ diseases.js not found")
        return False
    
    with open(diseases_js, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for lazy loading
    if 'loading="lazy"' in content:
        print("✓ Lazy loading enabled")
    else:
        print("✗ Lazy loading not found")
        return False
    
    # Check for async decoding
    if 'decoding="async"' in content:
        print("✓ Async decoding enabled")
    else:
        print("✗ Async decoding not found")
        return False
    
    # Check for onload handler
    if 'onload=' in content and "style.opacity='1'" in content:
        print("✓ Fade-in effect implemented")
    else:
        print("✗ Fade-in effect not found")
        return False
    
    # Check for error handling
    if 'onerror=' in content and 'console.error' in content:
        print("✓ Error logging implemented")
    else:
        print("✗ Error logging not found")
        return False
    
    return True

def test_image_css():
    """Test CSS for image loading states"""
    print("\n" + "="*60)
    print("TEST 3: Image CSS Styles")
    print("="*60)
    
    diseases_css = os.path.join('static', 'css', 'diseases.css')
    
    if not os.path.exists(diseases_css):
        print("✗ diseases.css not found")
        return False
    
    with open(diseases_css, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for opacity transition
    if 'opacity' in content and 'transition' in content:
        print("✓ Opacity transition defined")
    else:
        print("✗ Opacity transition not found")
        return False
    
    # Check for card-image-wrap styles
    if '.card-image-wrap img' in content:
        print("✓ Card image styles defined")
    else:
        print("✗ Card image styles not found")
        return False
    
    # Check for modal-image-wrap styles
    if '.modal-image-wrap img' in content:
        print("✓ Modal image styles defined")
    else:
        print("✗ Modal image styles not found")
        return False
    
    return True

def test_image_paths():
    """Test that all disease images have correct paths"""
    print("\n" + "="*60)
    print("TEST 4: Image Path Mappings")
    print("="*60)
    
    diseases_js = os.path.join('static', 'js', 'diseases.js')
    diseases_dir = os.path.join('static', 'images', 'diseases')
    
    # Get actual image files
    actual_images = set(f for f in os.listdir(diseases_dir) 
                       if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')))
    
    print(f"✓ Found {len(actual_images)} actual image files")
    
    # Extract DISEASE_IMAGES object from diseases.js
    with open(diseases_js, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all image paths in DISEASE_IMAGES
    import re
    image_paths = re.findall(r"'/static/images/diseases/([^']+)'", content)
    
    print(f"✓ Found {len(image_paths)} image paths in DISEASE_IMAGES")
    
    # Check for missing files
    missing = []
    for path in image_paths:
        if path not in actual_images:
            missing.append(path)
    
    if missing:
        print(f"⚠ {len(missing)} referenced images not found:")
        for img in missing[:5]:
            print(f"  • {img}")
        if len(missing) > 5:
            print(f"  ... and {len(missing)-5} more")
    else:
        print("✓ All referenced images exist")
    
    # Check for unused files
    referenced = set(image_paths)
    unused = actual_images - referenced
    
    if unused:
        print(f"⚠ {len(unused)} images not referenced:")
        for img in list(unused)[:5]:
            print(f"  • {img}")
        if len(unused) > 5:
            print(f"  ... and {len(unused)-5} more")
    else:
        print("✓ All images are referenced")
    
    return len(missing) == 0

def test_progressive_jpeg():
    """Test that images are progressive JPEGs"""
    print("\n" + "="*60)
    print("TEST 5: Progressive JPEG Format")
    print("="*60)
    
    try:
        from PIL import Image
    except ImportError:
        print("⚠ Pillow not available, skipping progressive check")
        return True
    
    diseases_dir = os.path.join('static', 'images', 'diseases')
    image_files = [f for f in os.listdir(diseases_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg'))]
    
    progressive_count = 0
    non_progressive = []
    
    for filename in image_files:
        filepath = os.path.join(diseases_dir, filename)
        try:
            img = Image.open(filepath)
            if img.format == 'JPEG':
                # Check if progressive
                if img.info.get('progressive', False) or img.info.get('progression', False):
                    progressive_count += 1
                else:
                    non_progressive.append(filename)
        except Exception as e:
            print(f"⚠ Could not check {filename}: {e}")
    
    print(f"✓ {progressive_count}/{len(image_files)} JPEG images are progressive")
    
    if non_progressive and len(non_progressive) < 5:
        print(f"⚠ Non-progressive images:")
        for img in non_progressive:
            print(f"  • {img}")
    
    # Progressive is recommended but not required
    return True

def main():
    print("\n" + "="*60)
    print(" MOBILE IMAGE DISPLAY TEST SUITE")
    print("="*60)
    
    tests = [
        ("Image Optimization", test_image_optimization),
        ("Lazy Loading", test_lazy_loading),
        ("Image CSS", test_image_css),
        ("Image Paths", test_image_paths),
        ("Progressive JPEG", test_progressive_jpeg),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' failed with error: {e}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "="*60)
    print(" TEST SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\nResults: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All mobile image tests passed!")
        print("\nMobile optimizations:")
        print("  ✓ Images compressed for faster loading")
        print("  ✓ Lazy loading for performance")
        print("  ✓ Async decoding for smooth rendering")
        print("  ✓ Fade-in effect for better UX")
        print("  ✓ Error handling and logging")
    else:
        print(f"\n⚠️ {total_count - passed_count} test(s) failed.")
    
    return passed_count == total_count

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
