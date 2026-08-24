# Smart Parking Finder & Management System
## Common Database Schema

### Purpose
This file defines the single MySQL database structure that all 3 team members must use.

### Database
Database name:
`smart_parking_db`

### Important Rule
All team members must use the same table names, column names, primary keys and foreign keys.

Do NOT create duplicate or differently named tables.

---

## 1. users

Stores user and admin accounts.

Columns:
- user_id INT PRIMARY KEY AUTO_INCREMENT
- name VARCHAR(100) NOT NULL
- email VARCHAR(150) UNIQUE NOT NULL
- password VARCHAR(255) NOT NULL
- phone VARCHAR(20)
- role ENUM('user','admin','manager') DEFAULT 'user'
- status ENUM('active','inactive') DEFAULT 'active'
- created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

---

## 2. parking_locations

Stores actual parking locations collected beforehand.

Columns:
- parking_id INT PRIMARY KEY AUTO_INCREMENT
- parking_name VARCHAR(150) NOT NULL
- area VARCHAR(100) NOT NULL
- address VARCHAR(255)
- latitude DECIMAL(10,7)
- longitude DECIMAL(10,7)
- total_slots INT DEFAULT 0
- parking_fee DECIMAL(10,2) DEFAULT 0
- opening_time TIME
- closing_time TIME
- ev_available BOOLEAN DEFAULT FALSE
- accessible_available BOOLEAN DEFAULT FALSE
- status ENUM('active','inactive') DEFAULT 'active'
- created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

---

## 3. parking_slots

Stores individual parking slots.

Columns:
- slot_id INT PRIMARY KEY AUTO_INCREMENT
- parking_id INT NOT NULL
- slot_number VARCHAR(20) NOT NULL
- slot_type ENUM('normal','ev','accessible') DEFAULT 'normal'
- status ENUM('available','occupied','reserved','maintenance') DEFAULT 'available'
- FOREIGN KEY (parking_id) REFERENCES parking_locations(parking_id)
- UNIQUE(parking_id, slot_number)

---

## 4. bookings

Stores user parking reservations.

Columns:
- booking_id INT PRIMARY KEY AUTO_INCREMENT
- user_id INT NOT NULL
- parking_id INT NOT NULL
- slot_id INT NOT NULL
- booking_date DATE NOT NULL
- start_time DATETIME NOT NULL
- end_time DATETIME NOT NULL
- status ENUM('reserved','cancelled','completed','active') DEFAULT 'reserved'
- created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- FOREIGN KEY (user_id) REFERENCES users(user_id)
- FOREIGN KEY (parking_id) REFERENCES parking_locations(parking_id)
- FOREIGN KEY (slot_id) REFERENCES parking_slots(slot_id)

---

## 5. parking_sessions

Stores actual parking check-in/check-out sessions.

Columns:
- session_id INT PRIMARY KEY AUTO_INCREMENT
- booking_id INT NOT NULL
- user_id INT NOT NULL
- parking_id INT NOT NULL
- slot_id INT NOT NULL
- check_in DATETIME
- check_out DATETIME
- status ENUM('active','completed') DEFAULT 'active'
- FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
- FOREIGN KEY (user_id) REFERENCES users(user_id)
- FOREIGN KEY (parking_id) REFERENCES parking_locations(parking_id)
- FOREIGN KEY (slot_id) REFERENCES parking_slots(slot_id)

---

# Relationships

users
  |
  | 1-to-many
  ↓
bookings
  |
  | many-to-1
  ↓
parking_locations
  |
  | 1-to-many
  ↓
parking_slots

bookings
  |
  | 1-to-1 / one booking can have one parking session
  ↓
parking_sessions

---

# Common Slot Status Rules

available → reserved
reserved → occupied
occupied → available
available → maintenance
maintenance → available

Cancelled reservation:
reserved → available

---

# Common Booking Rules

1. User can book only an available slot.
2. Occupied/reserved/maintenance slots cannot be newly booked.
3. On successful booking, slot status becomes `reserved`.
4. On check-in, slot status becomes `occupied`.
5. On check-out, slot status becomes `available`.
6. On valid cancellation before check-in, slot status becomes `available`.
7. All booking and status changes must be stored in MySQL.

---

# Sample Parking Data

Use real parking locations collected beforehand, but keep slot availability and booking data as project-controlled data.

Example parking records can include:
- Parking name
- Area
- Address
- Latitude
- Longitude

Do not claim that slot availability is real-time sensor data.

---

# Security Notes

- Never display passwords in dashboards.
- Do not store unnecessary personal information.
- Validate user input.
- Use parameterized SQL / SQLAlchemy queries.
