# Itinerary Generation Guide

## Overview

The Itinerary Generation feature provides utilities to create and manage trip itineraries. It includes functions to generate default templates, manage daily activities, and validate itinerary structures.

---

## Features

### 1. **Default Itinerary Templates**
Generate pre-populated itineraries with placeholder activities based on trip duration and destination.

### 2. **Multiple Template Types**
- **Standard**: Morning, lunch, afternoon, and dinner activities
- **Adventure**: Early morning, mid-day, and evening adventure-focused activities
- **Relaxation**: Spa, wellness, and leisure-focused activities
- **Cultural**: Historical, museum, and cultural experience-focused activities

### 3. **Activity Management**
- Add individual activities to specific dates
- Remove activities from the itinerary
- Retrieve activities by date
- Count total activities in an itinerary

### 4. **Validation & Utilities**
- Validate itinerary structure
- Get trip duration
- Calculate activities count
- Date range generation

---

## API Endpoints

### Generate Itinerary Template

**Endpoint:**
```
POST /api/trips/<trip_id>/itinerary/generate
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body (Optional):**
```json
{
    "template_type": "standard"
}
```

**Template Types:**
| Type | Purpose | Best For |
|------|---------|----------|
| `standard` | Default balanced itinerary | General trips |
| `adventure` | Outdoor & active activities | Adventure seekers |
| `relaxation` | Spa & leisure activities | Relaxation-focused trips |
| `cultural` | Museums & cultural events | Culture enthusiasts |

**Response (Success - 200 OK):**
```json
{
    "success": true,
    "message": "Itinerary template generated successfully using \"standard\" template",
    "data": {
        "id": 1,
        "destination": "Paris",
        "start_date": "2024-06-01T00:00:00+00:00",
        "end_date": "2024-06-05T00:00:00+00:00",
        "itinerary": {
            "2024-06-01": [
                {
                    "title": "Day 1 - Morning Activity",
                    "description": "Explore a local attraction or landmark in Paris.",
                    "location": null
                },
                {
                    "title": "Day 1 - Lunch",
                    "description": "Try local cuisine at a recommended restaurant in Paris.",
                    "location": null
                },
                ...
            ],
            "2024-06-02": [
                ...
            ]
        }
    }
}
```

**Response (Error - Trip Not Found - 404):**
```json
{
    "success": false,
    "error": "Trip not found"
}
```

**Response (Error - Access Denied - 403):**
```json
{
    "success": false,
    "error": "Access denied. You do not own this trip."
}
```

**Response (Error - Invalid Template Type - 400):**
```json
{
    "success": false,
    "error": "Invalid template_type. Must be one of: standard, adventure, relaxation, cultural"
}
```

---

## Using the API

### Step 1: Create a Trip
```bash
curl -X POST http://localhost:5000/api/trips \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Paris",
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-06-05T00:00:00Z",
    "latitude": 48.8566,
    "longitude": 2.3522
  }'
```

### Step 2: Generate Default Itinerary
```bash
curl -X POST http://localhost:5000/api/trips/1/itinerary/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "standard"
  }'
```

### Step 3: Add Custom Activity
```bash
curl -X POST http://localhost:5000/api/trips/1/itinerary \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-06-02",
    "title": "Eiffel Tower Visit",
    "description": "Visit and climb the Eiffel Tower",
    "location": "5 Avenue Anatole France, 75007 Paris"
  }'
```

---

## Using the Python Functions (Backend)

### Import the Module
```python
from utils.itinerary_utils import (
    generate_default_itinerary,
    get_date_range,
    add_activity_to_itinerary,
    remove_activity_from_itinerary,
    get_trip_duration,
    get_activities_count,
    validate_itinerary_structure
)
```

### Generate Default Itinerary
```python
from datetime import datetime

start = datetime(2024, 6, 1)
end = datetime(2024, 6, 5)

# Generate standard template
itinerary = generate_default_itinerary('Paris', start, end, template_type='standard')

# Result structure:
# {
#     '2024-06-01': [
#         {
#             'title': 'Day 1 - Morning Activity',
#             'description': 'Explore a local attraction or landmark in Paris.',
#             'location': None
#         },
#         ...
#     ],
#     ...
# }
```

### Using Trip Model Method
```python
from models import Trip
from database import db

trip = Trip.query.get(1)

# Generate template
trip.generate_default_itinerary(template_type='adventure')

# Save to database
db.session.commit()
```

### Get Date Range
```python
from utils.itinerary_utils import get_date_range
from datetime import datetime

start = datetime(2024, 6, 1)
end = datetime(2024, 6, 5)

dates = get_date_range(start, end)
# Result: [datetime(2024, 6, 1), datetime(2024, 6, 2), ..., datetime(2024, 6, 5)]
```

### Add Activity to Itinerary
```python
from utils.itinerary_utils import add_activity_to_itinerary

itinerary = {...}

itinerary = add_activity_to_itinerary(
    itinerary,
    date='2024-06-02',
    title='Eiffel Tower Visit',
    description='Visit and climb the Eiffel Tower',
    location='5 Avenue Anatole France, 75007 Paris'
)
```

### Remove Activity from Itinerary
```python
from utils.itinerary_utils import remove_activity_from_itinerary

itinerary = {...}

# Remove the second activity (index 1) from 2024-06-02
itinerary = remove_activity_from_itinerary(itinerary, '2024-06-02', 1)
```

### Get Trip Duration
```python
from utils.itinerary_utils import get_trip_duration
from datetime import datetime

start = datetime(2024, 6, 1)
end = datetime(2024, 6, 5)

duration = get_trip_duration(start, end)
# Result: 5 days
```

### Count Activities
```python
from utils.itinerary_utils import get_activities_count

itinerary = {...}

total = get_activities_count(itinerary)
# Result: Total number of activities across all days
```

### Validate Itinerary Structure
```python
from utils.itinerary_utils import validate_itinerary_structure

itinerary = {
    '2024-06-01': [
        {
            'title': 'Activity',
            'description': 'Description',
            'location': None
        }
    ]
}

is_valid = validate_itinerary_structure(itinerary)
# Result: True or False
```

---

## Itinerary JSON Structure

### Valid Format
```json
{
    "2024-06-01": [
        {
            "title": "Morning Activity",
            "description": "Description of the activity",
            "location": "Optional location details"
        },
        {
            "title": "Lunch",
            "description": "Try local cuisine",
            "location": "Restaurant name"
        }
    ],
    "2024-06-02": [
        ...
    ]
}
```

### Required Fields
- **Date Keys**: ISO format date string (YYYY-MM-DD)
- **title**: Activity title (string)
- **description**: Activity description (string)
- **location**: Optional location details (string or null)

---

## Template Examples

### Standard Template (3-day trip)
```json
{
    "2024-06-01": [
        {"title": "Day 1 - Morning Activity", "description": "Explore...", "location": null},
        {"title": "Day 1 - Lunch", "description": "Try local cuisine...", "location": null},
        {"title": "Day 1 - Afternoon Activity", "description": "Visit a museum...", "location": null},
        {"title": "Day 1 - Dinner", "description": "Enjoy dinner...", "location": null}
    ],
    "2024-06-02": [
        ...
    ],
    "2024-06-03": [
        ...
    ]
}
```

### Adventure Template
```json
{
    "2024-06-01": [
        {"title": "Day 1 - Early Morning Adventure", "description": "Start with an outdoor activity...", "location": null},
        {"title": "Day 1 - Mid-day Challenge", "description": "Engage in an exciting activity...", "location": null},
        {"title": "Day 1 - Evening Activity", "description": "Explore local nightlife...", "location": null}
    ]
}
```

### Relaxation Template
```json
{
    "2024-06-01": [
        {"title": "Day 1 - Leisurely Morning", "description": "Sleep in and enjoy breakfast...", "location": null},
        {"title": "Day 1 - Spa or Wellness", "description": "Indulge in a spa treatment...", "location": null},
        {"title": "Day 1 - Leisure Time", "description": "Enjoy reading or shopping...", "location": null},
        {"title": "Day 1 - Scenic Dinner", "description": "Dine at a scenic restaurant...", "location": null}
    ]
}
```

### Cultural Template
```json
{
    "2024-06-01": [
        {"title": "Day 1 - Historical Tour", "description": "Visit historical sites...", "location": null},
        {"title": "Day 1 - Museum Visit", "description": "Explore world-class museums...", "location": null},
        {"title": "Day 1 - Local Culture", "description": "Participate in a local cultural activity...", "location": null},
        {"title": "Day 1 - Traditional Dining", "description": "Experience traditional cuisine...", "location": null}
    ]
}
```

---

## Error Handling

### Common Errors

| Error | Status | Cause | Solution |
|-------|--------|-------|----------|
| Trip not found | 404 | Invalid trip ID | Verify trip exists |
| Access denied | 403 | Not trip owner | Use your own trip ID |
| Invalid template_type | 400 | Unsupported type | Use: standard, adventure, relaxation, cultural |
| Invalid date format | 400 | Wrong date format | Use ISO format: YYYY-MM-DD |
| Start date after end date | 400 | Date range invalid | Ensure start_date < end_date |
| Unauthorized | 401 | Missing/invalid token | Include valid JWT token |

---

## Workflow Example

### Complete Trip Planning Workflow

1. **Create Trip**
   ```bash
   POST /api/trips
   {
       "destination": "Tokyo",
       "start_date": "2024-07-01T00:00:00Z",
       "end_date": "2024-07-05T00:00:00Z",
       "latitude": 35.6762,
       "longitude": 139.6503
   }
   ```

2. **Generate Template** (Choose one)
   ```bash
   POST /api/trips/1/itinerary/generate
   {"template_type": "standard"}  # or adventure, relaxation, cultural
   ```

3. **Review Generated Itinerary**
   ```bash
   GET /api/trips/1
   # Check the itinerary field in response
   ```

4. **Customize with Activities**
   ```bash
   POST /api/trips/1/itinerary
   {
       "date": "2024-07-02",
       "title": "Senso-ji Temple",
       "description": "Visit the historic Buddhist temple",
       "location": "2 Chome Asakusa, Taito, Tokyo"
   }
   ```

5. **Update Trip**
   ```bash
   PUT /api/trips/1
   {
       "itinerary": {...updated itinerary...}
   }
   ```

---

## Best Practices

1. **Start with a Template**: Generate a default template first, then customize
2. **Add Specific Locations**: Update placeholder activities with real location details
3. **Validate Before Saving**: Always validate itinerary structure before database commit
4. **Regular Updates**: Update the `updated_at` timestamp when modifying itineraries
5. **Backup Original**: Keep original generated template as reference
6. **Use Proper Dates**: Always use ISO format (YYYY-MM-DD or ISO 8601)

---

## Troubleshooting

### Issue: Token Expired
**Solution**: Generate a new access token using the refresh token endpoint

### Issue: Activities Not Saving
**Solution**: Ensure you call `db.session.commit()` after modifications

### Issue: Template Generated but Itinerary Empty
**Solution**: Verify start_date and end_date are correct and in proper format

### Issue: Custom Activities Not Persisting
**Solution**: Make sure the date format matches (YYYY-MM-DD) and activity has required fields

---

## Future Enhancements

- [ ] Export itinerary to PDF/calendar
- [ ] Share itineraries with other users
- [ ] Collaborative itinerary editing
- [ ] Integration with Google Maps/Places
- [ ] Estimated time for activities
- [ ] Budget tracking per activity
- [ ] Photo/media attachment to activities
- [ ] Weather forecasts for trip dates
- [ ] Smart recommendations based on destination

---

## Summary

The Itinerary Generation feature streamlines trip planning by:
- ✅ Generating pre-filled templates in seconds
- ✅ Supporting multiple travel styles
- ✅ Managing daily activities easily
- ✅ Validating data structure
- ✅ Integrating seamlessly with Trip CRUD operations

Start generating your first itinerary template today!
