# Smart Parking Finder & Management System - Member 1 (User & Location Module)

A modern, responsive web application for finding available parking spots in Chennai and reserving slots with real-time status tracking, built with **Streamlit**, **FastAPI**, **SQLAlchemy 2.0**, and **MySQL (`smart_parking_db`)**.

---

## 📁 Project Architecture & Directory Structure

```text
smart_parking_system/
├── backend/
│   ├── main.py                  # FastAPI app entry point, CORS, and modular router registration
│   ├── database.py              # MySQL connection & session management via SQLAlchemy
│   ├── models.py                # Complete SQLAlchemy ORM models (5 shared tables)
│   ├── schemas.py               # Pydantic v2 validation & response schemas
│   ├── routers/
│   │   ├── auth.py              # User Registration & Login (/api/auth/register, /api/auth/login)
│   │   ├── user.py              # User Profile & Dashboard (/api/user/profile, /api/user/dashboard)
│   │   ├── parking.py           # Parking Search & Slot Availability (/api/parking, /api/parking/{id}/slots)
│   │   └── booking.py           # Bookings & Sessions (/api/bookings, /api/sessions/check-in, check-out)
│   └── services/
│       ├── auth_service.py      # Password hashing (bcrypt), JWT generation & user auth dependency
│       ├── location_service.py  # Chennai areas coordinates registry & Haversine distance calculator
│       └── booking_service.py   # Transactional slot reservation, conflict check, check-in, check-out
│
├── frontend/
│   ├── app.py                   # Main Streamlit entry point, custom CSS theme, and session router
│   ├── pages/
│   │   ├── login.py             # User Sign In and Registration forms
│   │   ├── user_dashboard.py    # KPI stat cards, active booking actions, quick navigation
│   │   ├── parking_search.py    # Area search, proximity sorting, filters, facility cards & slot viewer
│   │   ├── booking.py           # Slot reservation flow, duration picker & fee estimate
│   │   ├── my_bookings.py       # My Bookings, Check-in / Check-out actions, session history
│   │   └── profile.py           # User account details and activity summary
│   └── components/
│       ├── api_client.py        # Centralized HTTP client communicating with FastAPI REST backend
│       ├── cards.py             # Reusable UI components (Parking cards, slot grid, KPI stat tiles)
│       ├── tables.py            # Booking & session history tables with colored status badges
│       └── navigation.py        # Sidebar navigation, user header status, and logout button
│
├── database/
│   ├── schema.sql               # MySQL DDL for smart_parking_db (5 tables, constraints, FKs)
│   └── seed_data.sql            # Chennai parking locations, slots, and test accounts
│
├── tests/
│   └── test_backend.py          # Automated backend test suite
│
├── .env.example                 # Environment template
├── .env                         # Local environment configuration
├── requirements.txt             # Python dependencies
└── README.md                    # Documentation and execution guide
```

---

## ⚙️ Prerequisites & Setup

### 1. Configure Environment Variables
Ensure the `.env` file in the project root has your MySQL configuration:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=smart_parking_db

SECRET_KEY=smart_parking_jwt_super_secret_key_chennai_2026_secure
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

API_BASE_URL=http://127.0.0.1:8000
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Application

To run the complete system, launch the **FastAPI backend** in one terminal and the **Streamlit frontend** in a second terminal.

### Step 1: Start the FastAPI Backend
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- **Backend API**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Step 2: Start the Streamlit Frontend
```bash
streamlit run frontend/app.py
```
- **Streamlit Web UI**: [http://localhost:8501](http://localhost:8501)

---

## 👤 Test Accounts for Quick Demo

Pre-configured seed accounts (all use password: `password123`):
- **User 1**: `john@example.com`
- **User 2**: `priya@example.com`

---

## 🧪 Running Automated Backend Tests

```bash
python tests/test_backend.py
```
This script tests:
1. System health check & MySQL connection.
2. User authentication, login, registration, duplicate checks, and password verification.
3. User profile and dashboard statistics aggregation.
4. Area parking search with Haversine distance calculations and nearest-proximity sorting.
5. Real-time slot availability queries (`available`, `occupied`, `reserved`, `maintenance`).
6. Slot booking, transactional conflict prevention (double-booking prevention).
7. Self-service Check-in (`reserved` $\rightarrow$ `occupied`) and Check-out (`occupied` $\rightarrow$ `available`).
8. Reservation cancellation and automatic slot release.
