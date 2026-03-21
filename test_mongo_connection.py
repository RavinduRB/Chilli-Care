import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
uri = os.getenv('MONGODB_URI')
print(f'URI exists: {bool(uri)}')

if uri:
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client.get_default_database()
        print(f'✓ MongoDB connection works!')
        print(f'Database: {db.name}')
        
        # Check admin user
        admin = db.users.find_one({'email': 'admin@chillicare.com'})
        print(f'Admin exists: {admin is not None}')
        if admin:
            print(f'Admin type: {admin.get("user_type")}')
    except Exception as e:
        print(f'✗ Connection failed: {e}')
else:
    print('✗ MONGODB_URI not set')
