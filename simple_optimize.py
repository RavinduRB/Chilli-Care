"""
Simple Model Optimization - Alternative Approach
Manually process model without full reload
"""

import os
import h5py
import json
import shutil

def get_file_size_mb(filepath):
    """Get file size in MB"""
    size_bytes = os.path.getsize(filepath)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb

def remove_optimizer_from_h5(input_path, output_path):
    """
    Remove optimizer weights from H5 file to reduce size
    """
    print(f"\nOptimizing: {input_path}")
    print("="*60)
    
    original_size = get_file_size_mb(input_path)
    print(f"Original size: {original_size:.2f} MB")
    
    # Copy file first
    shutil.copy2(input_path, output_path)
    
    # Open H5 file and remove optimizer
    with h5py.File(output_path, 'r+') as f:
        # Remove optimizer if it exists
        if 'optimizer_weights' in f:
            del f['optimizer_weights']
            print("✓ Removed optimizer_weights")
        
        if 'optimizer' in f:
            del f['optimizer']
            print("✓ Removed optimizer")
        
        # Check for training configuration
        if 'model_weights' in f:
            model_weights = f['model_weights']
            if 'training_config' in model_weights.attrs:
                del model_weights.attrs['training_config']
                print("✓ Removed training_config")
    
    optimized_size = get_file_size_mb(output_path)
    reduction = original_size - optimized_size
    percentage = (reduction / original_size * 100) if original_size > 0 else 0
    
    print(f"\nOptimized size: {optimized_size:.2f} MB")
    print(f"Size reduction: {reduction:.2f} MB ({percentage:.1f}%)")
    
    return optimized_size

def analyze_h5_structure(filepath):
    """
    Analyze H5 file structure to see what's taking up space
    """
    print(f"\nAnalyzing: {filepath}")
    print("="*60)
    
    total_size = 0
    components = {}
    
    def visit_func(name, obj):
        nonlocal total_size
        if isinstance(obj, h5py.Dataset):
            size = obj.size * obj.dtype.itemsize
            total_size += size
            components[name] = size / (1024 * 1024)  # MB
    
    with h5py.File(filepath, 'r') as f:
        f.visititems(visit_func)
    
    print(f"\nTotal data size: {total_size / (1024 * 1024):.2f} MB")
    print("\nLargest components:")
    
    sorted_components = sorted(components.items(), key=lambda x: x[1], reverse=True)
    for name, size in sorted_components[:10]:  # Top 10
        if size > 0.1:  # Only show if > 0.1 MB
            print(f"  {size:8.2f} MB - {name}")
    
    return components

def main():
    print("\n" + "="*60)
    print("SIMPLE MODEL OPTIMIZATION")
    print("="*60)
    
    # Model paths
    models = [
        ("best_chilli_disease_model.h5", "best_chilli_disease_model_optimized.h5"),
        ("chilli_disease_detection_model_final.h5", "chilli_disease_detection_model_final_optimized.h5")
    ]
    
    results = []
    
    for input_model, output_model in models:
        if not os.path.exists(input_model):
            print(f"\n⚠️ Skipping {input_model} (not found)")
            continue
        
        print("\n" + "="*60)
        print(f"Processing: {input_model}")
        print("="*60)
        
        # Analyze structure
        analyze_h5_structure(input_model)
        
        # Optimize
        print("\n" + "-"*60)
        optimized_size = remove_optimizer_from_h5(input_model, output_model)
        
        results.append({
            'original': input_model,
            'optimized': output_model,
            'original_size': get_file_size_mb(input_model),
            'optimized_size': optimized_size
        })
    
    # Summary
    print("\n\n" + "="*60)
    print("OPTIMIZATION SUMMARY")
    print("="*60)
    
    for result in results:
        print(f"\n{result['original']}:")
        print(f"  Original:  {result['original_size']:8.2f} MB")
        print(f"  Optimized: {result['optimized_size']:8.2f} MB")
        reduction = result['original_size'] - result['optimized_size']
        percentage = (reduction / result['original_size'] * 100) if result['original_size'] > 0 else 0
        print(f"  Saved:     {reduction:8.2f} MB ({percentage:.1f}%)")
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    # Find smallest optimized model
    if results:
        smallest = min(results, key=lambda x: x['optimized_size'])
        
        print(f"\n✅ Best model for deployment:")
        print(f"   {smallest['optimized']}")
        print(f"   Size: {smallest['optimized_size']:.2f} MB")
        
        if smallest['optimized_size'] < 50:
            print("\n   ✓ Fits within Vercel's 50MB limit!")
            print("   You can deploy directly to Vercel.")
        else:
            print(f"\n   ✗ Still too large for Vercel ({smallest['optimized_size']:.2f} MB > 50 MB)")
            print("\n   Alternatives:")
            print("   1. Deploy to Render/Railway (no size limits)")
            print("   2. Host model on Hugging Face Hub")
            print("   3. Use model compression (requires retraining)")
        
        print("\n   Next steps:")
        print(f"   1. Update app.py to use: {smallest['optimized']}")
        print("   2. Test locally: python app.py")
        print("   3. Deploy to your chosen platform")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        import h5py
        main()
    except ImportError:
        print("\n❌ Error: h5py not installed")
        print("\nInstall with: pip install h5py")
        print("Then run this script again")
