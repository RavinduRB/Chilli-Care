"""
MongoDB Database Module for Chilli Disease Detection System
Handles connections, collections, and database operations
"""

import os
import ssl
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure
import logging
import certifi

# OpenSSL 3.x compatibility workaround for Windows
os.environ['OPENSSL_CONF'] = ''  # Disable OpenSSL config
os.environ['SSL_CERT_FILE'] = certifi.where()

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection and operations manager"""
    
    def __init__(self, connection_uri=None):
        """
        Initialize MongoDB connection
        
        Args:
            connection_uri: MongoDB connection string (defaults to env variable)
        """
        self.connection_uri = connection_uri or os.getenv('MONGODB_URI', '')
        self.client = None
        self.db = None
        self.connected = False
        
        if self.connection_uri:
            self.connect()
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            # PyMongo 4.x connection parameters with TLS workaround for Windows
            connection_params = {
                'serverSelectionTimeoutMS': 15000,
                'connectTimeoutMS': 30000,
                'maxPoolSize': 50,
                'tls': True,
                'tlsInsecure': True  # Bypasses all TLS verification (Windows OpenSSL 3.x workaround)
            }
            
            # Try to connect
            self.client = MongoClient(
                self.connection_uri,
                **connection_params
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database name from URI or use default
            try:
                self.db = self.client.get_database()
            except Exception:
                # No database specified in URI, use default
                logger.warning("No database in URI, using default: chilli_care")
                self.db = self.client['chilli_care']
            
            self.connected = True
            logger.info("✓ Connected to MongoDB successfully")
            
            # Create indexes
            self._create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.connected = False
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            self.connected = False
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Predictions collection indexes
            self.db.predictions.create_index([("timestamp", DESCENDING)])
            self.db.predictions.create_index([("predicted_disease", ASCENDING)])
            self.db.predictions.create_index([("confidence", DESCENDING)])
            
            # Diseases collection indexes
            self.db.diseases.create_index([("name", ASCENDING)], unique=True)
            
            # Users collection indexes
            self.db.users.create_index([("email", ASCENDING)], unique=True)
            self.db.users.create_index([("user_type", ASCENDING)])
            
            logger.info("✓ Database indexes created")
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("MongoDB connection closed")
    
    # ==================== DISEASE OPERATIONS ====================
    
    def get_disease(self, disease_name):
        """
        Get disease information by name
        
        Args:
            disease_name: Name of the disease
            
        Returns:
            Disease document or None
        """
        if not self.connected:
            return None
        
        try:
            return self.db.diseases.find_one({"name": disease_name})
        except Exception as e:
            logger.error(f"Error fetching disease: {e}")
            return None
    
    def get_all_diseases(self):
        """
        Get all diseases
        
        Returns:
            List of disease documents
        """
        if not self.connected:
            return []
        
        try:
            return list(self.db.diseases.find())
        except Exception as e:
            logger.error(f"Error fetching diseases: {e}")
            return []
    
    def insert_disease(self, disease_data):
        """
        Insert or update disease information
        
        Args:
            disease_data: Dictionary with disease information
            
        Returns:
            Inserted/updated document ID or None
        """
        if not self.connected:
            return None
        
        try:
            # Add timestamps
            disease_data['created_at'] = datetime.now()
            disease_data['updated_at'] = datetime.now()
            
            # Upsert (update if exists, insert if not)
            result = self.db.diseases.update_one(
                {"name": disease_data['name']},
                {"$set": disease_data},
                upsert=True
            )
            
            return result.upserted_id or disease_data['name']
        except Exception as e:
            logger.error(f"Error inserting disease: {e}")
            return None
    
    def update_disease(self, disease_name, disease_data):
        """
        Update disease information
        
        Args:
            disease_name: Name of the disease to update
            disease_data: Dictionary with updated disease information
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            # Preserve the name, add updated timestamp
            update_data = disease_data.copy()
            update_data['updated_at'] = datetime.now()
            
            # Remove _id if present (can't update _id)
            update_data.pop('_id', None)
            
            result = self.db.diseases.update_one(
                {"name": disease_name},
                {"$set": update_data}
            )
            
            if result.modified_count > 0 or result.matched_count > 0:
                logger.info(f"✓ Updated disease: {disease_name}")
                return True
            else:
                logger.warning(f"Disease not found: {disease_name}")
                return False
        except Exception as e:
            logger.error(f"Error updating disease: {e}")
            return False
    
    # ==================== PREDICTION OPERATIONS ====================
    
    def save_prediction(self, prediction_data):
        """
        Save prediction to database
        
        Args:
            prediction_data: Dictionary with prediction information
            
        Returns:
            Inserted document ID or None
        """
        if not self.connected:
            return None
        
        try:
            # Add timestamp if not present
            if 'timestamp' not in prediction_data:
                prediction_data['timestamp'] = datetime.now()
            
            result = self.db.predictions.insert_one(prediction_data)
            logger.info(f"✓ Saved prediction {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            return None
    
    def get_predictions(self, limit=20, skip=0, disease_filter=None):
        """
        Get predictions with pagination
        
        Args:
            limit: Number of predictions to return
            skip: Number of predictions to skip
            disease_filter: Filter by disease name
            
        Returns:
            List of prediction documents
        """
        if not self.connected:
            return []
        
        try:
            query = {}
            if disease_filter:
                query['predicted_disease'] = disease_filter
            
            predictions = self.db.predictions.find(query)\
                .sort("timestamp", DESCENDING)\
                .skip(skip)\
                .limit(limit)
            
            return list(predictions)
        except Exception as e:
            logger.error(f"Error fetching predictions: {e}")
            return []
    
    def count_predictions(self, disease_filter=None):
        """
        Count total predictions
        
        Args:
            disease_filter: Filter by disease name
            
        Returns:
            Count of predictions
        """
        if not self.connected:
            return 0
        
        try:
            query = {}
            if disease_filter:
                query['predicted_disease'] = disease_filter
            
            return self.db.predictions.count_documents(query)
        except Exception as e:
            logger.error(f"Error counting predictions: {e}")
            return 0
    
    def count_unique_locations(self):
        """
        Count unique locations (city + region combinations) from predictions
        This gives an accurate count of different places where farmers are using the system
        
        Returns:
            Count of unique city-region combinations
        """
        if not self.connected:
            return 0
        
        try:
            # Use aggregation to get distinct city-region combinations
            pipeline = [
                {
                    "$match": {
                        "location": {"$exists": True},
                        "user_type": {"$ne": "admin"}  # Exclude admin predictions
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "city": "$location.city",
                            "region": "$location.region",
                            "country": "$location.country"
                        }
                    }
                },
                {
                    "$match": {
                        "_id.city": {"$ne": "Unknown", "$ne": "Local", "$ne": None}
                    }
                },
                {
                    "$count": "total"
                }
            ]
            
            result = list(self.db.predictions.aggregate(pipeline))
            
            if result and len(result) > 0:
                return result[0]['total']
            return 0
        except Exception as e:
            logger.error(f"Error counting unique locations: {e}")
            return 0
    
    def get_location_statistics(self):
        """
        Get statistics on locations where predictions are being made
        
        Returns:
            List of locations with prediction counts
        """
        if not self.connected:
            return []
        
        try:
            pipeline = [
                {
                    "$match": {
                        "location": {"$exists": True},
                        "user_type": {"$ne": "admin"}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "city": "$location.city",
                            "region": "$location.region",
                            "country": "$location.country"
                        },
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$match": {
                        "_id.city": {"$ne": "Unknown", "$ne": "Local", "$ne": None}
                    }
                },
                {
                    "$sort": {"count": -1}
                },
                {
                    "$limit": 20
                }
            ]
            
            results = list(self.db.predictions.aggregate(pipeline))
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'city': result['_id'].get('city', 'Unknown'),
                    'region': result['_id'].get('region', 'Unknown'),
                    'country': result['_id'].get('country', 'Unknown'),
                    'prediction_count': result['count']
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error fetching location statistics: {e}")
            return []
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    def get_disease_statistics(self):
        """
        Get prediction statistics by disease
        
        Returns:
            List of disease statistics
        """
        if not self.connected:
            return []
        
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$predicted_disease",
                        "count": {"$sum": 1},
                        "avg_confidence": {"$avg": "$confidence"},
                        "max_confidence": {"$max": "$confidence"},
                        "min_confidence": {"$min": "$confidence"}
                    }
                },
                {
                    "$sort": {"count": -1}
                }
            ]
            
            return list(self.db.predictions.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error fetching statistics: {e}")
            return []
    
    def get_daily_statistics(self, days=30):
        """
        Get daily prediction counts
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of daily statistics
        """
        if not self.connected:
            return []
        
        try:
            from datetime import timedelta
            start_date = datetime.now() - timedelta(days=days)
            
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$timestamp"
                            }
                        },
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$sort": {"_id": 1}
                }
            ]
            
            return list(self.db.predictions.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error fetching daily statistics: {e}")
            return []
    
    def get_recent_predictions_count(self, days=7):
        """
        Get count of predictions in recent days
        
        Args:
            days: Number of days to look back
            
        Returns:
            Count of recent predictions
        """
        if not self.connected:
            return 0
        
        try:
            from datetime import timedelta
            start_date = datetime.now() - timedelta(days=days)
            
            return self.db.predictions.count_documents({
                "timestamp": {"$gte": start_date}
            })
        except Exception as e:
            logger.error(f"Error counting recent predictions: {e}")
            return 0
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, email, password_hash, user_type='farmer'):
        """
        Create a new user
        
        Args:
            email: User email address
            password_hash: Hashed password
            user_type: Type of user ('farmer' or 'admin')
            
        Returns:
            Inserted user ID or None
        """
        if not self.connected:
            return None
        
        try:
            # Check if user already exists
            existing_user = self.db.users.find_one({"email": email})
            if existing_user:
                return None
            
            user_data = {
                "email": email,
                "password": password_hash,
                "user_type": user_type,
                "created_at": datetime.now(),
                "last_login": None,
                "is_logged_in": False
            }
            
            result = self.db.users.insert_one(user_data)
            logger.info(f"✓ Created new user: {email}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email):
        """
        Get user by email
        
        Args:
            email: User email address
            
        Returns:
            User document or None
        """
        if not self.connected:
            return None
        
        try:
            return self.db.users.find_one({"email": email})
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """
        Get user by ID
        
        Args:
            user_id: User ID (string or ObjectId)
            
        Returns:
            User document or None
        """
        if not self.connected:
            return None
        
        try:
            from bson import ObjectId
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            return self.db.users.find_one({"_id": user_id})
        except Exception as e:
            logger.error(f"Error fetching user by ID: {e}")
            return None
    
    def update_last_login(self, email):
        """
        Update user's last login timestamp and set logged in status
        
        Args:
            email: User email address
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            result = self.db.users.update_one(
                {"email": email},
                {"$set": {
                    "last_login": datetime.now(),
                    "is_logged_in": True
                }}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False
    
    def update_logout_status(self, email):
        """
        Update user's logout status
        
        Args:
            email: User email address
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            result = self.db.users.update_one(
                {"email": email},
                {"$set": {"is_logged_in": False}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating logout status: {e}")
            return False
    
    def delete_user(self, email):
        """
        Delete a user account and all associated predictions
        
        Args:
            email: User email address
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            # First, delete all predictions associated with this user
            predictions_result = self.db.predictions.delete_many({"user_email": email})
            logger.info(f"✓ Deleted {predictions_result.deleted_count} predictions for user: {email}")
            
            # Then delete the user account
            result = self.db.users.delete_one({"email": email})
            if result.deleted_count > 0:
                logger.info(f"✓ Deleted user: {email}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    def count_users(self, user_type=None):
        """
        Count total users
        
        Args:
            user_type: Filter by user type ('farmer' or 'admin')
            
        Returns:
            Count of users
        """
        if not self.connected:
            return 0
        
        try:
            query = {}
            if user_type:
                query['user_type'] = user_type
            return self.db.users.count_documents(query)
        except Exception as e:
            logger.error(f"Error counting users: {e}")
            return 0
    
    def get_all_users(self, skip=0, limit=50):
        """
        Get all users with pagination
        
        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            List of user documents (without passwords)
        """
        if not self.connected:
            return []
        
        try:
            users = self.db.users.find(
                {},
                {'password': 0}  # Exclude password field
            ).skip(skip).limit(limit).sort("created_at", DESCENDING)
            
            return list(users)
        except Exception as e:
            logger.error(f"Error fetching all users: {e}")
            return []
    
    # ==================== USER PREDICTION ANALYTICS ====================
    
    def get_user_predictions(self, user_id, limit=20, skip=0):
        """
        Get predictions made by a specific user
        
        Args:
            user_id: User ID
            limit: Number of predictions to return
            skip: Number of predictions to skip
            
        Returns:
            List of prediction documents
        """
        if not self.connected:
            return []
        
        try:
            predictions = self.db.predictions.find({"user_id": str(user_id)})\
                .sort("timestamp", DESCENDING)\
                .skip(skip)\
                .limit(limit)
            
            return list(predictions)
        except Exception as e:
            logger.error(f"Error fetching user predictions: {e}")
            return []
    
    def count_user_predictions(self, user_id):
        """
        Count total predictions made by a user
        
        Args:
            user_id: User ID
            
        Returns:
            Count of predictions
        """
        if not self.connected:
            return 0
        
        try:
            return self.db.predictions.count_documents({"user_id": str(user_id)})
        except Exception as e:
            logger.error(f"Error counting user predictions: {e}")
            return 0
    
    def get_user_disease_statistics(self, user_id):
        """
        Get disease prediction statistics for a specific user
        
        Args:
            user_id: User ID
            
        Returns:
            List of disease statistics for the user
        """
        if not self.connected:
            return []
        
        try:
            pipeline = [
                {
                    "$match": {"user_id": str(user_id)}
                },
                {
                    "$group": {
                        "_id": "$predicted_disease",
                        "count": {"$sum": 1},
                        "avg_confidence": {"$avg": "$confidence"},
                        "max_confidence": {"$max": "$confidence"},
                        "min_confidence": {"$min": "$confidence"},
                        "last_prediction": {"$max": "$timestamp"}
                    }
                },
                {
                    "$sort": {"count": -1}
                }
            ]
            
            return list(self.db.predictions.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error fetching user disease statistics: {e}")
            return []


# Global database instance
mongodb = MongoDB()


def get_db():
    """Get the global MongoDB instance"""
    return mongodb
