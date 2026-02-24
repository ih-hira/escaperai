from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSON

class Trip(db.Model):
    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    destination = db.Column(db.String(255), nullable=False, index=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    itinerary = db.Column(JSON, nullable=True, default={})
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f'<Trip {self.destination} ({self.start_date.date()})>'
    
    def add_itinerary_item(self, date, title, description, location=None):
        """Add an item to the itinerary"""
        if not self.itinerary:
            self.itinerary = {}
        
        date_str = date.isoformat() if hasattr(date, 'isoformat') else str(date)
        
        if date_str not in self.itinerary:
            self.itinerary[date_str] = []
        
        item = {
            'title': title,
            'description': description,
            'location': location
        }
        self.itinerary[date_str].append(item)
    
    def get_itinerary_by_date(self, date):
        """Get itinerary items for a specific date"""
        if not self.itinerary:
            return []
        
        date_str = date.isoformat() if hasattr(date, 'isoformat') else str(date)
        return self.itinerary.get(date_str, [])
    
    def to_dict(self):
        """Convert trip object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'destination': self.destination,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'coordinates': {
                'latitude': self.latitude,
                'longitude': self.longitude
            },
            'itinerary': self.itinerary or {},
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
