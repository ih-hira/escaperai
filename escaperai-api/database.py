"""
Database instance initialization.
This module creates the SQLAlchemy instance without requiring the app,
avoiding circular imports with models and routes.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
