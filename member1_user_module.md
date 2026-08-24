# Smart Parking Finder & Management System
## Member 1 – User & Location Module

### Project Overview
Build the User-side module of a Smart Parking Finder & Management System.

The application allows users to select a location, find nearby parking locations from stored parking data, view parking details and available slots, and book parking slots.

### Technology
- Python
- Streamlit
- FastAPI
- MySQL
- Uvicorn
- VS Code / PyCharm

### Responsibilities

#### 1. User Registration & Login
Create:
- Registration page
- Login page
- Logout functionality
- Basic validation

Store user details in MySQL.

#### 2. Location Selection
Allow the user to:
- Search/select an area manually.
- Example: Guindy, Tambaram, T Nagar.
- Use the selected location to find nearby parking locations.

Do not implement automatic GPS detection in the first version.

#### 3. Parking Search
Display parking locations related to the selected area.

Show:
- Parking name
- Area
- Distance
- Total slots
- Available slots
- Parking fee
- EV availability
- Accessibility availability

#### 4. Parking Details
When the user selects a parking location, show its complete details and current slot status.

Slot status:
- Available
- Occupied
- Reserved
- Maintenance

#### 5. Slot Booking
Allow the user to:
- Select an available slot.
- Select required parking duration.
- Confirm booking.
- Store booking in MySQL.

Do not allow booking of occupied, reserved or maintenance slots.

#### 6. Booking Management
Create a "My Bookings" section.

Show:
- Booking ID
- Parking name
- Slot number
- Booking date
- Start time
- End time
- Status

Allow the user to cancel an eligible booking.

#### 7. Check-in / Check-out
Allow the user to:
- Check in when arriving.
- Check out when leaving.

After check-in:
Reserved → Occupied

After check-out:
Occupied → Available

#### 8. User Dashboard
Create a simple dashboard containing:
- Nearby parking count
- Current booking
- Available parking slots
- Booking history
- Recent booking status

### Backend APIs
Create/use FastAPI endpoints for:
- User registration
- User login
- Parking search
- Parking details
- Slot availability
- Booking
- Booking cancellation
- Check-in
- Check-out
- User dashboard

### Database
Use the shared project MySQL database.

Do not create duplicate tables if they already exist.

Expected tables:
- users
- parking_locations
- parking_slots
- bookings
- parking_sessions

Use proper primary keys and foreign keys.

### Integration Rules
- Keep API routes modular.
- Do not hard-code booking data in Streamlit.
- Streamlit must communicate with FastAPI.
- FastAPI must communicate with MySQL.
- Do not modify Admin functionality unnecessarily.
- Use clear variable and function names.
- Keep the UI simple and clean.

### Expected Result
A registered user should be able to:

Login
→ Select location
→ View nearby parking
→ View available slots
→ Select slot
→ Book slot
→ View booking in dashboard
→ Check-in
→ Check-out

Build only the User & Location module.
