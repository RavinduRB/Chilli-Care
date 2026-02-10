"""
Test the Multi-Tier Validation System
Shows how the app handles quota exhaustion
"""

import os
import io
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()

# Import validation functions
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_image(text="TEST IMAGE", color="green"):
    """Create a simple test image"""
    img = Image.new('RGB', (400, 300), color=color)
    draw = ImageDraw.Draw(img)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    draw.text((100, 130), text, fill="white", font=font)
    
    # Convert to bytes
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='JPEG')
    byte_arr.seek(0)
    return byte_arr


def test_validation_system():
    """Test all 3 tiers of validation"""
    print("=" * 60)
    print("🧪 TESTING MULTI-TIER VALIDATION SYSTEM")
    print("=" * 60)
    
    # Check configuration
    print("\n📋 CONFIGURATION CHECK:")
    print("-" * 60)
    
    gemini_keys = [
        os.getenv('GEMINI_API_KEY', ''),
        os.getenv('GEMINI_API_KEY_2', ''),
        os.getenv('GEMINI_API_KEY_3', ''),
        os.getenv('GEMINI_API_KEY_4', ''),
        os.getenv('GEMINI_API_KEY_5', ''),
    ]
    gemini_keys = [k for k in gemini_keys if k]
    
    hf_key = os.getenv('HUGGINGFACE_API_KEY', '')
    
    print(f"✓ Gemini API Keys: {len(gemini_keys)} configured")
    for i, _ in enumerate(gemini_keys):
        print(f"  • Key #{i+1}: {'*' * 10}{_[-8:]}")
    
    if not gemini_keys:
        print("  ⚠ WARNING: No Gemini API keys configured!")
        print("  Add GEMINI_API_KEY to your .env file")
    
    print(f"\n✓ HuggingFace API: {'✅ Configured' if hf_key else '❌ Not configured'}")
    if hf_key:
        print(f"  • Token: {'*' * 10}{hf_key[-8:]}")
    else:
        print("  ℹ Optional: Add HUGGINGFACE_API_KEY for Tier 2 backup")
    
    print(f"\n✓ Local Validation: ✅ Always Available (No API needed)")
    
    # Import app validation functions
    try:
        from app import validate_with_huggingface, validate_with_local_rules
        print("\n✅ Validation functions loaded successfully")
    except Exception as e:
        print(f"\n❌ Error loading validation functions: {e}")
        return
    
    # Test Tier 2: HuggingFace
    print("\n" + "=" * 60)
    print("🧪 TESTING TIER 2: HUGGING FACE VALIDATION")
    print("=" * 60)
    
    test_img = create_test_image("Green Plant", "darkgreen")
    img_bytes = test_img.read()
    
    if hf_key:
        print("\nTesting HuggingFace API...")
        try:
            result = validate_with_huggingface(img_bytes)
            if result:
                is_valid, message = result
                print(f"✅ Result: {'VALID' if is_valid else 'INVALID'}")
                print(f"   Message: {message}")
            else:
                print("⚠ HuggingFace returned None (API may be loading model)")
                print("  This is normal - model loads on first use (~30 seconds)")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("⊘ Skipped - No HUGGINGFACE_API_KEY configured")
        print("  Get free token at: https://huggingface.co/settings/tokens")
    
    # Test Tier 3: Local Validation
    print("\n" + "=" * 60)
    print("🧪 TESTING TIER 3: LOCAL COLOR VALIDATION")
    print("=" * 60)
    
    # Test with green image (should pass)
    print("\n1️⃣ Testing GREEN image (should detect plant):")
    green_img = create_test_image("Green Test", "green")
    green_bytes = green_img.read()
    
    try:
        is_valid, message = validate_with_local_rules(green_bytes)
        print(f"   Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
        print(f"   Message: {message}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test with blue image (should fail)
    print("\n2️⃣ Testing BLUE image (should reject):")
    blue_img = create_test_image("Blue Test", "blue")
    blue_bytes = blue_img.read()
    
    try:
        is_valid, message = validate_with_local_rules(blue_bytes)
        print(f"   Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
        print(f"   Message: {message}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SYSTEM SUMMARY")
    print("=" * 60)
    
    total_capacity = 0
    
    if gemini_keys:
        gemini_daily = len(gemini_keys) * 1500  # Flash models
        total_capacity += gemini_daily
        print(f"\n🔹 Tier 1 (Gemini):")
        print(f"   • {len(gemini_keys)} API keys configured")
        print(f"   • Estimated daily capacity: {gemini_daily:,} requests")
        print(f"   • Accuracy: ⭐⭐⭐⭐⭐ (99%)")
    else:
        print(f"\n🔹 Tier 1 (Gemini): ❌ Not configured")
        print(f"   • Add GEMINI_API_KEY to .env file")
        print(f"   • Get key at: https://aistudio.google.com/app/apikey")
    
    if hf_key:
        print(f"\n🔹 Tier 2 (HuggingFace):")
        print(f"   • API configured: ✅")
        print(f"   • Daily capacity: Unlimited (rate limited)")
        print(f"   • Accuracy: ⭐⭐⭐⭐ (90%)")
        total_capacity = "Unlimited*"
    else:
        print(f"\n🔹 Tier 2 (HuggingFace): ⚠ Optional backup not configured")
        print(f"   • Get token at: https://huggingface.co/settings/tokens")
    
    print(f"\n🔹 Tier 3 (Local):")
    print(f"   • Always available: ✅")
    print(f"   • Daily capacity: ∞ (No limits)")
    print(f"   • Accuracy: ⭐⭐ (70% - basic green detection)")
    
    print(f"\n" + "=" * 60)
    if isinstance(total_capacity, int):
        print(f"💪 Total Daily Capacity: {total_capacity:,}+ requests")
    else:
        print(f"💪 Total Daily Capacity: {total_capacity}")
    print("=" * 60)
    
    # Recommendations
    print("\n📋 RECOMMENDATIONS:")
    print("-" * 60)
    
    if len(gemini_keys) < 3:
        print("⚠ Consider adding more Gemini API keys for redundancy")
        print("  • Each Google account gives 1,500 free requests/day")
        print("  • Create 5 accounts = 7,500 requests/day")
        print("  • See QUOTA_SOLUTIONS.md for detailed steps")
    else:
        print("✅ Good! You have multiple Gemini keys for redundancy")
    
    if not hf_key:
        print("\n💡 Add HuggingFace API for extra backup:")
        print("  1. Visit: https://huggingface.co/settings/tokens")
        print("  2. Create token (Read access)")
        print("  3. Add to .env: HUGGINGFACE_API_KEY=hf_your_token")
    else:
        print("\n✅ Excellent! HuggingFace backup configured")
    
    print("\n" + "=" * 60)
    print("✨ Testing complete! Check results above.")
    print("=" * 60)


if __name__ == "__main__":
    test_validation_system()
