"""
Database Models for Chilli Disease Detection System
SQLAlchemy models for PostgreSQL/NeonDB
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
import json

db = SQLAlchemy()


class Disease(db.Model):
    """Disease information table"""
    __tablename__ = 'diseases'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    severity = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Store complex data as JSONB (efficient querying in PostgreSQL)
    symptoms = db.Column(JSONB, nullable=False, default=list)
    causes = db.Column(JSONB, nullable=False, default=list)
    treatment = db.Column(JSONB, nullable=False, default=list)
    prevention = db.Column(JSONB, nullable=False, default=list)
    organic_solutions = db.Column(JSONB, nullable=False, default=list)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    predictions = db.relationship('Prediction', backref='disease', lazy='dynamic')
    
    def to_dict(self):
        """Convert to dictionary format (compatible with existing DISEASE_INFO structure)"""
        return {
            'severity': self.severity,
            'description': self.description,
            'symptoms': self.symptoms,
            'causes': self.causes,
            'treatment': self.treatment,
            'prevention': self.prevention,
            'organic_solutions': self.organic_solutions
        }
    
    def __repr__(self):
        return f'<Disease {self.name}>'


class Prediction(db.Model):
    """Prediction history table - tracks all disease detections"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Image information
    image_filename = db.Column(db.String(255), nullable=True)
    image_path = db.Column(db.String(500), nullable=True)
    
    # Prediction results
    predicted_disease = db.Column(db.String(100), nullable=False)
    disease_id = db.Column(db.Integer, db.ForeignKey('diseases.id'), nullable=True)
    confidence = db.Column(db.Float, nullable=False)
    
    # Store all probabilities as JSONB
    all_probabilities = db.Column(JSONB, nullable=False, default=dict)
    top_3_predictions = db.Column(JSONB, nullable=False, default=list)
    
    # Validation information
    validation_method = db.Column(db.String(100), nullable=True)
    validation_message = db.Column(db.Text, nullable=True)
    
    # Request metadata
    user_ip = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Model information
    model_version = db.Column(db.String(20), default='1.0.0')
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'predicted_disease': self.predicted_disease,
            'confidence': self.confidence,
            'all_probabilities': self.all_probabilities,
            'top_3_predictions': self.top_3_predictions,
            'validation_method': self.validation_method,
            'timestamp': self.timestamp.isoformat(),
            'model_version': self.model_version
        }
    
    def __repr__(self):
        return f'<Prediction {self.id}: {self.predicted_disease} ({self.confidence:.2f}%)>'


class DailyStats(db.Model):
    """Daily statistics table - aggregated analytics"""
    __tablename__ = 'daily_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    disease_name = db.Column(db.String(100), nullable=False)
    
    total_predictions = db.Column(db.Integer, default=0)
    avg_confidence = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('date', 'disease_name', name='unique_daily_disease'),
    )
    
    def to_dict(self):
        return {
            'date': self.date.isoformat(),
            'disease_name': self.disease_name,
            'total_predictions': self.total_predictions,
            'avg_confidence': self.avg_confidence
        }
    
    def __repr__(self):
        return f'<DailyStats {self.date}: {self.disease_name} ({self.total_predictions} predictions)>'
