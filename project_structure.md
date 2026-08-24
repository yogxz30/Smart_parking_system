# Smart Parking Finder & Management System
## Common Project Structure

### Purpose
This is the shared project structure for all 3 team members.

All members must follow the same structure so that their modules can be integrated easily.

---

## Recommended Folder Structure

smart_parking/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── parking.py
│   │   ├── booking.py
│   │   └── admin.py
│   │
│   └── services/
│       ├── location_service.py
│       ├── parking_service.py
│       └── booking_service.py
│
├── frontend/
│   ├── app.py
│   ├── pages/
│   │   ├── login.py
│   │   ├── user_dashboard.py
│   │   ├── parking_search.py
│   │   ├── booking.py
│   │   └── admin_dashboard.py
│   │
│   └── components/
│       ├── cards.py
│       ├── tables.py
│       └── navigation.py
│
├── database/
│   ├── schema.sql
│   └── seed_data.sql
│
├── requirements.txt
└── README.md

---

# Responsibilities

## Member 1
Main focus:
- frontend/pages/login.py
- frontend/pages/user_dashboard.py
- frontend/pages/parking_search.py
- frontend/pages/booking.py
- backend/routers/auth.py
- backend/routers/user.py
- backend/routers/booking.py

Responsible for:
- User registration/login
- Location selection
- Parking search
- Parking details
- Slot booking
- My Bookings
- User dashboard

---

## Member 2
Main focus:
- backend/routers/parking.py
- backend/services/parking_service.py
- Parking/slot management UI

Responsible for:
- Parking location management
- Slot management
- Slot status
- Check-in/check-out
- Parking session management

---

## Member 3
Main focus:
- frontend/pages/admin_dashboard.py
- backend/routers/admin.py
- Dashboard/statistics queries

Responsible for:
- Admin login/access
- User monitoring
- Parking monitoring
- Booking monitoring
- Admin dashboard
- Reports/statistics

---

# Shared Backend Rules

### FastAPI
The backend must run through FastAPI.

Example:
`uvicorn backend.main:app --reload`

### Database
FastAPI communicates with MySQL.

Recommended:
- SQLAlchemy
- PyMySQL or mysql-connector-python

Do not let Streamlit directly modify the database when an equivalent FastAPI endpoint exists.

Architecture:

Streamlit
    ↓
FastAPI
    ↓
MySQL

---

# Shared API Naming

Use consistent endpoint names.

### Authentication
POST `/api/auth/register`
POST `/api/auth/login`

### User
GET `/api/user/profile`
GET `/api/user/dashboard`

### Parking
GET `/api/parking`
GET `/api/parking/{parking_id}`
GET `/api/parking/{parking_id}/slots`
POST `/api/parking`
PUT `/api/parking/{parking_id}`

### Slots
POST `/api/slots`
PUT `/api/slots/{slot_id}/status`

### Booking
POST `/api/bookings`
GET `/api/bookings/my`
GET `/api/bookings/{booking_id}`
PUT `/api/bookings/{booking_id}/cancel`

### Parking Session
POST `/api/sessions/check-in`
POST `/api/sessions/check-out`

### Admin
GET `/api/admin/dashboard`
GET `/api/admin/users`
GET `/api/admin/bookings`
GET `/api/admin/parking`

---

# Integration Rules

1. Do not rename shared tables.
2. Do not rename shared primary keys.
3. Do not create duplicate versions of the same table.
4. Reuse existing API endpoints whenever possible.
5. Do not hard-code booking or dashboard statistics.
6. All important data must come from MySQL.
7. Keep Streamlit UI and FastAPI backend separate.
8. Use environment variables for database credentials.
9. Do not commit passwords or API keys to GitHub.
10. Test each module before integration.

---

# Location Approach

The first version does NOT require automatic GPS.

User manually selects/searches an area.

The project may use:
- Actual location names
- Actual mapped parking locations collected beforehand
- Stored latitude/longitude

Nearby parking can be calculated using stored coordinates.

Do not make live parking-slot availability claims.

---

# Integration Flow

User:
Location
→ Nearby parking
→ Select parking
→ View slots
→ Book slot

Database:
Booking created
→ Slot becomes reserved

User:
Check-in
→ Slot becomes occupied

User:
Check-out
→ Slot becomes available

Admin:
Dashboard reads the latest MySQL values.

---

# 4-Day Development Priority

## Day 1
- Database
- FastAPI setup
- Streamlit setup
- Login/register
- Parking data

## Day 2
- Parking search
- Slot display
- User dashboard
- Parking/slot management

## Day 3
- Booking
- Check-in/check-out
- Admin dashboard
- Statistics

## Day 4
- Integration
- Testing
- Bug fixing
- UI improvement
- Demo preparation

---

# Important Scope Limit

Do NOT add these in the first 4-day version:
- Payment gateway
- IoT sensors
- Automatic GPS
- Complex real-time WebSockets
- SMS integration
- Advanced AI prediction

These can be mentioned as future enhancements.
