-- ==============================================================================
-- Smart Parking Finder & Management System
-- Database Seed Data (Chennai Locations, Slots, & Test Users)
-- Database: smart_parking_db
-- ==============================================================================

USE smart_parking_db;

-- Rebuild the local demonstration dataset deterministically.  Child tables are
-- cleared first so all foreign-key relationships and session uniqueness remain
-- valid on every seed run.
DELETE FROM favorites;
DELETE FROM parking_sessions;
DELETE FROM bookings;
DELETE FROM parking_slots;
DELETE FROM parking_locations;
DELETE FROM users;
ALTER TABLE users AUTO_INCREMENT = 1;
ALTER TABLE parking_locations AUTO_INCREMENT = 1;
ALTER TABLE parking_slots AUTO_INCREMENT = 1;
ALTER TABLE bookings AUTO_INCREMENT = 1;
ALTER TABLE parking_sessions AUTO_INCREMENT = 1;
ALTER TABLE favorites AUTO_INCREMENT = 1;

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

-- 4. Expanded Chennai demo population (50 users, 15 facilities, 119 slots,
--    50 bookings, 48 sessions, and 50 favourites).  Explicit IDs make this
--    seed safe to re-run without duplicating primary or unique keys.
INSERT INTO users (user_id, name, email, password, phone, role, status) VALUES
(5, 'Arun Kumar', 'arun.kumar@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010005', 'user', 'active'),
(6, 'Kavya Iyer', 'kavya.iyer@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010006', 'user', 'active'),
(7, 'Vignesh R', 'vignesh.r@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010007', 'user', 'active'),
(8, 'Meera Nair', 'meera.nair@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010008', 'user', 'active'),
(9, 'Sanjay Krishnan', 'sanjay.krishnan@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010009', 'user', 'active'),
(10, 'Divya Raj', 'divya.raj@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010010', 'user', 'active'),
(11, 'Rohit Menon', 'rohit.menon@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010011', 'user', 'active'),
(12, 'Ananya S', 'ananya.s@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010012', 'user', 'active'),
(13, 'Prakash V', 'prakash.v@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010013', 'user', 'active'),
(14, 'Nithya Balaji', 'nithya.balaji@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010014', 'user', 'active'),
(15, 'Hari Prasad', 'hari.prasad@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010015', 'user', 'active'),
(16, 'Lakshmi Devi', 'lakshmi.devi@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010016', 'user', 'active'),
(17, 'Gokul S', 'gokul.s@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010017', 'user', 'active'),
(18, 'Riya Thomas', 'riya.thomas@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010018', 'user', 'active'),
(19, 'Surya K', 'surya.k@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010019', 'user', 'active'),
(20, 'Aarthi M', 'aarthi.m@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010020', 'user', 'active'),
(21, 'Kiran Joseph', 'kiran.joseph@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010021', 'user', 'active'),
(22, 'Swetha R', 'swetha.r@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010022', 'user', 'active'),
(23, 'Madhavan P', 'madhavan.p@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010023', 'user', 'active'),
(24, 'Sneha Raman', 'sneha.raman@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010024', 'user', 'active'),
(25, 'Vishal Anand', 'vishal.anand@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010025', 'user', 'active'),
(26, 'Pooja Sreenivasan', 'pooja.s@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010026', 'user', 'active'),
(27, 'Ramesh Babu', 'ramesh.babu@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010027', 'user', 'active'),
(28, 'Keerthana S', 'keerthana.s@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010028', 'user', 'active'),
(29, 'Ajay Varma', 'ajay.varma@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010029', 'user', 'active'),
(30, 'Gayathri N', 'gayathri.n@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010030', 'user', 'active'),
(31, 'Dinesh Kumar', 'dinesh.kumar@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010031', 'user', 'active'),
(32, 'Revathi P', 'revathi.p@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010032', 'user', 'active'),
(33, 'Naveen S', 'naveen.s@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010033', 'user', 'active'),
(34, 'Uma Mahesh', 'uma.mahesh@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010034', 'user', 'active'),
(35, 'Sathish R', 'sathish.r@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010035', 'user', 'active'),
(36, 'Aishwarya K', 'aishwarya.k@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010036', 'user', 'active'),
(37, 'Manoj P', 'manoj.p@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010037', 'user', 'active'),
(38, 'Nandhini V', 'nandhini.v@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010038', 'user', 'active'),
(39, 'Bharath K', 'bharath.k@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010039', 'user', 'active'),
(40, 'Deepika M', 'deepika.m@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010040', 'user', 'active'),
(41, 'Suresh R', 'suresh.r@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010041', 'user', 'active'),
(42, 'Mahalakshmi P', 'mahalakshmi.p@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010042', 'user', 'active'),
(43, 'Aravind S', 'aravind.s@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010043', 'user', 'active'),
(44, 'Janani R', 'janani.r@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010044', 'user', 'active'),
(45, 'Karthik V', 'karthik.v@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010045', 'user', 'active'),
(46, 'Preethi S', 'preethi.s@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010046', 'user', 'active'),
(47, 'Mohan Raj', 'mohan.raj@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010047', 'user', 'active'),
(48, 'Shalini K', 'shalini.k@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010048', 'user', 'active'),
(49, 'Yogesh N', 'yogesh.n@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010049', 'user', 'active'),
(50, 'Harini V', 'harini.v@example.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '9840010050', 'user', 'active')
ON DUPLICATE KEY UPDATE name=VALUES(name), phone=VALUES(phone), role=VALUES(role), status=VALUES(status);

INSERT INTO parking_locations (parking_id, parking_name, area, address, latitude, longitude, total_slots, parking_fee, opening_time, closing_time, ev_available, accessible_available, status) VALUES
(11, 'Marina Beach Loop Road Parking', 'Marina', 'Kamarajar Salai, Near Marina Beach, Chennai - 600005', 13.0509000, 80.2824000, 5, 40.00, '06:00:00', '23:00:00', TRUE, TRUE, 'active'),
(12, 'Mylapore Tank Square Parking', 'Mylapore', 'Kutchery Road, Mylapore, Chennai - 600004', 13.0337000, 80.2687000, 5, 35.00, '07:00:00', '22:00:00', FALSE, TRUE, 'active'),
(13, 'Adyar Gandhi Nagar Parking', 'Adyar', '2nd Main Road, Gandhi Nagar, Adyar, Chennai - 600020', 13.0069000, 80.2570000, 5, 45.00, '07:00:00', '23:00:00', TRUE, TRUE, 'active'),
(14, 'Nungambakkam High Road Parking', 'Nungambakkam', 'Nungambakkam High Road, Chennai - 600034', 13.0613000, 80.2428000, 5, 50.00, '08:00:00', '23:00:00', TRUE, FALSE, 'active'),
(15, 'Koyambedu Metro Park and Ride', 'Koyambedu', 'Jawaharlal Nehru Salai, Koyambedu, Chennai - 600107', 13.0695000, 80.1945000, 5, 30.00, '05:30:00', '23:30:00', TRUE, TRUE, 'active')
ON DUPLICATE KEY UPDATE parking_name=VALUES(parking_name), total_slots=VALUES(total_slots), parking_fee=VALUES(parking_fee), status=VALUES(status);

INSERT INTO parking_slots (slot_id, parking_id, slot_number, slot_type, status) VALUES
(95, 11, 'MB-01', 'normal', 'available'), (96, 11, 'MB-02', 'normal', 'available'), (97, 11, 'MB-03', 'normal', 'available'), (98, 11, 'MB-04', 'ev', 'available'), (99, 11, 'MB-05', 'accessible', 'available'),
(100, 12, 'MY-01', 'normal', 'available'), (101, 12, 'MY-02', 'normal', 'available'), (102, 12, 'MY-03', 'normal', 'available'), (103, 12, 'MY-04', 'ev', 'available'), (104, 12, 'MY-05', 'accessible', 'available'),
(105, 13, 'AD-01', 'normal', 'available'), (106, 13, 'AD-02', 'normal', 'available'), (107, 13, 'AD-03', 'normal', 'available'), (108, 13, 'AD-04', 'ev', 'available'), (109, 13, 'AD-05', 'accessible', 'available'),
(110, 14, 'NU-01', 'normal', 'available'), (111, 14, 'NU-02', 'normal', 'available'), (112, 14, 'NU-03', 'normal', 'available'), (113, 14, 'NU-04', 'ev', 'available'), (114, 14, 'NU-05', 'accessible', 'available'),
(115, 15, 'KY-01', 'normal', 'available'), (116, 15, 'KY-02', 'normal', 'available'), (117, 15, 'KY-03', 'normal', 'available'), (118, 15, 'KY-04', 'ev', 'available'), (119, 15, 'KY-05', 'accessible', 'available')
ON DUPLICATE KEY UPDATE parking_id=VALUES(parking_id), slot_number=VALUES(slot_number), slot_type=VALUES(slot_type), status=VALUES(status);

-- IDs 1-8 reflect the occupied/reserved slots above; the remainder provide history.
INSERT INTO bookings (booking_id, user_id, parking_id, slot_id, booking_date, start_time, end_time, status) VALUES
(1,1,1,3,'2026-08-26','2026-08-26 08:00:00','2026-08-26 12:00:00','active'), (2,2,1,6,'2026-08-26','2026-08-26 18:00:00','2026-08-26 21:00:00','reserved'),
(3,5,2,14,'2026-08-26','2026-08-26 09:00:00','2026-08-26 13:00:00','active'), (4,6,3,22,'2026-08-26','2026-08-26 10:00:00','2026-08-26 14:00:00','active'),
(5,7,4,32,'2026-08-26','2026-08-26 11:00:00','2026-08-26 15:00:00','active'), (6,8,5,41,'2026-08-26','2026-08-26 08:30:00','2026-08-26 12:30:00','active'),
(7,9,7,62,'2026-08-26','2026-08-26 09:30:00','2026-08-26 13:30:00','active'), (8,10,9,79,'2026-08-26','2026-08-26 10:30:00','2026-08-26 14:30:00','active'),
(9,11,1,1,'2026-08-25','2026-08-25 17:00:00','2026-08-25 19:00:00','cancelled'), (10,12,1,2,'2026-08-01','2026-08-01 08:00:00','2026-08-01 10:00:00','completed'),
(11,13,1,4,'2026-08-02','2026-08-02 09:00:00','2026-08-02 11:00:00','completed'), (12,14,1,5,'2026-08-03','2026-08-03 10:00:00','2026-08-03 12:00:00','completed'),
(13,15,1,7,'2026-08-04','2026-08-04 11:00:00','2026-08-04 13:00:00','completed'), (14,16,2,11,'2026-08-05','2026-08-05 08:00:00','2026-08-05 10:00:00','completed'),
(15,17,2,12,'2026-08-06','2026-08-06 09:00:00','2026-08-06 11:00:00','completed'), (16,18,2,13,'2026-08-07','2026-08-07 10:00:00','2026-08-07 12:00:00','completed'),
(17,19,2,15,'2026-08-08','2026-08-08 11:00:00','2026-08-08 13:00:00','completed'), (18,20,3,19,'2026-08-09','2026-08-09 08:00:00','2026-08-09 10:00:00','completed'),
(19,21,3,20,'2026-08-10','2026-08-10 09:00:00','2026-08-10 11:00:00','completed'), (20,22,3,21,'2026-08-11','2026-08-11 10:00:00','2026-08-11 12:00:00','completed'),
(21,23,3,23,'2026-08-12','2026-08-12 11:00:00','2026-08-12 13:00:00','completed'), (22,24,4,29,'2026-08-13','2026-08-13 08:00:00','2026-08-13 10:00:00','completed'),
(23,25,4,30,'2026-08-14','2026-08-14 09:00:00','2026-08-14 11:00:00','completed'), (24,26,4,31,'2026-08-15','2026-08-15 10:00:00','2026-08-15 12:00:00','completed'),
(25,27,4,33,'2026-08-16','2026-08-16 11:00:00','2026-08-16 13:00:00','completed'), (26,28,5,37,'2026-08-17','2026-08-17 08:00:00','2026-08-17 10:00:00','completed'),
(27,29,5,38,'2026-08-18','2026-08-18 09:00:00','2026-08-18 11:00:00','completed'), (28,30,5,39,'2026-08-19','2026-08-19 10:00:00','2026-08-19 12:00:00','completed'),
(29,31,5,40,'2026-08-20','2026-08-20 11:00:00','2026-08-20 13:00:00','completed'), (30,32,6,47,'2026-08-01','2026-08-01 12:00:00','2026-08-01 14:00:00','completed'),
(31,33,6,48,'2026-08-02','2026-08-02 12:00:00','2026-08-02 14:00:00','completed'), (32,34,6,49,'2026-08-03','2026-08-03 12:00:00','2026-08-03 14:00:00','completed'),
(33,35,6,50,'2026-08-04','2026-08-04 12:00:00','2026-08-04 14:00:00','completed'), (34,36,7,55,'2026-08-05','2026-08-05 12:00:00','2026-08-05 14:00:00','completed'),
(35,37,7,56,'2026-08-06','2026-08-06 12:00:00','2026-08-06 14:00:00','completed'), (36,38,7,57,'2026-08-07','2026-08-07 12:00:00','2026-08-07 14:00:00','completed'),
(37,39,8,65,'2026-08-08','2026-08-08 12:00:00','2026-08-08 14:00:00','completed'), (38,40,8,66,'2026-08-09','2026-08-09 12:00:00','2026-08-09 14:00:00','completed'),
(39,41,8,67,'2026-08-10','2026-08-10 12:00:00','2026-08-10 14:00:00','completed'), (40,42,8,68,'2026-08-11','2026-08-11 12:00:00','2026-08-11 14:00:00','completed'),
(41,43,9,75,'2026-08-12','2026-08-12 12:00:00','2026-08-12 14:00:00','completed'), (42,44,9,76,'2026-08-13','2026-08-13 12:00:00','2026-08-13 14:00:00','completed'),
(43,45,9,77,'2026-08-14','2026-08-14 12:00:00','2026-08-14 14:00:00','completed'), (44,46,10,85,'2026-08-15','2026-08-15 12:00:00','2026-08-15 14:00:00','completed'),
(45,47,10,86,'2026-08-16','2026-08-16 12:00:00','2026-08-16 14:00:00','completed'), (46,48,10,87,'2026-08-17','2026-08-17 12:00:00','2026-08-17 14:00:00','completed'),
(47,49,11,95,'2026-08-18','2026-08-18 12:00:00','2026-08-18 14:00:00','completed'), (48,50,12,100,'2026-08-19','2026-08-19 12:00:00','2026-08-19 14:00:00','completed'),
(49,1,13,105,'2026-08-20','2026-08-20 12:00:00','2026-08-20 14:00:00','completed'), (50,2,14,110,'2026-08-21','2026-08-21 12:00:00','2026-08-21 14:00:00','completed')
ON DUPLICATE KEY UPDATE user_id=VALUES(user_id), parking_id=VALUES(parking_id), slot_id=VALUES(slot_id), booking_date=VALUES(booking_date), start_time=VALUES(start_time), end_time=VALUES(end_time), status=VALUES(status);

INSERT INTO parking_sessions (session_id, booking_id, user_id, parking_id, slot_id, check_in, check_out, status)
SELECT booking_id, booking_id, user_id, parking_id, slot_id,
       CASE WHEN status='active' THEN start_time ELSE start_time END,
       CASE WHEN status='active' THEN NULL ELSE end_time END,
       CASE WHEN status='active' THEN 'active' ELSE 'completed' END
FROM bookings WHERE booking_id IN (1,3,4,5,6,7,8) OR (booking_id BETWEEN 10 AND 50)
ON DUPLICATE KEY UPDATE user_id=VALUES(user_id), parking_id=VALUES(parking_id), slot_id=VALUES(slot_id), check_in=VALUES(check_in), check_out=VALUES(check_out), status=VALUES(status);

INSERT INTO favorites (favorite_id, user_id, parking_id) VALUES
(1,1,1),(2,2,2),(3,3,3),(4,4,4),(5,5,5),(6,6,6),(7,7,7),(8,8,8),(9,9,9),(10,10,10),
(11,11,11),(12,12,12),(13,13,13),(14,14,14),(15,15,15),(16,16,1),(17,17,2),(18,18,3),(19,19,4),(20,20,5),
(21,21,6),(22,22,7),(23,23,8),(24,24,9),(25,25,10),(26,26,11),(27,27,12),(28,28,13),(29,29,14),(30,30,15),
(31,31,1),(32,32,2),(33,33,3),(34,34,4),(35,35,5),(36,36,6),(37,37,7),(38,38,8),(39,39,9),(40,40,10),
(41,41,11),(42,42,12),(43,43,13),(44,44,14),(45,45,15),(46,46,1),(47,47,2),(48,48,3),(49,49,4),(50,50,5)
ON DUPLICATE KEY UPDATE user_id=VALUES(user_id), parking_id=VALUES(parking_id);
