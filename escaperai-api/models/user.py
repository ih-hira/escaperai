from database import db
from datetime import datetime, timezone
from utils.security import hash_password, verify_password

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    trips = db.relationship('Trip', backref=db.backref('user', lazy=True), cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set the password using secure PBKDF2 with SHA256"""
        self.password_hash = hash_password(password)
    
    def check_password(self, password):
        """Verify password against stored hash"""
        return verify_password(password, self.password_hash)
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'trips_count': len(self.trips),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
