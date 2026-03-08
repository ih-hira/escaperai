"""
Examples and tests for the Itinerary Generation feature.
Demonstrates how to use the itinerary generation utilities and API endpoints.
"""

from datetime import datetime, timedelta
import json


def example_1_generate_itinerary_in_code():
    """Example: Generate itinerary template using Python functions."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Generate Itinerary in Code")
    print("="*60)
    
    from utils.itinerary_utils import generate_default_itinerary
    
    # Define trip dates
    start_date = datetime(2024, 6, 1)
    end_date = datetime(2024, 6, 5)
    
    # Generate standard template
    itinerary = generate_default_itinerary(
        destination='Paris',
        start_date=start_date,
        end_date=end_date,
        template_type='standard'
    )
    
    print(f"\nGenerated itinerary for Paris (5 days):")
    print(json.dumps(itinerary, indent=2))
    
    return itinerary


def example_2_add_and_remove_activities():
    """Example: Add and remove activities from itinerary."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Add and Remove Activities")
    print("="*60)
    
    from utils.itinerary_utils import (
        generate_default_itinerary,
        add_activity_to_itinerary,
        remove_activity_from_itinerary
    )
    
    # Start with a basic itinerary
    start_date = datetime(2024, 6, 1)
    end_date = datetime(2024, 6, 3)
    
    itinerary = generate_default_itinerary(
        destination='Tokyo',
        start_date=start_date,
        end_date=end_date,
        template_type='standard'
    )
    
    print(f"\nOriginal activities on 2024-06-01: {len(itinerary['2024-06-01'])}")
    
    # Add a custom activity
    itinerary = add_activity_to_itinerary(
        itinerary,
        date='2024-06-01',
        title='Senso-ji Temple',
        description='Visit the historic Buddhist temple at dawn',
        location='2 Chome Asakusa, Taito, Tokyo'
    )
    
    print(f"After adding activity: {len(itinerary['2024-06-01'])}")
    print(f"\nNewly added activity:")
    print(json.dumps(itinerary['2024-06-01'][-1], indent=2))
    
    # Remove an activity (index 0 - morning activity)
    itinerary = remove_activity_from_itinerary(
        itinerary,
        date='2024-06-01',
        activity_index=0
    )
    
    print(f"After removing activity: {len(itinerary['2024-06-01'])}")


def example_3_different_template_types():
    """Example: Generate different template types."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Different Template Types")
    print("="*60)
    
    from utils.itinerary_utils import generate_default_itinerary
    
    start_date = datetime(2024, 7, 1)
    end_date = datetime(2024, 7, 2)  # Just 2 days for clarity
    
    templates = ['standard', 'adventure', 'relaxation', 'cultural']
    
    for template_type in templates:
        itinerary = generate_default_itinerary(
            destination='Barcelona',
            start_date=start_date,
            end_date=end_date,
            template_type=template_type
        )
        
        activities = itinerary['2024-07-01']
        print(f"\n{template_type.upper()} Template ({len(activities)} activities):")
        for activity in activities:
            print(f"  - {activity['title']}")


def example_4_trip_duration_and_activity_count():
    """Example: Calculate trip duration and count activities."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Trip Duration and Activity Count")
    print("="*60)
    
    from utils.itinerary_utils import (
        generate_default_itinerary,
        get_trip_duration,
        get_activities_count
    )
    
    start_date = datetime(2024, 8, 1)
    end_date = datetime(2024, 8, 10)  # 10-day trip
    
    itinerary = generate_default_itinerary(
        destination='Thailand',
        start_date=start_date,
        end_date=end_date,
        template_type='adventure'
    )
    
    duration = get_trip_duration(start_date, end_date)
    activity_count = get_activities_count(itinerary)
    
    print(f"\nTrip Duration: {duration} days")
    print(f"Total Activities: {activity_count}")
    print(f"Average Activities per Day: {activity_count // duration}")


def example_5_validate_itinerary():
    """Example: Validate itinerary structure."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Validate Itinerary Structure")
    print("="*60)
    
    from utils.itinerary_utils import validate_itinerary_structure
    
    # Valid itinerary
    valid_itinerary = {
        '2024-06-01': [
            {
                'title': 'Morning Activity',
                'description': 'Do something fun',
                'location': 'Some place'
            }
        ]
    }
    
    # Invalid itinerary (missing required field)
    invalid_itinerary = {
        '2024-06-01': [
            {
                'title': 'Activity',
                'location': 'Place'
                # Missing 'description'
            }
        ]
    }
    
    is_valid_1 = validate_itinerary_structure(valid_itinerary)
    is_valid_2 = validate_itinerary_structure(invalid_itinerary)
    
    print(f"\nValid itinerary check: {is_valid_1}")
    print(f"Invalid itinerary check: {is_valid_2}")


def example_6_using_trip_model():
    """Example: Using the Trip model method for generation."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Using Trip Model Method")
    print("="*60)
    
    # This would be used in actual Flask routes
    print("""
    from models import Trip
    from database import db
    
    # Get existing trip
    trip = Trip.query.get(1)
    
    # Generate itinerary using model method
    trip.generate_default_itinerary(template_type='cultural')
    
    # Save to database
    db.session.commit()
    
    # Access the itinerary
    print(trip.itinerary)
    """)


def example_7_api_workflow():
    """Example: Complete API workflow."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Complete API Workflow")
    print("="*60)
    
    print("""
    # STEP 1: Create a Trip
    curl -X POST http://localhost:5000/api/trips \\
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{
        "destination": "Barcelona",
        "start_date": "2024-09-01T00:00:00Z",
        "end_date": "2024-09-07T00:00:00Z",
        "latitude": 41.3851,
        "longitude": 2.1734
      }'
    # Response: {"success": true, "data": {"id": 1, ...}}
    
    
    # STEP 2: Generate Itinerary Template
    curl -X POST http://localhost:5000/api/trips/1/itinerary/generate \\
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{
        "template_type": "cultural"
      }'
    # Response: {"success": true, "data": {"id": 1, "itinerary": {...}}}
    
    
    # STEP 3: View Trip with Itinerary
    curl -X GET http://localhost:5000/api/trips/1 \\
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
    # Response shows populated itinerary
    
    
    # STEP 4: Add Custom Activity
    curl -X POST http://localhost:5000/api/trips/1/itinerary \\
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{
        "date": "2024-09-02",
        "title": "Sagrada Familia",
        "description": "Visit the iconic basilica designed by Gaudí",
        "location": "Carrer de Mallorca, 401, Barcelona"
      }'
    
    
    # STEP 5: Update Trip with Modified Itinerary
    curl -X PUT http://localhost:5000/api/trips/1 \\
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{
        "itinerary": {...your updated itinerary...}
      }'
    """)


def example_8_error_handling():
    """Example: Error handling scenarios."""
    print("\n" + "="*60)
    print("EXAMPLE 8: Error Handling")
    print("="*60)
    
    from utils.itinerary_utils import (
        add_activity_to_itinerary,
        remove_activity_from_itinerary
    )
    
    itinerary = {
        '2024-06-01': [
            {'title': 'Activity 1', 'description': 'Desc 1', 'location': None}
        ]
    }
    
    # Error 1: Invalid date format
    try:
        add_activity_to_itinerary(
            itinerary,
            date='06-01-2024',  # Wrong format
            title='Activity',
            description='Test'
        )
    except ValueError as e:
        print(f"Error 1 - Invalid date format: {e}")
    
    # Error 2: Activity index out of range
    try:
        remove_activity_from_itinerary(
            itinerary,
            date='2024-06-01',
            activity_index=10  # Too high
        )
    except ValueError as e:
        print(f"Error 2 - Invalid activity index: {e}")
    
    # Error 3: Date not found
    try:
        remove_activity_from_itinerary(
            itinerary,
            date='2024-07-01',  # Doesn't exist
            activity_index=0
        )
    except ValueError as e:
        print(f"Error 3 - Date not found: {e}")


def run_all_examples():
    """Run all examples."""
    examples = [
        example_1_generate_itinerary_in_code,
        example_2_add_and_remove_activities,
        example_3_different_template_types,
        example_4_trip_duration_and_activity_count,
        example_5_validate_itinerary,
        example_6_using_trip_model,
        example_7_api_workflow,
        example_8_error_handling,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nNote: {example.__name__} requires database setup")
            print(f"Error: {e}\n")


if __name__ == '__main__':
    print("\n" + "█"*60)
    print("ITINERARY GENERATION EXAMPLES")
    print("█"*60)
    
    # Run individual examples or all
    # example_1_generate_itinerary_in_code()
    # example_2_add_and_remove_activities()
    # example_3_different_template_types()
    # example_4_trip_duration_and_activity_count()
    # example_5_validate_itinerary()
    example_6_using_trip_model()
    example_7_api_workflow()
    example_8_error_handling()
    
    print("\n" + "█"*60)
    print("For more examples, uncomment them in the main section")
    print("█"*60 + "\n")
