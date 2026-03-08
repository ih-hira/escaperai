"""
Itinerary utilities for generating and managing trip itineraries.
Provides functions for creating default itinerary templates and managing daily activities.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional


def get_date_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    """
    Generate a list of dates between start_date and end_date (inclusive).
    
    Args:
        start_date: Trip start date
        end_date: Trip end date
    
    Returns:
        List of datetime objects for each day of the trip
    
    Raises:
        ValueError: If start_date is after end_date
    """
    if start_date > end_date:
        raise ValueError("Start date must be before or equal to end date")
    
    dates = []
    current_date = start_date.date() if hasattr(start_date, 'date') else start_date
    end = end_date.date() if hasattr(end_date, 'date') else end_date
    
    while current_date <= end:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    return dates


def generate_default_itinerary(
    destination: str,
    start_date: datetime,
    end_date: datetime,
    template_type: str = 'standard'
) -> Dict[str, List[Dict]]:
    """
    Generate a default itinerary template for a trip.
    Creates placeholder entries for each day with generic activities.
    
    Args:
        destination: Trip destination name
        start_date: Trip start date
        end_date: Trip end date
        template_type: Type of template - 'standard', 'adventure', 'relaxation', 'cultural'
    
    Returns:
        Dictionary with date strings as keys and activity lists as values
    
    Example:
        >>> from datetime import datetime
        >>> start = datetime(2024, 6, 1)
        >>> end = datetime(2024, 6, 3)
        >>> itinerary = generate_default_itinerary('Paris', start, end)
        >>> itinerary['2024-06-01']
        [{'title': 'Morning Activity', 'description': '...', 'location': None}]
    """
    dates = get_date_range(start_date, end_date)
    itinerary = {}
    
    templates = {
        'standard': _standard_template,
        'adventure': _adventure_template,
        'relaxation': _relaxation_template,
        'cultural': _cultural_template,
    }
    
    template_func = templates.get(template_type, _standard_template)
    
    for i, date in enumerate(dates):
        date_str = date.isoformat()
        day_number = i + 1
        total_days = len(dates)
        
        activities = template_func(destination, day_number, total_days)
        itinerary[date_str] = activities
    
    return itinerary


def _standard_template(destination: str, day: int, total_days: int) -> List[Dict]:
    """Standard template with morning, afternoon, and evening activities."""
    return [
        {
            'title': f'Day {day} - Morning Activity',
            'description': f'Explore a local attraction or landmark in {destination}.',
            'location': None
        },
        {
            'title': f'Day {day} - Lunch',
            'description': f'Try local cuisine at a recommended restaurant in {destination}.',
            'location': None
        },
        {
            'title': f'Day {day} - Afternoon Activity',
            'description': f'Visit a museum, park, or cultural site in {destination}.',
            'location': None
        },
        {
            'title': f'Day {day} - Dinner',
            'description': f'Enjoy dinner at a local restaurant or café.',
            'location': None
        }
    ]


def _adventure_template(destination: str, day: int, total_days: int) -> List[Dict]:
    """Adventure-focused template with outdoor and active activities."""
    activities = [
        {
            'title': f'Day {day} - Early Morning Adventure',
            'description': f'Start with an outdoor activity or sunrise viewing in {destination}.',
            'location': None
        },
        {
            'title': f'Day {day} - Mid-day Challenge',
            'description': f'Engage in an exciting activity like hiking, water sports, or cycling.',
            'location': None
        },
        {
            'title': f'Day {day} - Evening Activity',
            'description': f'Explore local nightlife or enjoy an evening adventure experience.',
            'location': None
        }
    ]
    return activities


def _relaxation_template(destination: str, day: int, total_days: int) -> List[Dict]:
    """Relaxation-focused template with spa and leisure activities."""
    return [
        {
            'title': f'Day {day} - Leisurely Morning',
            'description': f'Sleep in and enjoy a relaxing breakfast in {destination}.',
            'location': None
        },
        {
            'title': f'Day {day} - Spa or Wellness',
            'description': f'Indulge in a spa treatment, yoga session, or wellness activity.',
            'location': None
        },
        {
            'title': f'Day {day} - Leisure Time',
            'description': f'Enjoy reading, leisure shopping, or simply relaxing in a local café.',
            'location': None
        },
        {
            'title': f'Day {day} - Scenic Dinner',
            'description': f'Dine at a scenic or relaxing restaurant with a view.',
            'location': None
        }
    ]


def _cultural_template(destination: str, day: int, total_days: int) -> List[Dict]:
    """Cultural-focused template with museums and cultural experiences."""
    return [
        {
            'title': f'Day {day} - Historical Tour',
            'description': f'Visit historical sites and learn about {destination}\'s rich heritage.',
            'location': None
        },
        {
            'title': f'Day {day} - Museum Visit',
            'description': f'Explore world-class museums showcasing art, history, or local culture.',
            'location': None
        },
        {
            'title': f'Day {day} - Local Culture',
            'description': f'Participate in a local cultural activity, workshop, or performance.',
            'location': None
        },
        {
            'title': f'Day {day} - Traditional Dining',
            'description': f'Experience traditional cuisine and dining customs of {destination}.',
            'location': None
        }
    ]


def add_activity_to_itinerary(
    itinerary: Dict[str, List[Dict]],
    date: str,
    title: str,
    description: str,
    location: Optional[str] = None
) -> Dict[str, List[Dict]]:
    """
    Add a single activity to an existing itinerary.
    
    Args:
        itinerary: Existing itinerary dictionary
        date: Date string in ISO format (YYYY-MM-DD)
        title: Activity title
        description: Activity description
        location: Optional location details
    
    Returns:
        Updated itinerary dictionary
    
    Raises:
        ValueError: If date format is invalid
    """
    try:
        # Validate date format
        datetime.fromisoformat(date)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid date format: {date}. Use ISO format (YYYY-MM-DD)")
    
    if date not in itinerary:
        itinerary[date] = []
    
    activity = {
        'title': title,
        'description': description,
        'location': location
    }
    
    itinerary[date].append(activity)
    return itinerary


def remove_activity_from_itinerary(
    itinerary: Dict[str, List[Dict]],
    date: str,
    activity_index: int
) -> Dict[str, List[Dict]]:
    """
    Remove an activity from an itinerary.
    
    Args:
        itinerary: Existing itinerary dictionary
        date: Date string in ISO format (YYYY-MM-DD)
        activity_index: Index of the activity to remove
    
    Returns:
        Updated itinerary dictionary
    
    Raises:
        ValueError: If date not found or activity index is invalid
    """
    if date not in itinerary:
        raise ValueError(f"No activities found for date: {date}")
    
    if activity_index < 0 or activity_index >= len(itinerary[date]):
        raise ValueError(f"Invalid activity index: {activity_index}")
    
    itinerary[date].pop(activity_index)
    
    # Remove empty dates from itinerary
    if not itinerary[date]:
        del itinerary[date]
    
    return itinerary


def get_trip_duration(start_date: datetime, end_date: datetime) -> int:
    """
    Calculate the number of days in a trip.
    
    Args:
        start_date: Trip start date
        end_date: Trip end date
    
    Returns:
        Number of days (inclusive)
    """
    delta = end_date.date() - start_date.date() if hasattr(start_date, 'date') else end_date - start_date
    return delta.days + 1


def get_activities_count(itinerary: Dict[str, List[Dict]]) -> int:
    """
    Count total number of activities in itinerary.
    
    Args:
        itinerary: Itinerary dictionary
    
    Returns:
        Total number of activities
    """
    return sum(len(activities) for activities in itinerary.values())


def validate_itinerary_structure(itinerary: Dict) -> bool:
    """
    Validate that itinerary follows the correct structure.
    
    Args:
        itinerary: Itinerary dictionary to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(itinerary, dict):
        return False
    
    for date, activities in itinerary.items():
        # Validate date format
        try:
            datetime.fromisoformat(date)
        except (ValueError, TypeError):
            return False
        
        # Validate activities list
        if not isinstance(activities, list):
            return False
        
        for activity in activities:
            if not isinstance(activity, dict):
                return False
            
            required_keys = {'title', 'description'}
            if not required_keys.issubset(activity.keys()):
                return False
    
    return True
