# Smart Parking Finder & Management System
## Member 2 – Parking & Slot Management Module

### Project Overview
Build the Parking and Slot Management module.

This module manages parking locations, parking slots, slot status, parking details, and check-in/check-out status.

### Technology
- Python
- FastAPI
- Streamlit
- MySQL
- Uvicorn
- VS Code / PyCharm

### Responsibilities

#### 1. Parking Location Management
Create functionality to:
- Add parking location
- Edit parking details
- View parking details
- Activate/deactivate parking location

Parking details:
- Parking ID
- Parking name
- Area
- Latitude
- Longitude
- Total slots
- Parking fee
- Opening time
- Closing time
- EV availability
- Accessibility availability

The project will use actual parking locations collected beforehand and stored in MySQL.

Do not implement live parking discovery from external APIs in the first version.

#### 2. Slot Management
Create parking slots for each parking location.

Each slot should have:
- Slot ID
- Parking ID
- Slot number
- Slot type
- Status

Slot types:
- Normal
- EV
- Accessible

Slot statuses:
- Available
- Occupied
- Reserved
- Maintenance

#### 3. Slot Status Update
Allow authorized management users to update slot status.

Examples:
- Available → Maintenance
- Available → Reserved
- Reserved → Occupied
- Occupied → Available

Do not allow invalid status transitions where possible.

#### 4. Check-in / Check-out
Support parking session status.

Check-in:
Reserved → Occupied

Check-out:
Occupied → Available

Store:
- Session ID
- Booking ID
- Slot ID
- Check-in time
- Check-out time

#### 5. Parking Management Interface
Create a simple management interface to:
- View parking locations
- View slot layout/status
- Update slot status
- View active parking sessions

### Backend APIs
Create/use FastAPI endpoints for:
- Add parking
- Update parking
- Get parking details
- Get slots
- Add slot
- Update slot status
- Check-in
- Check-out
- Parking session details

### Database
Use the shared MySQL database.

Expected tables:
- parking_locations
- parking_slots
- parking_sessions

Do not create duplicate tables.

Use proper foreign keys.

### Integration Rules
- Do not hard-code slot status in Streamlit.
- All slot status changes must be stored in MySQL.
- User booking module must be able to read the latest slot status.
- Do not modify User Dashboard unnecessarily.
- Keep APIs modular.

### Expected Result
A parking manager should be able to:

Login
→ Select parking
→ View slots
→ See available/occupied/reserved/maintenance slots
→ Update slot status
→ Monitor active parking sessions

Build only the Parking & Slot Management module.
