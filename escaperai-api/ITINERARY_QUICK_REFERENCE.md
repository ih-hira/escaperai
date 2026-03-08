# Itinerary Generation - Quick Reference

## 🚀 Quick Start

### Generate Default Itinerary (API)
```bash
# Create a trip first
curl -X POST http://localhost:5000/api/trips \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"destination":"Paris","start_date":"2024-06-01T00:00:00Z","end_date":"2024-06-05T00:00:00Z"}'

# Then generate template
curl -X POST http://localhost:5000/api/trips/1/itinerary/generate \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template_type":"standard"}'
```

### Generate Default Itinerary (Python)
```python
from utils.itinerary_utils import generate_default_itinerary
from datetime import datetime

itinerary = generate_default_itinerary(
    destination='Paris',
    start_date=datetime(2024, 6, 1),
    end_date=datetime(2024, 6, 5),
    template_type='standard'
)
```

### Using Trip Model
```python
from models import Trip
from database import db

trip = Trip.query.get(1)
trip.generate_default_itinerary('standard')
db.session.commit()
```

---

## 📋 Template Types

| Type | Use Case | Activities |
|------|----------|-----------|
| **standard** | General trips | Morning, Lunch, Afternoon, Dinner |
| **adventure** | Active travelers | Early morning, Mid-day, Evening |
| **relaxation** | Leisure trips | Leisure, Spa, Wellness, Scenic dining |
| **cultural** | Museums, history | Historical, Museum, Cultural, Traditional |

---

## 🔧 Core Functions

### Generate Itinerary
```python
generate_default_itinerary(
    destination: str,
    start_date: datetime,
    end_date: datetime,
    template_type: str = 'standard'
) -> Dict
```

### Add Activity
```python
add_activity_to_itinerary(
    itinerary: Dict,
    date: str,  # ISO format: '2024-06-01'
    title: str,
    description: str,
    location: str = None
) -> Dict
```

### Remove Activity
```python
remove_activity_from_itinerary(
    itinerary: Dict,
    date: str,  # ISO format: '2024-06-01'
    activity_index: int
) -> Dict
```

### Utilities
```python
get_trip_duration(start_date, end_date) -> int
get_activities_count(itinerary) -> int
get_date_range(start_date, end_date) -> List[datetime]
validate_itinerary_structure(itinerary) -> bool
```

---

## 📍 API Endpoints

### Generate Template
```
POST /api/trips/<trip_id>/itinerary/generate
```
**Body (optional):** `{"template_type": "standard"}`  
**Response:** Trip with generated itinerary

### Add Activity
```
POST /api/trips/<trip_id>/itinerary
```
**Body:** 
```json
{
    "date": "2024-06-01",
    "title": "Activity Title",
    "description": "Activity description",
    "location": "Optional location"
}
```

### Get Trip
```
GET /api/trips/<trip_id>
```
**Response:** Trip details including itinerary

### Update Trip
```
PUT /api/trips/<trip_id>
```
**Body:** Can include updated itinerary object

---

## 📊 Itinerary Structure

```json
{
    "2024-06-01": [
        {
            "title": "Morning Activity",
            "description": "Activity description",
            "location": "Optional location"
        },
        {
            "title": "Lunch",
            "description": "Try local cuisine",
            "location": null
        }
    ],
    "2024-06-02": [...]
}
```

---

## ✅ Validations

- **Date Format**: ISO 8601 (YYYY-MM-DD or full ISO format)
- **Template Type**: standard | adventure | relaxation | cultural
- **Required Fields**: title, description
- **Optional Fields**: location
- **Date Range**: start_date < end_date

---

## 🐛 Error Codes

| Code | Issue | Fix |
|------|-------|-----|
| 404 | Trip not found | Verify trip ID |
| 403 | Not trip owner | Use own trip ID |
| 400 | Invalid template type | Use valid type |
| 400 | Invalid date format | Use ISO format |
| 401 | Unauthorized | Provide JWT token |

---

## 📝 Workflow

```
1. Create Trip → 2. Generate Template → 3. View Itinerary
   ↓              ↓                     ↓
POST /api/trips   POST /itinerary/     GET /api/trips/<id>
                  generate             

4. Add Activities → 5. Update Trip (if needed)
   ↓
POST /api/trips/<id>/itinerary
```

---

## 💡 Tips

✅ **Do's:**
- Start with a template, then customize
- Validate itinerary before saving
- Use proper date format
- Save with `db.session.commit()`
- Add specific locations to activities

❌ **Don'ts:**
- Don't skip authentication
- Don't mix date formats
- Don't forget to commit changes
- Don't use invalid template types
- Don't forget location context

---

## 📚 Documentation Files

- **ITINERARY_GENERATION_GUIDE.md** - Full documentation
- **itinerary_examples.py** - Code examples
- **TRIP_JSON_FORMAT.md** - Trip JSON reference

---

## 🔗 Imports

```python
from utils.itinerary_utils import (
    generate_default_itinerary,
    get_date_range,
    add_activity_to_itinerary,
    remove_activity_from_itinerary,
    get_trip_duration,
    get_activities_count,
    validate_itinerary_structure,
)

# Or from models
from models import Trip
```

---

## 🚀 Example: Full Workflow

```python
from models import Trip
from datetime import datetime
from database import db

# 1. Get trip
trip = Trip.query.get(1)

# 2. Generate template
trip.generate_default_itinerary('adventure')

# 3. Add custom activity
trip.add_itinerary_item(
    date=datetime(2024, 6, 2),
    title='Climbing',
    description='Rock climbing adventure',
    location='Mountain rock face'
)

# 4. Save
db.session.commit()

# 5. View
print(trip.to_dict())
```

---

## 🆘 Troubleshooting

**Itinerary not generating?**
- Check start_date < end_date
- Verify datetime objects are proper format
- Ensure database session is active

**Activities not saving?**
- Call `db.session.commit()`
- Check date format is ISO (YYYY-MM-DD)
- Verify trip exists and you own it

**API returns 403?**
- Make sure it's your trip
- Check JWT token is valid

**API returns 400?**
- Verify JSON format
- Check all required fields present
- Validate template_type value

---

**Last Updated:** 2024  
**Version:** 1.0
