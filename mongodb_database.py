"""
MongoDB Database Module for Chilli Disease Detection System
Handles connections, collections, and database operations
"""

import os
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure
import logging

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
            self.client = MongoClient(
                self.connection_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                maxPoolSize=50
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
            disease_data['created_at'] = datetime.utcnow()
            disease_data['updated_at'] = datetime.utcnow()
            
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
                prediction_data['timestamp'] = datetime.utcnow()
            
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
            start_date = datetime.utcnow() - timedelta(days=days)
            
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
            start_date = datetime.utcnow() - timedelta(days=days)
            
            return self.db.predictions.count_documents({
                "timestamp": {"$gte": start_date}
            })
        except Exception as e:
            logger.error(f"Error counting recent predictions: {e}")
            return 0


# Global database instance
mongodb = MongoDB()


def get_db():
    """Get the global MongoDB instance"""
    return mongodb
