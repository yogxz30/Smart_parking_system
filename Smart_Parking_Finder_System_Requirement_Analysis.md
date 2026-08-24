# System Requirement Analysis Document

## Project Title

**Smart Parking Finder & Management System**

---

## 2.1 Introduction

Smart Parking Finder & Management System is a web-based application designed to help users find suitable parking locations based on their selected area and view parking slot availability.

The system also provides an administrative interface for managing parking locations, slots, reservations, and parking status.

---

## 2.2 Problem Statement

Traditional parking systems often require users to search manually for parking spaces. Users may not know which nearby parking facility has available spaces, the parking fee, or whether a particular slot is occupied or reserved.

The proposed system provides a centralized platform where users can search for parking and reserve available slots, while parking managers can manage parking facilities and update slot status.

---

## 2.3 Objectives

The main objectives are:

- To help users find nearby parking facilities.
- To display parking availability.
- To allow users to reserve parking slots.
- To reduce unnecessary searching for parking.
- To allow managers to manage parking slots.
- To maintain parking and booking information digitally.
- To provide a simple admin dashboard for monitoring parking status.

---

## 2.4 Scope

The system covers:

- User registration and login
- Manual location selection
- Nearby parking recommendation
- Parking information
- Slot availability
- Slot reservation
- Booking history
- Check-in/check-out
- Parking management
- Slot status management
- Admin dashboard

### Project Limitation

The initial version will not include live sensor-based slot detection or online payment integration.

Slot availability will be maintained based on manager/database updates.

---

## 2.5 Actors

| Actor | Responsibility |
|---|---|
| User | Search, view and book parking slots |
| Admin/Parking Manager | Manage parking, slots and bookings |
| System | Calculate nearby parking and update booking/slot status |

---

## 2.6 Functional Requirements

### FR-01: User Registration

The system shall allow new users to create an account by providing required information such as name, email, phone number and password.

### FR-02: User Login

The system shall allow registered users to securely log in using their credentials.

### FR-03: Location Selection

The system shall allow users to manually select their required area or location.

### FR-04: Nearby Parking Search

The system shall display suitable parking facilities based on the user's selected location.

### FR-05: Parking Information

The system shall display parking details such as:

- Parking name
- Location
- Address
- Parking fee
- Total slots
- Available slots
- Parking status

### FR-06: Slot Availability

The system shall display the current status of parking slots.

Possible slot statuses include:

- Available
- Reserved
- Occupied
- Maintenance

### FR-07: Slot Selection

The system shall allow users to select an available parking slot.

### FR-08: Slot Reservation

The system shall allow users to reserve an available parking slot by providing the required booking details.

### FR-09: Booking Confirmation

The system shall generate and display booking information after a successful reservation.

### FR-10: Booking History

The system shall allow users to view their previous and current parking bookings.

### FR-11: Check-in

The system shall allow users to check in for their confirmed parking reservation.

### FR-12: Check-out

The system shall allow users to check out after completing their parking session.

### FR-13: Slot Status Update

After check-out, the system shall update the corresponding slot status to available.

### FR-14: Parking Management

The Admin/Parking Manager shall be able to:

- Add parking locations
- Update parking information
- Remove parking locations
- View parking facilities

### FR-15: Slot Management

The Admin/Parking Manager shall be able to:

- Add parking slots
- Update slot information
- Change slot status
- Remove parking slots
- View slot availability

### FR-16: Booking Management

The Admin/Parking Manager shall be able to view and manage user bookings.

### FR-17: Admin Dashboard

The system shall provide an admin dashboard displaying important parking information such as:

- Total parking locations
- Total parking slots
- Available slots
- Occupied slots
- Reserved slots
- Total bookings
- Current parking status

### FR-18: Access Control

The system shall restrict admin management functions to authorized Admin/Parking Manager accounts.

### FR-19: Booking Conflict Prevention

The system shall prevent the same parking slot from being assigned to multiple users for the same time period.

### FR-20: Database Storage

The system shall store user, parking, slot and booking information in the MySQL database.

---

## 2.7 High-Level System Flow

```text
User Login
    ↓
Select Location
    ↓
Find Nearby Parking
    ↓
View Parking Details
    ↓
Check Available Slots
    ↓
Select Slot
    ↓
Book Slot
    ↓
Check-in
    ↓
Park Vehicle
    ↓
Check-out
    ↓
Slot Becomes Available
```

---

# 3. Non-Functional Requirements

## 3.1 Performance

- System should respond quickly to user requests.
- Parking and slot information should load without unnecessary delay.

## 3.2 Security

- User passwords should be protected.
- Only authorized admins can access management functions.
- Users should only access their own bookings.

## 3.3 Usability

- Interface should be simple and beginner-friendly.
- Parking status should be clearly displayed.

## 3.4 Reliability

- Booking information should be stored safely.
- Same slot should not be assigned to multiple users for the same time period.

## 3.5 Scalability

System should allow additional parking locations and slots to be added later.

## 3.6 Maintainability

- Backend, frontend and database should be separated.
- Python/FastAPI code should be organized into modules.

---

# 4. Software Requirements

| Component | Technology |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| Backend | FastAPI |
| Database | MySQL |
| API Server | Uvicorn |
| IDE | Antigravity IDE |
| Location Data | OpenStreetMap-based data |
| API Testing | FastAPI Swagger UI / Postman |
| Operating System | Windows |

---

# 5. Main Architecture

```text
┌─────────────────────┐
│      User/Admin     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│     Streamlit UI    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│      FastAPI        │
│     REST APIs       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│       MySQL         │
│       Database      │
└─────────────────────┘
```
