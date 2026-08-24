USE smart_parking_db;

SHOW TABLES;

SELECT COUNT(*) AS users_count FROM users;
SELECT COUNT(*) AS parking_count FROM parking_locations;
SELECT COUNT(*) AS slots_count FROM parking_slots;
SELECT COUNT(*) AS bookings_count FROM bookings;
SELECT COUNT(*) AS sessions_count FROM parking_sessions;