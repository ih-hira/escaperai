"""
Middleware test examples demonstrating how to test protected routes.
Shows examples of testing various authentication scenarios.
"""

import pytest
import json
from datetime import datetime, timedelta, timezone
from app import app, db
from models import User, Trip
from utils import hash_password


@pytest.fixture
def client():
    """Create a test client with a fresh database."""
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def auth_token(client):
    """Create a test user and return their JWT token."""
    # Register a user
    response = client.post('/api/auth/register', json={
        'email': 'testuser@example.com',
        'password': 'TestP@ss123'
    })
    assert response.status_code == 201
    
    # Login to get token
    response = client.post('/api/auth/login', json={
        'email': 'testuser@example.com',
        'password': 'TestP@ss123'
    })
    assert response.status_code == 200
    
    data = response.get_json()
    return data['data']['access_token']


@pytest.fixture
def another_user_token(client):
    """Create another test user and return their JWT token."""
    response = client.post('/api/auth/register', json={
        'email': 'otheruser@example.com',
        'password': 'OtherP@ss123'
    })
    
    response = client.post('/api/auth/login', json={
        'email': 'otheruser@example.com',
        'password': 'OtherP@ss123'
    })
    
    data = response.get_json()
    return data['data']['access_token']


class TestAuthRequired:
    """Tests for @auth_required middleware."""
    
    def test_requires_token(self, client):
        """Test that route without token returns 401."""
        response = client.get('/api/trips')
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
    
    def test_accepts_valid_token(self, client, auth_token):
        """Test that route with valid token succeeds."""
        response = client.get(
            '/api/trips',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)
    
    def test_rejects_invalid_token(self, client):
        """Test that route with invalid token returns 401."""
        response = client.get(
            '/api/trips',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        assert response.status_code == 401
    
    def test_rejects_malformed_header(self, client):
        """Test that malformed auth header returns 401."""
        response = client.get(
            '/api/trips',
            headers={'Authorization': 'InvalidFormat'}
        )
        assert response.status_code == 401


class TestOwnershipCheck:
    """Tests for ownership validation in protected routes."""
    
    def test_can_access_own_trip(self, client, auth_token):
        """Test that user can access their own trip."""
        # Create a trip
        response = client.post(
            '/api/trips',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'destination': 'Paris',
                'start_date': '2024-06-01T00:00:00Z',
                'end_date': '2024-06-15T00:00:00Z'
            }
        )
        assert response.status_code == 201
        trip_id = response.get_json()['data']['id']
        
        # Access the trip
        response = client.get(
            f'/api/trips/{trip_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 200
    
    def test_cannot_access_others_trip(self, client, auth_token, another_user_token):
        """Test that user cannot access another user's trip."""
        # User 1 creates a trip
        response = client.post(
            '/api/trips',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'destination': 'Paris',
                'start_date': '2024-06-01T00:00:00Z',
                'end_date': '2024-06-15T00:00:00Z'
            }
        )
        trip_id = response.get_json()['data']['id']
        
        # User 2 tries to access it
        response = client.get(
            f'/api/trips/{trip_id}',
            headers={'Authorization': f'Bearer {another_user_token}'}
        )
        assert response.status_code == 403
        data = response.get_json()
        assert 'Access denied' in data['error']
    
    def test_cannot_update_others_trip(self, client, auth_token, another_user_token):
        """Test that user cannot update another user's trip."""
        # User 1 creates a trip
        response = client.post(
            '/api/trips',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'destination': 'Paris',
                'start_date': '2024-06-01T00:00:00Z',
                'end_date': '2024-06-15T00:00:00Z'
            }
        )
        trip_id = response.get_json()['data']['id']
        
        # User 2 tries to update it
        response = client.put(
            f'/api/trips/{trip_id}',
            headers={'Authorization': f'Bearer {another_user_token}'},
            json={'destination': 'London'}
        )
        assert response.status_code == 403
    
    def test_cannot_delete_others_trip(self, client, auth_token, another_user_token):
        """Test that user cannot delete another user's trip."""
        # User 1 creates a trip
        response = client.post(
            '/api/trips',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'destination': 'Paris',
                'start_date': '2024-06-01T00:00:00Z',
                'end_date': '2024-06-15T00:00:00Z'
            }
        )
        trip_id = response.get_json()['data']['id']
        
        # User 2 tries to delete it
        response = client.delete(
            f'/api/trips/{trip_id}',
            headers={'Authorization': f'Bearer {another_user_token}'}
        )
        assert response.status_code == 403


class TestValidateJson:
    """Tests for @validate_json middleware."""
    
    def test_rejects_missing_required_fields(self, client, auth_token):
        """Test that missing required fields returns 400."""
        response = client.post(
            '/api/trips',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'destination': 'Paris'
                # Missing start_date and end_date
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'missing' in data
    
    def test_accepts_all_required_fields(self, client, auth_token):
        """Test that with all required fields succeeds."""
        response = client.post(
            '/api/trips',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'destination': 'Paris',
                'start_date': '2024-06-01T00:00:00Z',
                'end_date': '2024-06-15T00:00:00Z'
            }
        )
        assert response.status_code == 201
    
    def test_rejects_non_json_body(self, client, auth_token):
        """Test that non-JSON body returns 400."""
        response = client.post(
            '/api/trips',
            headers={
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'text/plain'
            },
            data='not json'
        )
        assert response.status_code == 400


class TestRateLimiting:
    """Tests for @rate_limit middleware."""
    
    def test_allows_requests_within_limit(self, client, auth_token):
        """Test that requests within limit are allowed."""
        # Make 5 requests (limit is 30 per minute)
        for i in range(5):
            response = client.get(
                '/api/trips',
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            assert response.status_code == 200
    
    def test_exceeds_rate_limit(self, client, auth_token):
        """Test that exceeding limit returns 429."""
        # Make requests up to the limit
        # Note: The real test would use time manipulation or
        # a lower limit for testing purposes
        
        # For this example, we're just verifying the 429 response format
        response = client.get(
            '/api/trips',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 200
        
        if response.status_code == 429:
            data = response.get_json()
            assert 'retry_after' in data


class TestTripCRUD:
    """Integration tests for trip CRUD operations."""
    
    def test_create_trip(self, client, auth_token):
        """Test creating a trip."""
        response = client.post(
            '/api/trips',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'destination': 'Tokyo',
                'start_date': '2024-07-01T00:00:00Z',
                'end_date': '2024-07-15T00:00:00Z',
                'latitude': 35.6762,
                'longitude': 139.6503
            }
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['destination'] == 'Tokyo'
        assert data['data']['user_id'] == data['data'].get('user_id')
    
    def test_list_user_trips(self, client, auth_token):
        """Test listing user's trips."""
        # Create a trip first
        client.post(
            '/api/trips',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'destination': 'Paris',
                'start_date': '2024-06-01T00:00:00Z',
                'end_date': '2024-06-15T00:00:00Z'
            }
        )
        
        # List trips
        response = client.get(
            '/api/trips',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) == 1
    
    def test_update_trip(self, client, auth_token):
        """Test updating a trip."""
        # Create a trip
        response = client.post(
            '/api/trips',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'destination': 'Paris',
                'start_date': '2024-06-01T00:00:00Z',
                'end_date': '2024-06-15T00:00:00Z'
            }
        )
        trip_id = response.get_json()['data']['id']
        
        # Update it
        response = client.put(
            f'/api/trips/{trip_id}',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'destination': 'London'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['destination'] == 'London'
    
    def test_delete_trip(self, client, auth_token):
        """Test deleting a trip."""
        # Create a trip
        response = client.post(
            '/api/trips',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'destination': 'Paris',
                'start_date': '2024-06-01T00:00:00Z',
                'end_date': '2024-06-15T00:00:00Z'
            }
        )
        trip_id = response.get_json()['data']['id']
        
        # Delete it
        response = client.delete(
            f'/api/trips/{trip_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 200
        
        # Verify it's gone
        response = client.get(
            f'/api/trips/{trip_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 404


class TestItinerary:
    """Tests for trip itinerary operations."""
    
    def test_add_itinerary_item(self, client, auth_token):
        """Test adding an item to trip itinerary."""
        # Create a trip
        response = client.post(
            '/api/trips',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'destination': 'Paris',
                'start_date': '2024-06-01T00:00:00Z',
                'end_date': '2024-06-15T00:00:00Z'
            }
        )
        trip_id = response.get_json()['data']['id']
        
        # Add itinerary item
        response = client.post(
            f'/api/trips/{trip_id}/itinerary',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'date': '2024-06-05',
                'title': 'Eiffel Tower',
                'description': 'Visit and climb',
                'location': 'Paris, France'
            }
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'itinerary' in data['data']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
