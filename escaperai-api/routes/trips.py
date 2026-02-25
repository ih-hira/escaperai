"""
Trip routes demonstrating authentication middleware usage.
Shows examples of protected routes with various security decorators.
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime, timezone
from database import db
from models import Trip
from utils import (
    auth_required,
    auth_optional,
    owner_only,
    validate_json,
    rate_limit,
)

trips_bp = Blueprint('trips', __name__, url_prefix='/api/trips')


@trips_bp.route('', methods=['GET'])
@auth_required
@rate_limit(max_requests=30, window_seconds=60)
def list_user_trips():
    """
    Get all trips for the authenticated user.
    
    Protected: Requires valid JWT token
    Rate limited: Max 30 requests per minute
    
    Response:
    {
        "success": true,
        "data": [
            {
                "id": 1,
                "destination": "Paris",
                "start_date": "2024-06-01T00:00:00+00:00",
                "end_date": "2024-06-15T00:00:00+00:00",
                ...
            }
        ]
    }
    """
    try:
        user_id = g.user_id
        trips = Trip.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'success': True,
            'data': [trip.to_dict() for trip in trips]
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@trips_bp.route('', methods=['POST'])
@auth_required
@validate_json('destination', 'start_date', 'end_date')
def create_trip():
    """
    Create a new trip for the authenticated user.
    
    Protected: Requires valid JWT token
    Validates: Required JSON fields (destination, start_date, end_date)
    
    Request body:
    {
        "destination": "Tokyo",
        "start_date": "2024-07-01T00:00:00Z",
        "end_date": "2024-07-15T00:00:00Z",
        "latitude": 35.6762,
        "longitude": 139.6503,
        "itinerary": {}
    }
    
    Response:
    {
        "success": true,
        "data": {
            "id": 2,
            "destination": "Tokyo",
            ...
        }
    }
    """
    try:
        data = request.get_json()
        user_id = g.user_id
        
        # Parse dates
        try:
            start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Use ISO format (e.g., 2024-07-01T00:00:00Z)'
            }), 400
        
        # Validate dates
        if start_date >= end_date:
            return jsonify({
                'success': False,
                'error': 'Start date must be before end date'
            }), 400
        
        # Create trip
        trip = Trip(
            user_id=user_id,
            destination=data['destination'],
            start_date=start_date,
            end_date=end_date,
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            itinerary=data.get('itinerary', {})
        )
        
        db.session.add(trip)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': trip.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@trips_bp.route('/<int:id>', methods=['GET'])
@auth_required
def get_trip(id):
    """
    Get a specific trip (must belong to authenticated user).
    
    Protected: Requires valid JWT token AND user must own the trip
    
    Response:
    {
        "success": true,
        "data": {
            "id": 1,
            "destination": "Paris",
            ...
        }
    }
    """
    try:
        user_id = g.user_id
        trip = Trip.query.get(id)
        
        if not trip:
            return jsonify({
                'success': False,
                'error': 'Trip not found'
            }), 404
        
        # Check ownership
        if trip.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied. You do not own this trip.'
            }), 403
        
        return jsonify({
            'success': True,
            'data': trip.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@trips_bp.route('/<int:id>', methods=['PUT'])
@auth_required
def update_trip(id):
    """
    Update a trip (must belong to authenticated user).
    
    Protected: Requires valid JWT token AND user must own the trip
    
    Request body:
    {
        "destination": "Paris",
        "start_date": "2024-06-01T00:00:00Z",
        "end_date": "2024-06-15T00:00:00Z",
        "latitude": 48.8566,
        "longitude": 2.3522
    }
    
    Response:
    {
        "success": true,
        "data": { ... }
    }
    """
    try:
        user_id = g.user_id
        trip = Trip.query.get(id)
        
        if not trip:
            return jsonify({
                'success': False,
                'error': 'Trip not found'
            }), 404
        
        # Check ownership
        if trip.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied. You do not own this trip.'
            }), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Update fields
        if 'destination' in data:
            trip.destination = data['destination']
        
        if 'start_date' in data:
            try:
                trip.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return jsonify({
                    'success': False,
                    'error': 'Invalid start_date format'
                }), 400
        
        if 'end_date' in data:
            try:
                trip.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return jsonify({
                    'success': False,
                    'error': 'Invalid end_date format'
                }), 400
        
        if 'latitude' in data:
            trip.latitude = data['latitude']
        
        if 'longitude' in data:
            trip.longitude = data['longitude']
        
        if 'itinerary' in data:
            trip.itinerary = data['itinerary']
        
        # Validate dates
        if trip.start_date >= trip.end_date:
            return jsonify({
                'success': False,
                'error': 'Start date must be before end date'
            }), 400
        
        trip.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': trip.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@trips_bp.route('/<int:id>', methods=['DELETE'])
@auth_required
def delete_trip(id):
    """
    Delete a trip (must belong to authenticated user).
    
    Protected: Requires valid JWT token AND user must own the trip
    
    Response:
    {
        "success": true,
        "message": "Trip deleted successfully"
    }
    """
    try:
        user_id = g.user_id
        trip = Trip.query.get(id)
        
        if not trip:
            return jsonify({
                'success': False,
                'error': 'Trip not found'
            }), 404
        
        # Check ownership
        if trip.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied. You do not own this trip.'
            }), 403
        
        db.session.delete(trip)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Trip deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@trips_bp.route('/<int:id>/itinerary', methods=['POST'])
@auth_required
@validate_json('date', 'title', 'description')
def add_itinerary_item(id):
    """
    Add an item to a trip's itinerary.
    
    Protected: Requires valid JWT token AND user must own the trip
    Validates: Required fields (date, title, description)
    
    Request body:
    {
        "date": "2024-06-05",
        "title": "Eiffel Tower Visit",
        "description": "Visit and climb the Eiffel Tower",
        "location": "5 Avenue Anatole France, 75007 Paris"
    }
    
    Response:
    {
        "success": true,
        "data": { ... }
    }
    """
    try:
        user_id = g.user_id
        trip = Trip.query.get(id)
        
        if not trip:
            return jsonify({
                'success': False,
                'error': 'Trip not found'
            }), 404
        
        # Check ownership
        if trip.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied. You do not own this trip.'
            }), 403
        
        data = request.get_json()
        
        # Parse date
        try:
            date = datetime.fromisoformat(data['date'])
        except (ValueError, AttributeError):
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Use ISO format (e.g., 2024-06-05)'
            }), 400
        
        # Add itinerary item
        trip.add_itinerary_item(
            date=date,
            title=data['title'],
            description=data['description'],
            location=data.get('location')
        )
        
        trip.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': trip.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
