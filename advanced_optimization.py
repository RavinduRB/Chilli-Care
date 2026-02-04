"""
Advanced Model Optimization with Knowledge Distillation
Creates a smaller student model trained by the larger teacher model
"""

import os
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt

class ModelDistillation:
    """
    Create a smaller model through knowledge distillation
    """
    
    def __init__(self, teacher_model, input_shape=(224, 224, 3), num_classes=5):
        self.teacher_model = teacher_model
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.student_model = None
    
    def create_student_model(self, complexity='light'):
        """
        Create a smaller student model
        
        Args:
            complexity: 'ultra-light', 'light', 'medium'
        """
        print(f"\nCreating {complexity} student model...")
        
        if complexity == 'ultra-light':
            # Very small model for extreme size reduction
            base_model = keras.applications.MobileNetV3Small(
                input_shape=self.input_shape,
                include_top=False,
                weights='imagenet',
                pooling='avg'
            )
            dropout_rate = 0.3
            dense_units = 128
            
        elif complexity == 'light':
            # Small efficient model
            base_model = keras.applications.MobileNetV2(
                input_shape=self.input_shape,
                include_top=False,
                weights='imagenet',
                alpha=0.5,  # Width multiplier
                pooling='avg'
            )
            dropout_rate = 0.3
            dense_units = 256
            
        else:  # medium
            # Medium-sized model
            base_model = keras.applications.MobileNetV2(
                input_shape=self.input_shape,
                include_top=False,
                weights='imagenet',
                alpha=1.0,
                pooling='avg'
            )
            dropout_rate = 0.4
            dense_units = 512
        
        # Build student model
        inputs = keras.Input(shape=self.input_shape)
        x = base_model(inputs, training=False)
        x = layers.Dropout(dropout_rate)(x)
        x = layers.Dense(dense_units, activation='relu')(x)
        x = layers.Dropout(dropout_rate)(x)
        outputs = layers.Dense(self.num_classes, activation='softmax')(x)
        
        self.student_model = keras.Model(inputs, outputs)
        
        print(f"Student model created:")
        self.student_model.summary()
        
        return self.student_model
    
    def distillation_loss(self, temperature=3.0):
        """
        Custom loss function for knowledge distillation
        """
        def loss(y_true, y_pred, teacher_pred):
            # Student loss (regular categorical crossentropy)
            student_loss = keras.losses.categorical_crossentropy(y_true, y_pred)
            
            # Distillation loss (soft targets from teacher)
            teacher_soft = tf.nn.softmax(teacher_pred / temperature)
            student_soft = tf.nn.softmax(y_pred / temperature)
            distillation_loss = keras.losses.categorical_crossentropy(teacher_soft, student_soft)
            
            # Combined loss (weighted average)
            return 0.5 * student_loss + 0.5 * distillation_loss
        
        return loss
    
    def save_optimized_model(self, output_path, include_optimizer=False):
        """
        Save the student model in optimized format
        """
        print(f"\nSaving optimized student model to: {output_path}")
        
        self.student_model.save(
            output_path,
            save_format='h5',
            include_optimizer=include_optimizer
        )
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"Model size: {file_size:.2f} MB")
        
        return file_size

def create_lightweight_model_manual():
    """
    Manually create a very lightweight model from scratch
    """
    print("\nCreating ultra-lightweight custom model...")
    
    model = keras.Sequential([
        # Input layer
        layers.Input(shape=(224, 224, 3)),
        
        # First conv block
        layers.Conv2D(32, 3, strides=2, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),
        
        # Second conv block
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),
        
        # Third conv block
        layers.Conv2D(128, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),
        
        # Fourth conv block
        layers.Conv2D(256, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.GlobalAveragePooling2D(),
        
        # Dense layers
        layers.Dropout(0.3),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(5, activation='softmax')
    ])
    
    print("Custom lightweight model created:")
    model.summary()
    
    return model

def main():
    print("\n" + "="*60)
    print("ADVANCED MODEL OPTIMIZATION")
    print("Knowledge Distillation & Lightweight Architectures")
    print("="*60)
    
    # Load teacher model
    teacher_path = "best_chilli_disease_model.h5"
    
    if not os.path.exists(teacher_path):
        print(f"\n❌ Error: Model file not found: {teacher_path}")
        return
    
    print(f"\nLoading teacher model: {teacher_path}")
    teacher_model = keras.models.load_model(teacher_path)
    teacher_size = os.path.getsize(teacher_path) / (1024 * 1024)
    print(f"Teacher model size: {teacher_size:.2f} MB")
    
    # Load class names
    with open('class_names.json', 'r') as f:
        class_names = json.load(f)
    num_classes = len(class_names)
    print(f"Number of classes: {num_classes}")
    
    # Create distillation object
    distiller = ModelDistillation(teacher_model, num_classes=num_classes)
    
    # Option 1: Ultra-light student
    print("\n" + "="*60)
    print("OPTION 1: Ultra-Light Student Model")
    print("="*60)
    student_ultra = distiller.create_student_model(complexity='ultra-light')
    size_ultra = distiller.save_optimized_model('student_model_ultra_light.h5')
    
    # Option 2: Light student
    print("\n" + "="*60)
    print("OPTION 2: Light Student Model")
    print("="*60)
    distiller.student_model = None
    student_light = distiller.create_student_model(complexity='light')
    size_light = distiller.save_optimized_model('student_model_light.h5')
    
    # Option 3: Medium student
    print("\n" + "="*60)
    print("OPTION 3: Medium Student Model")
    print("="*60)
    distiller.student_model = None
    student_medium = distiller.create_student_model(complexity='medium')
    size_medium = distiller.save_optimized_model('student_model_medium.h5')
    
    # Option 4: Custom lightweight
    print("\n" + "="*60)
    print("OPTION 4: Custom Ultra-Lightweight Model")
    print("="*60)
    custom_model = create_lightweight_model_manual()
    custom_model.save('custom_lightweight_model.h5', include_optimizer=False)
    size_custom = os.path.getsize('custom_lightweight_model.h5') / (1024 * 1024)
    print(f"Custom model size: {size_custom:.2f} MB")
    
    # Summary
    print("\n" + "="*60)
    print("SIZE COMPARISON SUMMARY")
    print("="*60)
    print(f"\nOriginal Teacher Model:  {teacher_size:8.2f} MB (100%)")
    print(f"Ultra-Light Student:     {size_ultra:8.2f} MB ({size_ultra/teacher_size*100:5.1f}%)")
    print(f"Light Student:           {size_light:8.2f} MB ({size_light/teacher_size*100:5.1f}%)")
    print(f"Medium Student:          {size_medium:8.2f} MB ({size_medium/teacher_size*100:5.1f}%)")
    print(f"Custom Lightweight:      {size_custom:8.2f} MB ({size_custom/teacher_size*100:5.1f}%)")
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    print("\n⚠️ IMPORTANT: These models need to be trained/fine-tuned!")
    print("\nThese are architecture-only models. To use them:")
    print("\n1. Train from scratch with your dataset:")
    print("   - Requires training data (train/ folder)")
    print("   - Takes time but gives best results")
    
    print("\n2. Use knowledge distillation:")
    print("   - Train student using teacher's predictions")
    print("   - Faster than training from scratch")
    print("   - Better performance than random initialization")
    
    print("\n3. For immediate deployment:")
    print("   - Use the basic optimization script (optimize_model.py)")
    print("   - Reduces size without retraining")
    
    print("\nBest approach for your use case:")
    if teacher_size > 100:
        print("   → Try ultra-light or light student model")
        print("   → Expected size: 10-30 MB after training")
    else:
        print("   → Use basic optimization (optimize_model.py)")
        print("   → Should fit Vercel limits")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
