"""Quick test script to verify database connection"""
import os
from dotenv import load_dotenv

load_dotenv()

# Check if DATABASE_URL is set
DATABASE_URL = os.getenv('DATABASE_URL', '')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env file")
    exit(1)

print("✅ DATABASE_URL is configured")
print(f"   Host: {DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'unknown'}")

# Test database connection
try:
    from flask import Flask
    from models import db, Disease, Prediction
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Test query
        disease_count = Disease.query.count()
        prediction_count = Prediction.query.count()
        
        print(f"\n✅ Database connection successful!")
        print(f"   Diseases: {disease_count}")
        print(f"   Predictions: {prediction_count}")
        
        if disease_count > 0:
            print(f"\n📋 Diseases in database:")
            for disease in Disease.query.all():
                print(f"   • {disease.name} (Severity: {disease.severity})")
        
        print("\n🎉 Everything is working perfectly!")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
