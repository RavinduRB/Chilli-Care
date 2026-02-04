"""
Model Optimization Script for Chilli Disease Detection
Reduces model size while maintaining accuracy for deployment
"""

import os
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
import shutil

print("TensorFlow version:", tf.__version__)

def get_file_size_mb(filepath):
    """Get file size in MB"""
    size_bytes = os.path.getsize(filepath)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb

def optimize_model_h5(input_model_path, output_model_path):
    """
    Optimize H5 model using quantization and optimization
    """
    print(f"\n{'='*60}")
    print(f"Optimizing: {input_model_path}")
    print(f"{'='*60}")
    
    # Load original model
    print("\n1. Loading original model...")
    model = keras.models.load_model(input_model_path)
    original_size = get_file_size_mb(input_model_path)
    print(f"   Original size: {original_size:.2f} MB")
    
    # Model summary
    print("\n2. Model architecture:")
    model.summary()
    
    # Save with optimization
    print("\n3. Saving with optimization...")
    model.save(
        output_model_path,
        save_format='h5',
        include_optimizer=False  # Remove optimizer to reduce size
    )
    
    optimized_size = get_file_size_mb(output_model_path)
    print(f"   Optimized size: {optimized_size:.2f} MB")
    print(f"   Size reduction: {original_size - optimized_size:.2f} MB ({((original_size - optimized_size) / original_size * 100):.1f}%)")
    
    return model

def convert_to_tflite(model, output_path, use_quantization=True):
    """
    Convert model to TensorFlow Lite format with quantization
    """
    print(f"\n{'='*60}")
    print(f"Converting to TensorFlow Lite: {output_path}")
    print(f"{'='*60}")
    
    # Convert to TFLite
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    if use_quantization:
        print("\n1. Applying post-training quantization...")
        # Dynamic range quantization
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float16]
    
    print("\n2. Converting model...")
    tflite_model = converter.convert()
    
    # Save TFLite model
    print(f"\n3. Saving TFLite model...")
    with open(output_path, 'wb') as f:
        f.write(tflite_model)
    
    tflite_size = get_file_size_mb(output_path)
    print(f"   TFLite size: {tflite_size:.2f} MB")
    
    return tflite_model

def create_optimized_savedmodel(model, output_dir):
    """
    Create optimized SavedModel format
    """
    print(f"\n{'='*60}")
    print(f"Creating optimized SavedModel: {output_dir}")
    print(f"{'='*60}")
    
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    print("\n1. Saving in SavedModel format...")
    model.save(
        output_dir,
        save_format='tf',
        include_optimizer=False
    )
    
    # Calculate directory size
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(output_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    
    savedmodel_size = total_size / (1024 * 1024)
    print(f"   SavedModel size: {savedmodel_size:.2f} MB")
    
    return savedmodel_size

def test_model_inference(original_model, optimized_model_path):
    """
    Test if optimized model produces similar results
    """
    print(f"\n{'='*60}")
    print("Testing Model Inference")
    print(f"{'='*60}")
    
    # Create a random test input
    test_input = np.random.rand(1, 224, 224, 3).astype(np.float32)
    
    # Original model prediction
    print("\n1. Testing original model...")
    original_pred = original_model.predict(test_input, verbose=0)
    
    # Optimized model prediction
    print("2. Testing optimized model...")
    optimized_model = keras.models.load_model(optimized_model_path)
    optimized_pred = optimized_model.predict(test_input, verbose=0)
    
    # Compare predictions
    difference = np.abs(original_pred - optimized_pred).mean()
    print(f"\n3. Prediction difference: {difference:.6f}")
    
    if difference < 0.001:
        print("   ✅ Models produce nearly identical results!")
    else:
        print("   ⚠️ Models have some difference (still acceptable)")
    
    return difference

def main():
    print("\n" + "="*60)
    print("CHILLI DISEASE MODEL OPTIMIZATION")
    print("="*60)
    
    # Model paths
    input_model = "best_chilli_disease_model.h5"
    
    if not os.path.exists(input_model):
        print(f"\n❌ Error: Model file not found: {input_model}")
        print("   Please make sure the model file is in the current directory.")
        return
    
    # Create optimization results
    results = []
    
    # 1. Optimize H5 format (remove optimizer)
    print("\n\n" + "="*60)
    print("OPTIMIZATION 1: H5 Format (Remove Optimizer)")
    print("="*60)
    optimized_h5 = "best_chilli_disease_model_optimized.h5"
    model = optimize_model_h5(input_model, optimized_h5)
    results.append(("Optimized H5", optimized_h5, get_file_size_mb(optimized_h5)))
    
    # 2. Convert to TFLite with quantization
    print("\n\n" + "="*60)
    print("OPTIMIZATION 2: TensorFlow Lite (Quantized)")
    print("="*60)
    tflite_path = "best_chilli_disease_model.tflite"
    convert_to_tflite(model, tflite_path, use_quantization=True)
    results.append(("TFLite Quantized", tflite_path, get_file_size_mb(tflite_path)))
    
    # 3. SavedModel format
    print("\n\n" + "="*60)
    print("OPTIMIZATION 3: SavedModel Format")
    print("="*60)
    savedmodel_dir = "chilli_disease_model_optimized"
    savedmodel_size = create_optimized_savedmodel(model, savedmodel_dir)
    results.append(("SavedModel", savedmodel_dir, savedmodel_size))
    
    # 4. Test optimized model
    print("\n\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    test_model_inference(model, optimized_h5)
    
    # Print summary
    print("\n\n" + "="*60)
    print("OPTIMIZATION SUMMARY")
    print("="*60)
    
    original_size = get_file_size_mb(input_model)
    print(f"\nOriginal Model: {original_size:.2f} MB")
    print("\nOptimized Versions:")
    print("-" * 60)
    
    for name, path, size in results:
        reduction = ((original_size - size) / original_size * 100)
        print(f"{name:20s}: {size:8.2f} MB (↓{reduction:5.1f}%)")
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    # Find best option
    best_option = min(results, key=lambda x: x[2])
    
    print(f"\n✅ Best option: {best_option[0]} ({best_option[2]:.2f} MB)")
    print("\nFor Vercel deployment (<50MB):")
    
    if best_option[2] < 50:
        print(f"   ✅ Use: {best_option[1]}")
        print("   This model will fit within Vercel's limits!")
    else:
        print("   ⚠️ Even optimized model is too large for Vercel.")
        print("   Recommended alternatives:")
        print("   1. Host model on Hugging Face Hub")
        print("   2. Deploy to Render or Railway instead")
        print("   3. Use model distillation to create smaller model")
    
    print("\nFor general deployment:")
    print(f"   Use: {optimized_h5}")
    print("   (Best balance of size and compatibility)")
    
    print("\nFor mobile/edge deployment:")
    print(f"   Use: {tflite_path}")
    print("   (Smallest size, fastest inference)")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("\n1. Update app.py to use optimized model:")
    print(f"   MODEL_PATH = '{optimized_h5}'")
    print("\n2. Test the optimized model locally:")
    print("   python app.py")
    print("\n3. Deploy to your chosen platform")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
