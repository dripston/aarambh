from datetime import datetime
from app import db

class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    precipitation = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WeatherData {self.location} at {self.timestamp}>'

class DisasterRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disaster_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.Integer, nullable=False)  # Scale 1-5
    date = db.Column(db.DateTime, nullable=False)
    casualties = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<DisasterRecord {self.disaster_type} at {self.location}>'

class DisasterPrediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disaster_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    probability = db.Column(db.Float, nullable=False)  # 0-1
    predicted_severity = db.Column(db.Integer, nullable=False)  # Scale 1-5
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<DisasterPrediction {self.disaster_type} at {self.location}>'

class ImageAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(100), nullable=True)
    analysis_result = db.Column(db.Text, nullable=True)
    disaster_type = db.Column(db.String(50), nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return f'<ImageAnalysis {self.filename}>'
