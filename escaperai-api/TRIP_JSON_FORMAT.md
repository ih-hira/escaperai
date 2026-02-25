# Trip JSON Format Reference

## Create New Trip

### Endpoint
```
POST /api/trips
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Request Format

**Minimal (Required fields only):**
```json
{
    "destination": "Paris",
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-06-15T00:00:00Z"
}
```

**Complete (All optional fields):**
```json
{
    "destination": "Paris",
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-06-15T00:00:00Z",
    "latitude": 48.8566,
    "longitude": 2.3522,
    "itinerary": {
        "2024-06-05": [
            {
                "title": "Eiffel Tower",
                "description": "Visit and climb the Eiffel Tower",
                "location": "5 Avenue Anatole France, 75007 Paris"
            }
        ]
    }
}
```

### Field Descriptions

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `destination` | string | ✓ | Trip destination name | `"Tokyo"`, `"New York"` |
| `start_date` | string (ISO 8601) | ✓ | Trip start date/time | `"2024-07-01T00:00:00Z"` |
| `end_date` | string (ISO 8601) | ✓ | Trip end date/time | `"2024-07-15T00:00:00Z"` |
| `latitude` | float | ✗ | Geographic latitude | `35.6762` |
| `longitude` | float | ✗ | Geographic longitude | `139.6503` |
| `itinerary` | object | ✗ | Daily itinerary items | See itinerary format below |

### Response Format

**Success (201 Created):**
```json
{
    "success": true,
    "data": {
        "id": 2,
        "user_id": 123,
        "destination": "Paris",
        "start_date": "2024-06-01T00:00:00+00:00",
        "end_date": "2024-06-15T00:00:00+00:00",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "itinerary": {},
        "created_at": "2024-02-25T10:30:00+00:00",
        "updated_at": "2024-02-25T10:30:00+00:00"
    }
}
```

**Error - Missing Required Fields (400 Bad Request):**
```json
{
    "success": false,
    "error": "Missing required fields",
    "missing": ["start_date", "end_date"]
}
```

**Error - Invalid Date Format (400 Bad Request):**
```json
{
    "success": false,
    "error": "Invalid date format. Use ISO format (e.g., 2024-07-01T00:00:00Z)"
}
```

**Error - Invalid Date Range (400 Bad Request):**
```json
{
    "success": false,
    "error": "Start date must be before end date"
}
```

---

## Update Existing Trip

### Endpoint
```
PUT /api/trips/<trip_id>
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Request Format

**Update Single Field:**
```json
{
    "destination": "London"
}
```

**Update Multiple Fields:**
```json
{
    "destination": "London",
    "latitude": 51.5074,
    "longitude": -0.1278
}
```

**Update Entire Trip:**
```json
{
    "destination": "London",
    "start_date": "2024-08-01T00:00:00Z",
    "end_date": "2024-08-10T00:00:00Z",
    "latitude": 51.5074,
    "longitude": -0.1278
}
```

### Response Format

**Success (200 OK):**
```json
{
    "success": true,
    "data": {
        "id": 2,
        "user_id": 123,
        "destination": "London",
        "start_date": "2024-08-01T00:00:00+00:00",
        "end_date": "2024-08-10T00:00:00+00:00",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "itinerary": {},
        "created_at": "2024-02-25T10:30:00+00:00",
        "updated_at": "2024-02-25T10:45:00+00:00"
    }
}
```

**Error - Trip Not Found (404 Not Found):**
```json
{
    "success": false,
    "error": "Trip not found"
}
```

**Error - Access Denied (403 Forbidden):**
```json
{
    "success": false,
    "error": "Access denied. You do not own this trip."
}
```

---

## Add Itinerary Item

### Endpoint
```
POST /api/trips/<trip_id>/itinerary
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Request Format

**Minimal (Required fields only):**
```json
{
    "date": "2024-06-05",
    "title": "Eiffel Tower Visit",
    "description": "Climb to the top and enjoy the views"
}
```

**Complete (With location):**
```json
{
    "date": "2024-06-05",
    "title": "Eiffel Tower Visit",
    "description": "Climb to the top and enjoy the views",
    "location": "5 Avenue Anatole France, 75007 Paris, France"
}
```

### Field Descriptions

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `date` | string (ISO 8601 date) | ✓ | Activity date | `"2024-06-05"` |
| `title` | string | ✓ | Activity title | `"Museum visit"` |
| `description` | string | ✓ | Activity description | `"Visit the Louvre"` |
| `location` | string | ✗ | Activity location | `"Rue de Rivoli, Paris"` |

### Response Format

**Success (200 OK):**
```json
{
    "success": true,
    "data": {
        "id": 2,
        "user_id": 123,
        "destination": "Paris",
        "start_date": "2024-06-01T00:00:00+00:00",
        "end_date": "2024-06-15T00:00:00+00:00",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "itinerary": {
            "2024-06-05": [
                {
                    "title": "Eiffel Tower Visit",
                    "description": "Climb to the top and enjoy the views",
                    "location": "5 Avenue Anatole France, 75007 Paris, France"
                }
            ]
        },
        "created_at": "2024-02-25T10:30:00+00:00",
        "updated_at": "2024-02-25T10:45:00+00:00"
    }
}
```

**Error - Missing Required Fields (400 Bad Request):**
```json
{
    "success": false,
    "error": "Missing required fields",
    "missing": ["description"]
}
```

**Error - Invalid Date Format (400 Bad Request):**
```json
{
    "success": false,
    "error": "Invalid date format. Use ISO format (e.g., 2024-06-05)"
}
```

---

## Date/Time Format

### ISO 8601 Format (Required)

All dates must be in ISO 8601 format. The API accepts with or without timezone:

**Full datetime (with time and timezone):**
```
2024-07-01T14:30:00Z          # UTC (Z = Zulu time)
2024-07-01T14:30:00+00:00     # UTC with offset
2024-07-01T10:30:00-04:00     # EDT (UTC-4)
```

**Date only (for itinerary items):**
```
2024-06-05
```

### Examples

✓ Valid formats:
```json
{
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-06-15T23:59:59Z"
}
```

✗ Invalid formats:
```json
{
    "start_date": "06/01/2024",           // Wrong format
    "start_date": "2024-06-01",           // No time
    "start_date": "June 1, 2024"          // Text format
}
```

---

## Coordinate Format

### Latitude / Longitude

Coordinates use standard geographic format (WGS84):

| Coordinate | Range | Format | Examples |
|----------|-------|--------|----------|
| Latitude | -90 to +90 | Decimal degrees | `48.8566`, `51.5074`, `-33.8688` |
| Longitude | -180 to +180 | Decimal degrees | `2.3522`, `-0.1278`, `151.2093` |

### Examples

**Paris:**
```json
{
    "latitude": 48.8566,
    "longitude": 2.3522
}
```

**London:**
```json
{
    "latitude": 51.5074,
    "longitude": -0.1278
}
```

**Tokyo:**
```json
{
    "latitude": 35.6762,
    "longitude": 139.6503
}
```

**Sydney:**
```json
{
    "latitude": -33.8688,
    "longitude": 151.2093
}
```

---

## Complete Examples

### Example 1: Simple Paris Trip

**Request:**
```bash
curl -X POST http://localhost:5000/api/trips \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Paris",
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-06-15T00:00:00Z"
  }'
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "user_id": 123,
        "destination": "Paris",
        "start_date": "2024-06-01T00:00:00+00:00",
        "end_date": "2024-06-15T00:00:00+00:00",
        "latitude": null,
        "longitude": null,
        "itinerary": {},
        "created_at": "2024-02-25T10:30:00+00:00",
        "updated_at": "2024-02-25T10:30:00+00:00"
    }
}
```

---

### Example 2: Tokyo Trip with Coordinates

**Request:**
```bash
curl -X POST http://localhost:5000/api/trips \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Tokyo",
    "start_date": "2024-07-01T00:00:00Z",
    "end_date": "2024-07-15T00:00:00Z",
    "latitude": 35.6762,
    "longitude": 139.6503
  }'
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 2,
        "user_id": 123,
        "destination": "Tokyo",
        "start_date": "2024-07-01T00:00:00+00:00",
        "end_date": "2024-07-15T00:00:00+00:00",
        "latitude": 35.6762,
        "longitude": 139.6503,
        "itinerary": {},
        "created_at": "2024-02-25T10:35:00+00:00",
        "updated_at": "2024-02-25T10:35:00+00:00"
    }
}
```

---

### Example 3: Update Trip with New Destination

**Request:**
```bash
curl -X PUT http://localhost:5000/api/trips/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Barcelona",
    "latitude": 41.3851,
    "longitude": 2.1734
  }'
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "user_id": 123,
        "destination": "Barcelona",
        "start_date": "2024-06-01T00:00:00+00:00",
        "end_date": "2024-06-15T00:00:00+00:00",
        "latitude": 41.3851,
        "longitude": 2.1734,
        "itinerary": {},
        "created_at": "2024-02-25T10:30:00+00:00",
        "updated_at": "2024-02-25T10:50:00+00:00"
    }
}
```

---

### Example 4: Add Itinerary Item

**Request:**
```bash
curl -X POST http://localhost:5000/api/trips/1/itinerary \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-06-05",
    "title": "Sagrada Familia Tour",
    "description": "Visit the famous basilica designed by Gaudí",
    "location": "Carrer de Mallorca, 401, Barcelona"
  }'
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "user_id": 123,
        "destination": "Barcelona",
        "start_date": "2024-06-01T00:00:00+00:00",
        "end_date": "2024-06-15T00:00:00+00:00",
        "latitude": 41.3851,
        "longitude": 2.1734,
        "itinerary": {
            "2024-06-05": [
                {
                    "title": "Sagrada Familia Tour",
                    "description": "Visit the famous basilica designed by Gaudí",
                    "location": "Carrer de Mallorca, 401, Barcelona"
                }
            ]
        },
        "created_at": "2024-02-25T10:30:00+00:00",
        "updated_at": "2024-02-25T10:55:00+00:00"
    }
}
```

---

### Example 5: Multiple Itinerary Items in One Day

**Request:**
```bash
curl -X POST http://localhost:5000/api/trips/1/itinerary \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-06-05",
    "title": "Park Güell Visit",
    "description": "Explore Gaudí's stunning park with panoramic views",
    "location": "Carrer d\"Olot, Barcelona"
  }'
```

**Response (itinerary updated with multiple items on same date):**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "destination": "Barcelona",
        "itinerary": {
            "2024-06-05": [
                {
                    "title": "Sagrada Familia Tour",
                    "description": "Visit the famous basilica designed by Gaudí",
                    "location": "Carrer de Mallorca, 401, Barcelona"
                },
                {
                    "title": "Park Güell Visit",
                    "description": "Explore Gaudí's stunning park with panoramic views",
                    "location": "Carrer d'Olot, Barcelona"
                }
            ]
        }
    }
}
```

---

## Common Errors and Solutions

### Error 1: Missing Authorization Header
```
Status: 401 Unauthorized
Response: { "error": "Authorization required. Missing token." }
Solution: Add Authorization header: Authorization: Bearer <token>
```

### Error 2: Invalid Date Format
```
Status: 400 Bad Request
Response: { "error": "Invalid date format. Use ISO format (e.g., 2024-07-01T00:00:00Z)" }
Solution: Use ISO 8601 format with Z suffix: "2024-07-01T00:00:00Z"
```

### Error 3: Start Date After End Date
```
Status: 400 Bad Request
Response: { "error": "Start date must be before end date" }
Solution: Ensure start_date < end_date
```

### Error 4: Access Denied (Not Owner)
```
Status: 403 Forbidden
Response: { "error": "Access denied. You do not own this trip." }
Solution: Use a valid token for the trip owner
```

### Error 5: Trip Not Found
```
Status: 404 Not Found
Response: { "error": "Trip not found" }
Solution: Verify the trip ID is correct and belongs to the user
```

---

## Testing with Different Tools

### Using curl

```bash
# Create trip
curl -X POST http://localhost:5000/api/trips \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"destination":"Paris","start_date":"2024-06-01T00:00:00Z","end_date":"2024-06-15T00:00:00Z"}'

# Get all trips
curl -H "Authorization: Bearer eyJhbGc..." \
  http://localhost:5000/api/trips

# Update trip
curl -X PUT http://localhost:5000/api/trips/1 \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"destination":"London"}'

# Delete trip
curl -X DELETE http://localhost:5000/api/trips/1 \
  -H "Authorization: Bearer eyJhbGc..."
```

### Using VS Code REST Client

Create a file named `requests.http`:

```rest
@host = http://localhost:5000
@token = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

### Create trip
POST {{host}}/api/trips
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "destination": "Paris",
  "start_date": "2024-06-01T00:00:00Z",
  "end_date": "2024-06-15T00:00:00Z",
  "latitude": 48.8566,
  "longitude": 2.3522
}

### Get all trips
GET {{host}}/api/trips
Authorization: Bearer {{token}}

### Get specific trip
GET {{host}}/api/trips/1
Authorization: Bearer {{token}}

### Update trip
PUT {{host}}/api/trips/1
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "destination": "Barcelona"
}

### Add itinerary item
POST {{host}}/api/trips/1/itinerary
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "date": "2024-06-05",
  "title": "Museum Visit",
  "description": "Visit local museum",
  "location": "Museum Street"
}

### Delete trip
DELETE {{host}}/api/trips/1
Authorization: Bearer {{token}}
```

### Using Postman

1. Create a new POST request
2. Set URL: `http://localhost:5000/api/trips`
3. Add header: `Authorization: Bearer <token>`
4. Set body (raw JSON):
   ```json
   {
       "destination": "Paris",
       "start_date": "2024-06-01T00:00:00Z",
       "end_date": "2024-06-15T00:00:00Z"
   }
   ```
5. Send request

---

## Summary Table

| Operation | Method | Endpoint | Required Fields |
|-----------|--------|----------|-----------------|
| Create Trip | POST | `/api/trips` | destination, start_date, end_date |
| List Trips | GET | `/api/trips` | (none) |
| Get Trip | GET | `/api/trips/<id>` | (none) |
| Update Trip | PUT | `/api/trips/<id>` | (partial update OK) |
| Delete Trip | DELETE | `/api/trips/<id>` | (none) |
| Add Itinerary | POST | `/api/trips/<id>/itinerary` | date, title, description |
