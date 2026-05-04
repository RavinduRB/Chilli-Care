#!/usr/bin/env python3
"""
Optimize disease images for mobile devices
Compresses large images while maintaining quality
Target: < 500KB per image, max 1200px width
"""

import os
from PIL import Image
import sys

def optimize_image(image_path, max_width=1200, quality=85, max_size_kb=500):
    """
    Optimize an image for web/mobile display
    
    Args:
        image_path: Path to the image file
        max_width: Maximum width in pixels (default 1200)
        quality: JPEG quality 1-100 (default 85)
        max_size_kb: Target max file size in KB (default 500)
    """
    try:
        # Open the image
        img = Image.open(image_path)
        
        # Get original size
        original_size = os.path.getsize(image_path) / 1024  # KB
        original_dims = img.size
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        
        # Resize if image is too wide
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Save with progressive JPEG and optimization
        # Try different quality levels to meet size target
        temp_path = image_path + '.tmp'
        current_quality = quality
        
        while current_quality > 50:
            img.save(temp_path, 'JPEG', 
                    quality=current_quality, 
                    optimize=True, 
                    progressive=True)
            
            temp_size = os.path.getsize(temp_path) / 1024  # KB
            
            # If size is acceptable, replace original
            if temp_size <= max_size_kb or current_quality <= 60:
                os.replace(temp_path, image_path)
                new_size = os.path.getsize(image_path) / 1024
                
                print(f"✓ {os.path.basename(image_path)}")
                print(f"  {original_dims[0]}x{original_dims[1]} → {img.width}x{img.height}")
                print(f"  {original_size:.1f}KB → {new_size:.1f}KB ({(1-new_size/original_size)*100:.1f}% reduction)")
                print(f"  Quality: {current_quality}")
                return True
            
            # Reduce quality and try again
            current_quality -= 5
        
        # Clean up temp file if it exists
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return False
        
    except Exception as e:
        print(f"✗ Error optimizing {os.path.basename(image_path)}: {e}")
        return False

def main():
    diseases_dir = os.path.join('static', 'images', 'diseases')
    
    if not os.path.exists(diseases_dir):
        print(f"Error: Directory not found: {diseases_dir}")
        sys.exit(1)
    
    print("🔍 Scanning disease images...")
    print("=" * 60)
    
    # Get all image files
    image_files = [f for f in os.listdir(diseases_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    
    if not image_files:
        print("No image files found!")
        sys.exit(1)
    
    print(f"Found {len(image_files)} images\n")
    
    # Check which images need optimization
    large_images = []
    for filename in image_files:
        filepath = os.path.join(diseases_dir, filename)
        size_kb = os.path.getsize(filepath) / 1024
        if size_kb > 500:
            large_images.append((filename, size_kb))
    
    if not large_images:
        print("✓ All images are already optimized (< 500KB)")
        return
    
    print(f"⚠ Found {len(large_images)} images > 500KB:")
    for filename, size in large_images:
        print(f"  • {filename}: {size:.1f}KB")
    print()
    
    # Ask for confirmation
    response = input("Optimize these images? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    print("\n🔧 Optimizing images...")
    print("=" * 60)
    
    success_count = 0
    for filename, _ in large_images:
        filepath = os.path.join(diseases_dir, filename)
        if optimize_image(filepath):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"✓ Optimized {success_count}/{len(large_images)} images successfully")
    
    # Show final statistics
    total_size = sum(os.path.getsize(os.path.join(diseases_dir, f)) / 1024 
                     for f in image_files)
    print(f"\n📊 Total images folder size: {total_size/1024:.2f}MB")

if __name__ == '__main__':
    main()
