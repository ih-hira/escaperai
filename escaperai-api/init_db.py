"""
Database initialization script
Run this script to create all database tables

Usage:
    python init_db.py
"""

import os
import sys
from app import app
from database import db
from models import User, Trip

def init_database():
    """Initialize the database and create all tables"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        print("\nAvailable models:")
        print("  - User")
        print("  - Trip")

def drop_database():
    """Drop all database tables (use with caution!)"""
    with app.app_context():
        confirm = input("⚠️  WARNING: This will drop all tables. Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            print("Dropping all tables...")
            db.drop_all()
            print("✓ All tables dropped!")
        else:
            print("Cancelled.")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--drop':
        drop_database()
    else:
        init_database()
