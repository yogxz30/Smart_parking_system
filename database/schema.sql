-- ==============================================================================
-- Smart Parking Finder & Management System
-- Common Database Schema
-- Database: smart_parking_db
-- ==============================================================================

-- 1. Create and select the database
CREATE DATABASE IF NOT EXISTS smart_parking_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE smart_parking_db;

-- ==============================================================================
-- Table: users
-- Stores registered user, manager, and admin accounts.
-- ==============================================================================
CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role ENUM('user', 'admin', 'manager') DEFAULT 'user',
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ==============================================================================
-- Table: parking_locations
-- Stores parking facility details with geographic coordinates and amenities.
-- ==============================================================================
CREATE TABLE IF NOT EXISTS parking_locations (
    parking_id INT PRIMARY KEY AUTO_INCREMENT,
    parking_name VARCHAR(150) NOT NULL,
    area VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    total_slots INT DEFAULT 0,
    parking_fee DECIMAL(10, 2) DEFAULT 0.00,
    opening_time TIME,
    closing_time TIME,
    ev_available BOOLEAN DEFAULT FALSE,
    accessible_available BOOLEAN DEFAULT FALSE,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ==============================================================================
-- Table: parking_slots
-- Stores individual slots for each parking location with status and slot type.
-- ==============================================================================
CREATE TABLE IF NOT EXISTS parking_slots (
    slot_id INT PRIMARY KEY AUTO_INCREMENT,
    parking_id INT NOT NULL,
    slot_number VARCHAR(20) NOT NULL,
    slot_type ENUM('normal', 'ev', 'accessible') DEFAULT 'normal',
    status ENUM('available', 'occupied', 'reserved', 'maintenance') DEFAULT 'available',
    CONSTRAINT fk_slots_parking FOREIGN KEY (parking_id) 
        REFERENCES parking_locations(parking_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_parking_slot UNIQUE (parking_id, slot_number)
) ENGINE=InnoDB;

-- ==============================================================================
-- Table: bookings
-- Stores reservations created by users for specific parking slots.
-- ==============================================================================
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    parking_id INT NOT NULL,
    slot_id INT NOT NULL,
    booking_date DATE NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    status ENUM('reserved', 'cancelled', 'completed', 'active') DEFAULT 'reserved',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_bookings_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_bookings_parking FOREIGN KEY (parking_id) 
        REFERENCES parking_locations(parking_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_bookings_slot FOREIGN KEY (slot_id) 
        REFERENCES parking_slots(slot_id) 
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ==============================================================================
-- Table: parking_sessions
-- Stores check-in and check-out records for active and completed parking events.
-- ==============================================================================
CREATE TABLE IF NOT EXISTS parking_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT NOT NULL,
    user_id INT NOT NULL,
    parking_id INT NOT NULL,
    slot_id INT NOT NULL,
    check_in DATETIME,
    check_out DATETIME,
    status ENUM('active', 'completed') DEFAULT 'active',
    CONSTRAINT uq_sessions_booking UNIQUE (booking_id),
    CONSTRAINT fk_sessions_booking FOREIGN KEY (booking_id) 
        REFERENCES bookings(booking_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_sessions_parking FOREIGN KEY (parking_id) 
        REFERENCES parking_locations(parking_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_sessions_slot FOREIGN KEY (slot_id) 
        REFERENCES parking_slots(slot_id) 
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ==============================================================================
-- Table: favorites
-- Stores user-favorited parking locations for quick access.
-- ==============================================================================
CREATE TABLE IF NOT EXISTS favorites (
    favorite_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id     INT NOT NULL,
    parking_id  INT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_favorites_user    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_favorites_parking FOREIGN KEY (parking_id)
        REFERENCES parking_locations(parking_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_user_parking_fav  UNIQUE (user_id, parking_id)
) ENGINE=InnoDB;
