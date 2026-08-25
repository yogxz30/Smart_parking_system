-- ==============================================================================
-- Smart Parking Finder & Management System
-- Database Seed Data (Chennai Locations, Slots, & Test Users)
-- Database: smart_parking_db
-- ==============================================================================

USE smart_parking_db;

-- 1. Insert Initial Users
-- Passwords below are hashed using bcrypt for "password123"
-- Hash: $2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi
INSERT INTO users (user_id, name, email, password, phone, role, status) VALUES
(1, 'John Doe', 'john@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9876543210', 'user', 'active'),
(2, 'Priya Sharma', 'priya@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9876543211', 'user', 'active'),
(3, 'City Parking Manager', 'manager@smartparking.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9876543212', 'manager', 'active'),
(4, 'System Administrator', 'admin@smartparking.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9876543213', 'admin', 'active')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 2. Insert Real Chennai Parking Locations
INSERT INTO parking_locations 
(parking_id, parking_name, area, address, latitude, longitude, total_slots, parking_fee, opening_time, closing_time, ev_available, accessible_available, status) 
VALUES
(1, 'Guindy Metro Multilevel Parking', 'Guindy', 'GST Road, Near Guindy Metro Station, Chennai - 600032', 13.0067000, 80.2026000, 10, 30.00, '06:00:00', '23:00:00', TRUE, TRUE, 'active'),
(2, 'Olympia Tech Park Parking', 'Guindy', '1, SIDCO Industrial Estate, Guindy, Chennai - 600032', 13.0135000, 80.2082000, 8, 40.00, '08:00:00', '22:00:00', TRUE, FALSE, 'active'),
(3, 'Pondy Bazaar Automated Multilevel Parking', 'T Nagar', 'Thanikachalam Rd, Pondy Bazaar, T. Nagar, Chennai - 600017', 13.0418000, 80.2341000, 10, 50.00, '08:00:00', '23:00:00', TRUE, TRUE, 'active'),
(4, 'Panagal Park Municipal Parking', 'T Nagar', 'Duraiswamy Road, Panagal Park, T. Nagar, Chennai - 600017', 13.0402000, 80.2295000, 8, 30.00, '07:00:00', '22:00:00', FALSE, TRUE, 'active'),
(5, 'Tambaram Railway Station East Parking', 'Tambaram', 'East Tambaram Station Complex, Chennai - 600059', 12.9249000, 80.1180000, 10, 20.00, '05:00:00', '23:59:00', FALSE, TRUE, 'active'),
(6, 'Tambaram Sanatorium Hub Parking', 'Tambaram', 'GST Road, Tambaram Sanatorium, Chennai - 600047', 12.9431000, 80.1287000, 8, 25.00, '07:00:00', '22:00:00', TRUE, TRUE, 'active'),
(7, 'Anna Nagar Tower Park Parking', 'Anna Nagar', '3rd Avenue, Anna Nagar, Chennai - 600040', 13.0850000, 80.2101000, 10, 25.00, '06:00:00', '22:00:00', TRUE, TRUE, 'active'),
(8, 'VR Mall Visitors Parking Annex', 'Anna Nagar', 'Jawaharlal Nehru Road, Anna Nagar West, Chennai - 600040', 13.0838000, 80.1983000, 10, 60.00, '10:00:00', '23:00:00', TRUE, TRUE, 'active'),
(9, 'Velachery MRTS Station Parking', 'Velachery', 'Inner Ring Road, Velachery, Chennai - 600042', 12.9815000, 80.2180000, 10, 20.00, '05:30:00', '23:30:00', FALSE, TRUE, 'active'),
(10, 'Phoenix Marketcity Parking Annex', 'Velachery', '142, Velachery Main Rd, Indira Gandhi Nagar, Velachery, Chennai - 600042', 12.9918000, 80.2167000, 10, 50.00, '09:00:00', '23:00:00', TRUE, TRUE, 'active')
ON DUPLICATE KEY UPDATE parking_name=VALUES(parking_name);

-- 3. Insert Sample Slots for Parking Facilities
-- Facility 1: Guindy Metro Multilevel Parking
INSERT INTO parking_slots (parking_id, slot_number, slot_type, status) VALUES
(1, 'G1-01', 'normal', 'available'),
(1, 'G1-02', 'normal', 'available'),
(1, 'G1-03', 'normal', 'occupied'),
(1, 'G1-04', 'normal', 'available'),
(1, 'G1-05', 'ev', 'available'),
(1, 'G1-06', 'ev', 'reserved'),
(1, 'G1-07', 'accessible', 'available'),
(1, 'G1-08', 'accessible', 'available'),
(1, 'G1-09', 'normal', 'maintenance'),
(1, 'G1-10', 'normal', 'available')
ON DUPLICATE KEY UPDATE slot_type=VALUES(slot_type);

-- Facility 2: Olympia Tech Park Parking (Guindy)
INSERT INTO parking_slots (parking_id, slot_number, slot_type, status) VALUES
(2, 'OTP-01', 'normal', 'available'),
(2, 'OTP-02', 'normal', 'available'),
(2, 'OTP-03', 'normal', 'available'),
(2, 'OTP-04', 'normal', 'occupied'),
(2, 'OTP-05', 'ev', 'available'),
(2, 'OTP-06', 'ev', 'available'),
(2, 'OTP-07', 'normal', 'available'),
(2, 'OTP-08', 'normal', 'available')
ON DUPLICATE KEY UPDATE slot_type=VALUES(slot_type);

-- Facility 3: Pondy Bazaar Automated Parking (T Nagar)
INSERT INTO parking_slots (parking_id, slot_number, slot_type, status) VALUES
(3, 'PB-01', 'normal', 'available'),
(3, 'PB-02', 'normal', 'available'),
(3, 'PB-03', 'normal', 'available'),
(3, 'PB-04', 'normal', 'occupied'),
(3, 'PB-05', 'normal', 'available'),
(3, 'PB-06', 'ev', 'available'),
(3, 'PB-07', 'ev', 'available'),
(3, 'PB-08', 'accessible', 'available'),
(3, 'PB-09', 'accessible', 'available'),
(3, 'PB-10', 'normal', 'available')
ON DUPLICATE KEY UPDATE slot_type=VALUES(slot_type);

-- Facility 4: Panagal Park Municipal Parking (T Nagar)
INSERT INTO parking_slots (parking_id, slot_number, slot_type, status) VALUES
(4, 'PP-01', 'normal', 'available'),
(4, 'PP-02', 'normal', 'available'),
(4, 'PP-03', 'normal', 'available'),
(4, 'PP-04', 'normal', 'occupied'),
(4, 'PP-05', 'accessible', 'available'),
(4, 'PP-06', 'accessible', 'available'),
(4, 'PP-07', 'normal', 'available'),
(4, 'PP-08', 'normal', 'available')
ON DUPLICATE KEY UPDATE slot_type=VALUES(slot_type);

-- Facility 5: Tambaram Railway Station East Parking (Tambaram)
INSERT INTO parking_slots (parking_id, slot_number, slot_type, status) VALUES
(5, 'TB-01', 'normal', 'available'),
(5, 'TB-02', 'normal', 'available'),
(5, 'TB-03', 'normal', 'available'),
(5, 'TB-04', 'normal', 'available'),
(5, 'TB-05', 'normal', 'occupied'),
(5, 'TB-06', 'accessible', 'available'),
(5, 'TB-07', 'accessible', 'available'),
(5, 'TB-08', 'normal', 'available'),
(5, 'TB-09', 'normal', 'maintenance'),
(5, 'TB-10', 'normal', 'available')
ON DUPLICATE KEY UPDATE slot_type=VALUES(slot_type);

-- Facility 6: Tambaram Sanatorium Hub Parking (Tambaram)
INSERT INTO parking_slots (parking_id, slot_number, slot_type, status) VALUES
(6, 'TS-01', 'normal', 'available'),
(6, 'TS-02', 'normal', 'available'),
(6, 'TS-03', 'normal', 'available'),
(6, 'TS-04', 'ev', 'available'),
(6, 'TS-05', 'ev', 'available'),
(6, 'TS-06', 'accessible', 'available'),
(6, 'TS-07', 'normal', 'available'),
(6, 'TS-08', 'normal', 'available')
ON DUPLICATE KEY UPDATE slot_type=VALUES(slot_type);

-- Facility 7: Anna Nagar Tower Park Parking (Anna Nagar)
INSERT INTO parking_slots (parking_id, slot_number, slot_type, status) VALUES
(7, 'AN-01', 'normal', 'available'),
(7, 'AN-02', 'normal', 'available'),
(7, 'AN-03', 'normal', 'available'),
(7, 'AN-04', 'ev', 'available'),
(7, 'AN-05', 'ev', 'available'),
(7, 'AN-06', 'accessible', 'available'),
(7, 'AN-07', 'accessible', 'available'),
(7, 'AN-08', 'normal', 'occupied'),
(7, 'AN-09', 'normal', 'available'),
(7, 'AN-10', 'normal', 'available')
ON DUPLICATE KEY UPDATE slot_type=VALUES(slot_type);

-- Facility 8: VR Mall Parking Annex (Anna Nagar)
INSERT INTO parking_slots (parking_id, slot_number, slot_type, status) VALUES
(8, 'VR-01', 'normal', 'available'),
(8, 'VR-02', 'normal', 'available'),
(8, 'VR-03', 'normal', 'available'),
(8, 'VR-04', 'normal', 'available'),
(8, 'VR-05', 'ev', 'available'),
(8, 'VR-06', 'ev', 'available'),
(8, 'VR-07', 'accessible', 'available'),
(8, 'VR-08', 'accessible', 'available'),
(8, 'VR-09', 'normal', 'available'),
(8, 'VR-10', 'normal', 'available')
ON DUPLICATE KEY UPDATE slot_type=VALUES(slot_type);

-- Facility 9: Velachery MRTS Station Parking (Velachery)
INSERT INTO parking_slots (parking_id, slot_number, slot_type, status) VALUES
(9, 'VL-01', 'normal', 'available'),
(9, 'VL-02', 'normal', 'available'),
(9, 'VL-03', 'normal', 'available'),
(9, 'VL-04', 'normal', 'available'),
(9, 'VL-05', 'normal', 'occupied'),
(9, 'VL-06', 'accessible', 'available'),
(9, 'VL-07', 'accessible', 'available'),
(9, 'VL-08', 'normal', 'available'),
(9, 'VL-09', 'normal', 'available'),
(9, 'VL-10', 'normal', 'available')
ON DUPLICATE KEY UPDATE slot_type=VALUES(slot_type);

-- Facility 10: Phoenix Marketcity Parking Annex (Velachery)
INSERT INTO parking_slots (parking_id, slot_number, slot_type, status) VALUES
(10, 'PMC-01', 'normal', 'available'),
(10, 'PMC-02', 'normal', 'available'),
(10, 'PMC-03', 'normal', 'available'),
(10, 'PMC-04', 'normal', 'available'),
(10, 'PMC-05', 'ev', 'available'),
(10, 'PMC-06', 'ev', 'available'),
(10, 'PMC-07', 'accessible', 'available'),
(10, 'PMC-08', 'accessible', 'available'),
(10, 'PMC-09', 'normal', 'available'),
(10, 'PMC-10', 'normal', 'available')
ON DUPLICATE KEY UPDATE slot_type=VALUES(slot_type);

SHOW CREATE TABLE parking_sessions;
SELECT parking_name,parking_fee FROM parking_locations;
select count(*) from parking_sessions;
SHOW COLUMNS FROM parking_locations;