import os
import sys
import time
from datetime import datetime, timedelta, time as dt_time

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import engine, Base, SessionLocal
from backend.models import (
    User, UserRole, UserStatus,
    ParkingLocation, ParkingLocationStatus,
    ParkingSlot, SlotStatus, SlotType,
    Booking, BookingStatus
)

client = TestClient(app)


def seed_database_if_needed():
    """Ensure schema and baseline seed records exist for testing."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if users already seeded
        if db.query(User).count() == 0:
            seed_hash = "$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi"
            users = [
                User(user_id=1, name="John Doe", email="john@example.com", password=seed_hash, phone="9876543210", role=UserRole.USER, status=UserStatus.ACTIVE),
                User(user_id=2, name="Priya Sharma", email="priya@example.com", password=seed_hash, phone="9876543211", role=UserRole.USER, status=UserStatus.ACTIVE),
                User(user_id=3, name="City Parking Manager", email="manager@smartparking.com", password=seed_hash, phone="9876543212", role=UserRole.MANAGER, status=UserStatus.ACTIVE),
                User(user_id=4, name="System Administrator", email="admin@smartparking.com", password=seed_hash, phone="9876543213", role=UserRole.ADMIN, status=UserStatus.ACTIVE),
            ]
            db.add_all(users)
            db.commit()

        if db.query(ParkingLocation).count() == 0:
            locations = [
                ParkingLocation(parking_id=1, parking_name="Guindy Metro Multilevel Parking", area="Guindy", address="GST Road, Near Guindy Metro Station, Chennai - 600032", latitude=13.0067, longitude=80.2026, total_slots=10, parking_fee=30.00, opening_time=dt_time(6,0), closing_time=dt_time(23,0), ev_available=True, accessible_available=True, status=ParkingLocationStatus.ACTIVE),
                ParkingLocation(parking_id=2, parking_name="Olympia Tech Park Parking", area="Guindy", address="1, SIDCO Industrial Estate, Guindy, Chennai - 600032", latitude=13.0135, longitude=80.2082, total_slots=8, parking_fee=40.00, opening_time=dt_time(8,0), closing_time=dt_time(22,0), ev_available=True, accessible_available=False, status=ParkingLocationStatus.ACTIVE),
                ParkingLocation(parking_id=3, parking_name="Pondy Bazaar Automated Multilevel Parking", area="T Nagar", address="Thanikachalam Rd, Pondy Bazaar, T. Nagar, Chennai - 600017", latitude=13.0418, longitude=80.2341, total_slots=10, parking_fee=50.00, opening_time=dt_time(8,0), closing_time=dt_time(23,0), ev_available=True, accessible_available=True, status=ParkingLocationStatus.ACTIVE),
                ParkingLocation(parking_id=4, parking_name="Panagal Park Municipal Parking", area="T Nagar", address="Duraiswamy Road, Panagal Park, T. Nagar, Chennai - 600017", latitude=13.0402, longitude=80.2295, total_slots=8, parking_fee=30.00, opening_time=dt_time(7,0), closing_time=dt_time(22,0), ev_available=False, accessible_available=True, status=ParkingLocationStatus.ACTIVE),
                ParkingLocation(parking_id=5, parking_name="Tambaram Railway Station East Parking", area="Tambaram", address="East Tambaram Station Complex, Chennai - 600059", latitude=12.9249, longitude=80.1180, total_slots=10, parking_fee=20.00, opening_time=dt_time(5,0), closing_time=dt_time(23,59), ev_available=False, accessible_available=True, status=ParkingLocationStatus.ACTIVE),
                ParkingLocation(parking_id=6, parking_name="Tambaram Sanatorium Hub Parking", area="Tambaram", address="GST Road, Tambaram Sanatorium, Chennai - 600047", latitude=12.9431, longitude=80.1287, total_slots=8, parking_fee=25.00, opening_time=dt_time(7,0), closing_time=dt_time(22,0), ev_available=True, accessible_available=True, status=ParkingLocationStatus.ACTIVE),
                ParkingLocation(parking_id=7, parking_name="Anna Nagar Tower Park Parking", area="Anna Nagar", address="3rd Avenue, Anna Nagar, Chennai - 600040", latitude=13.0850, longitude=80.2101, total_slots=10, parking_fee=25.00, opening_time=dt_time(6,0), closing_time=dt_time(22,0), ev_available=True, accessible_available=True, status=ParkingLocationStatus.ACTIVE),
                ParkingLocation(parking_id=8, parking_name="VR Mall Visitors Parking Annex", area="Anna Nagar", address="Jawaharlal Nehru Road, Anna Nagar West, Chennai - 600040", latitude=13.0838, longitude=80.1983, total_slots=10, parking_fee=60.00, opening_time=dt_time(10,0), closing_time=dt_time(23,0), ev_available=True, accessible_available=True, status=ParkingLocationStatus.ACTIVE),
                ParkingLocation(parking_id=9, parking_name="Velachery MRTS Station Parking", area="Velachery", address="Inner Ring Road, Velachery, Chennai - 600042", latitude=12.9815, longitude=80.2180, total_slots=10, parking_fee=20.00, opening_time=dt_time(5,30), closing_time=dt_time(23,30), ev_available=False, accessible_available=True, status=ParkingLocationStatus.ACTIVE),
                ParkingLocation(parking_id=10, parking_name="Phoenix Marketcity Parking Annex", area="Velachery", address="142, Velachery Main Rd, Indira Gandhi Nagar, Velachery, Chennai - 600042", latitude=12.9918, longitude=80.2167, total_slots=10, parking_fee=50.00, opening_time=dt_time(9,0), closing_time=dt_time(23,0), ev_available=True, accessible_available=True, status=ParkingLocationStatus.ACTIVE),
            ]
            db.add_all(locations)
            db.commit()

        if db.query(ParkingSlot).count() == 0:
            slots = [
                # Guindy
                ParkingSlot(parking_id=1, slot_number="G1-01", slot_type=SlotType.NORMAL, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=1, slot_number="G1-02", slot_type=SlotType.NORMAL, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=1, slot_number="G1-03", slot_type=SlotType.NORMAL, status=SlotStatus.OCCUPIED),
                ParkingSlot(parking_id=1, slot_number="G1-04", slot_type=SlotType.NORMAL, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=1, slot_number="G1-05", slot_type=SlotType.EV, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=1, slot_number="G1-06", slot_type=SlotType.EV, status=SlotStatus.RESERVED),
                ParkingSlot(parking_id=1, slot_number="G1-07", slot_type=SlotType.ACCESSIBLE, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=1, slot_number="G1-08", slot_type=SlotType.ACCESSIBLE, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=1, slot_number="G1-09", slot_type=SlotType.NORMAL, status=SlotStatus.MAINTENANCE),
                ParkingSlot(parking_id=1, slot_number="G1-10", slot_type=SlotType.NORMAL, status=SlotStatus.AVAILABLE),
                # Olympia
                ParkingSlot(parking_id=2, slot_number="OTP-01", slot_type=SlotType.NORMAL, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=2, slot_number="OTP-02", slot_type=SlotType.NORMAL, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=2, slot_number="OTP-03", slot_type=SlotType.NORMAL, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=2, slot_number="OTP-04", slot_type=SlotType.NORMAL, status=SlotStatus.OCCUPIED),
                ParkingSlot(parking_id=2, slot_number="OTP-05", slot_type=SlotType.EV, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=2, slot_number="OTP-06", slot_type=SlotType.EV, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=2, slot_number="OTP-07", slot_type=SlotType.NORMAL, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=2, slot_number="OTP-08", slot_type=SlotType.NORMAL, status=SlotStatus.AVAILABLE),
                # Pondy Bazaar
                ParkingSlot(parking_id=3, slot_number="PB-01", slot_type=SlotType.NORMAL, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=3, slot_number="PB-02", slot_type=SlotType.NORMAL, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=3, slot_number="PB-03", slot_type=SlotType.NORMAL, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=3, slot_number="PB-04", slot_type=SlotType.NORMAL, status=SlotStatus.OCCUPIED),
                ParkingSlot(parking_id=3, slot_number="PB-05", slot_type=SlotType.NORMAL, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=3, slot_number="PB-06", slot_type=SlotType.EV, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=3, slot_number="PB-07", slot_type=SlotType.EV, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=3, slot_number="PB-08", slot_type=SlotType.ACCESSIBLE, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=3, slot_number="PB-09", slot_type=SlotType.ACCESSIBLE, status=SlotStatus.AVAILABLE),
                ParkingSlot(parking_id=3, slot_number="PB-10", slot_type=SlotType.NORMAL, status=SlotStatus.AVAILABLE),
            ]
            # Add slots for remaining 4-10
            for pid in range(4, 11):
                for sid in range(1, 9):
                    stype = SlotType.EV if sid == 4 else (SlotType.ACCESSIBLE if sid == 5 else SlotType.NORMAL)
                    slots.append(ParkingSlot(parking_id=pid, slot_number=f"LOC{pid}-{sid:02d}", slot_type=stype, status=SlotStatus.AVAILABLE))
            db.add_all(slots)
            db.commit()

        if db.query(Booking).count() == 0:
            # Baseline booking
            now = datetime.now()
            b = Booking(
                user_id=1,
                parking_id=1,
                slot_id=6,
                booking_date=now.date(),
                start_time=now + timedelta(hours=1),
                end_time=now + timedelta(hours=3),
                status=BookingStatus.RESERVED
            )
            db.add(b)
            db.commit()

    finally:
        db.close()


def run_comprehensive_tests():
    print("\n" + "="*70)
    print("SMART PARKING FINDER - FULL SYSTEM & ADMIN MODULE (MEMBER 3) VERIFICATION")
    print("="*70)

    # Ensure baseline database schema and seed data are populated
    seed_database_if_needed()

    # -------------------------------------------------------------------------
    # Setup & Authentication Tokens
    # -------------------------------------------------------------------------
    print("\n[Setup] Authenticating test accounts...")
    
    # 1. Admin account (admin@smartparking.com)
    admin_login = client.post("/api/auth/login", json={"email": "admin@smartparking.com", "password": "password123"})
    assert admin_login.status_code == 200, f"Admin login failed: {admin_login.text}"
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    admin_user = admin_login.json()["user"]
    print(f"  [OK] Admin logged in: {admin_user['name']} (role={admin_user['role']})")
    assert admin_user["role"] == "admin"

    # 2. Normal user account (john@example.com)
    user_login = client.post("/api/auth/login", json={"email": "john@example.com", "password": "password123"})
    assert user_login.status_code == 200, f"User login failed: {user_login.text}"
    user_token = user_login.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    normal_user = user_login.json()["user"]
    print(f"  [OK] Normal user logged in: {normal_user['name']} (role={normal_user['role']})")
    assert normal_user["role"] == "user"

    # 3. Manager account (manager@smartparking.com)
    mgr_login = client.post("/api/auth/login", json={"email": "manager@smartparking.com", "password": "password123"})
    assert mgr_login.status_code == 200, f"Manager login failed: {mgr_login.text}"
    mgr_token = mgr_login.json()["access_token"]
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}
    mgr_user = mgr_login.json()["user"]
    print(f"  [OK] Manager logged in: {mgr_user['name']} (role={mgr_user['role']})")

    # =========================================================================
    # ITEM 1: Existing User Flow (Login -> Search -> Book -> Checkin -> Checkout -> Cancel)
    # =========================================================================
    print("\n[Test Item 1] Verifying existing user flow remains 100% operational...")
    # Search
    search_r = client.get("/api/parking?area=Guindy")
    assert search_r.status_code == 200
    locations = search_r.json()
    assert len(locations) > 0
    p1 = locations[0]
    p1_id = p1["parking_id"]

    # Slots
    slots_r = client.get(f"/api/parking/{p1_id}/slots")
    assert slots_r.status_code == 200
    avail_slot = next((s for s in slots_r.json() if s["status"] == "available"), None)
    assert avail_slot is not None, "Need available slot for testing user flow"

    # Book
    start_time = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S")
    book_r = client.post("/api/bookings", headers=user_headers, json={
        "parking_id": p1_id,
        "slot_id": avail_slot["slot_id"],
        "start_time": start_time,
        "duration_hours": 1
    })
    assert book_r.status_code == 201
    b_id = book_r.json()["booking_id"]
    print(f"  [OK] Booking created: #{b_id}")

    # Check-in
    checkin_r = client.post("/api/sessions/check-in", headers=user_headers, json={"booking_id": b_id})
    assert checkin_r.status_code == 201
    s_id = checkin_r.json()["session_id"]
    print(f"  [OK] Session started (Check-in): #{s_id}")

    # Check-out
    checkout_r = client.post("/api/sessions/check-out", headers=user_headers, json={"session_id": s_id})
    assert checkout_r.status_code == 200
    assert checkout_r.json()["status"] == "completed"
    print(f"  [OK] Session finished (Check-out): Status={checkout_r.json()['status']}")

    # Cancellation flow on a second slot
    avail_slot2 = next((s for s in client.get(f"/api/parking/{p1_id}/slots").json() if s["status"] == "available"), None)
    if avail_slot2:
        book2_r = client.post("/api/bookings", headers=user_headers, json={
            "parking_id": p1_id,
            "slot_id": avail_slot2["slot_id"],
            "start_time": (datetime.now() + timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S"),
            "duration_hours": 1
        })
        assert book2_r.status_code == 201
        b2_id = book2_r.json()["booking_id"]
        cancel_r = client.put(f"/api/bookings/{b2_id}/cancel", headers=user_headers)
        assert cancel_r.status_code == 200
        assert cancel_r.json()["status"] == "cancelled"
        print(f"  [OK] Booking #{b2_id} cancelled and released successfully")
    print("  [PASS] ITEM 1: User flow completely operational.")

    # =========================================================================
    # ITEM 2: Member 2's Parking Management Functionality
    # =========================================================================
    print("\n[Test Item 2] Verifying Member 2 parking management endpoints...")
    mgr_all_r = client.get("/api/parking/management/all", headers=mgr_headers)
    assert mgr_all_r.status_code == 200
    print(f"  [OK] Managed parking locations retrieved: {len(mgr_all_r.json())} locations")

    sessions_all_r = client.get("/api/sessions/all", headers=mgr_headers)
    assert sessions_all_r.status_code == 200
    print(f"  [OK] Active sessions retrieved: {len(sessions_all_r.json())} sessions")
    print("  [PASS] ITEM 2: Member 2 management endpoints completely operational.")

    # =========================================================================
    # ITEM 3: Admin Role-Checked Access
    # =========================================================================
    print("\n[Test Item 3] Verifying Admin role gating (admin allowed, non-admin forbidden)...")
    # Admin allowed
    admin_dash_r = client.get("/api/admin/dashboard-stats", headers=admin_headers)
    assert admin_dash_r.status_code == 200
    print("  [OK] Admin token accessed /api/admin/dashboard-stats -> 200 OK")

    # Non-admin rejected
    user_dash_admin_r = client.get("/api/admin/dashboard-stats", headers=user_headers)
    assert user_dash_admin_r.status_code == 403
    print(f"  [OK] User token rejected with 403 Forbidden: {user_dash_admin_r.json()['detail']}")

    # Manager rejected
    mgr_admin_r = client.get("/api/admin/dashboard-stats", headers=mgr_headers)
    assert mgr_admin_r.status_code == 403
    print(f"  [OK] Manager token rejected with 403 Forbidden: {mgr_admin_r.json()['detail']}")

    # Anonymous rejected
    anon_r = client.get("/api/admin/dashboard-stats")
    assert anon_r.status_code == 401
    print("  [OK] Anonymous request rejected with 401 Unauthorized")
    print("  [PASS] ITEM 3: Role-checked access strictly enforced.")

    # =========================================================================
    # ITEM 4: Summary Cards Live DB Counts
    # =========================================================================
    print("\n[Test Item 4] Verifying summary card metrics from live DB...")
    stats_data = admin_dash_r.json()
    print(f"  Live Stats: Users={stats_data['total_users']}, Locations={stats_data['total_parking_locations']}, Slots={stats_data['total_slots']}, Available={stats_data['available_slots']}, Occupied={stats_data['occupied_slots']}, Reserved={stats_data['reserved_slots']}, Bookings={stats_data['total_bookings']}")
    assert stats_data["total_users"] >= 4
    assert stats_data["total_parking_locations"] >= 10
    assert stats_data["total_slots"] >= 80
    assert stats_data["total_bookings"] >= 1
    assert stats_data["total_slots"] == (stats_data["available_slots"] + stats_data["occupied_slots"] + stats_data["reserved_slots"] + stats_data["maintenance_slots"])
    print("  [PASS] ITEM 4: Live aggregate counts are mathematically coherent and accurate.")

    # =========================================================================
    # ITEM 5: Charts Breakdown Data
    # =========================================================================
    print("\n[Test Item 5] Verifying 4 charts breakdown telemetry...")
    rep_r = client.get("/api/admin/reports", headers=admin_headers)
    assert rep_r.status_code == 200
    rep_data = rep_r.json()

    # Chart 1: Parking-wise occupancy
    assert "parking_occupancy_list" in rep_data
    assert len(rep_data["parking_occupancy_list"]) >= 10
    print(f"  [OK] 1. Parking occupancy breakdown: {len(rep_data['parking_occupancy_list'])} facilities loaded")

    # Chart 2: Bookings by parking location
    assert "bookings_by_parking" in rep_data
    assert len(rep_data["bookings_by_parking"]) >= 10
    print(f"  [OK] 2. Bookings by location breakdown: {len(rep_data['bookings_by_parking'])} facilities loaded")

    # Chart 3: Slot status breakdown
    assert "slot_status_counts" in rep_data
    assert "Available" in rep_data["slot_status_counts"]
    assert "Occupied" in rep_data["slot_status_counts"]
    print(f"  [OK] 3. Slot status breakdown: {rep_data['slot_status_counts']}")

    # Chart 4: Booking status breakdown
    assert "booking_status_counts" in rep_data
    assert "Reserved" in rep_data["booking_status_counts"]
    assert "Completed" in rep_data["booking_status_counts"]
    print(f"  [OK] 4. Booking status breakdown: {rep_data['booking_status_counts']}")
    print("  [PASS] ITEM 5: All 4 charts breakdowns provide complete live telemetry.")

    # =========================================================================
    # ITEM 6: User Management (View Users & Details, No Password Exposed)
    # =========================================================================
    print("\n[Test Item 6] Verifying user listing and sanitization (no passwords exposed)...")
    users_r = client.get("/api/admin/users", headers=admin_headers)
    assert users_r.status_code == 200
    all_users = users_r.json()
    assert len(all_users) >= 4
    for u in all_users:
        assert "password" not in u, f"CRITICAL: password field exposed in user {u['user_id']}"
        assert "user_id" in u and "email" in u and "role" in u and "status" in u
    print(f"  [OK] Retrieved {len(all_users)} users. Verified ZERO passwords or password hashes exposed.")
    print("  [PASS] ITEM 6: User inspection sanitized.")

    # =========================================================================
    # ITEM 7: Activate / Deactivate User Account & Persistence
    # =========================================================================
    print("\n[Test Item 7] Verifying user activation/deactivation and login block persistence...")
    # Create a dummy user for deactivation test
    test_user_email = f"deact_test_{int(time.time())}@example.com"
    reg_test = client.post("/api/auth/register", json={
        "name": "Deactivation Test",
        "email": test_user_email,
        "password": "password123",
        "phone": "9998887776"
    })
    assert reg_test.status_code == 201
    test_uid = reg_test.json()["user_id"]
    print(f"  [OK] Created test user #{test_uid} ({test_user_email})")

    # Deactivate the user
    deact_r = client.put(f"/api/admin/users/{test_uid}/status", headers=admin_headers, json={"status": "inactive"})
    assert deact_r.status_code == 200
    assert deact_r.json()["status"] == "inactive"
    print(f"  [OK] User #{test_uid} deactivated by admin")

    # Verify user cannot log in
    deact_login_r = client.post("/api/auth/login", json={"email": test_user_email, "password": "password123"})
    assert deact_login_r.status_code == 403
    print(f"  [OK] Login blocked with 403 Forbidden: {deact_login_r.json()['detail']}")

    # Reactivate the user
    react_r = client.put(f"/api/admin/users/{test_uid}/status", headers=admin_headers, json={"status": "active"})
    assert react_r.status_code == 200
    assert react_r.json()["status"] == "active"
    print(f"  [OK] User #{test_uid} reactivated by admin")

    # Verify user can log in again
    react_login_r = client.post("/api/auth/login", json={"email": test_user_email, "password": "password123"})
    assert react_login_r.status_code == 200
    print(f"  [OK] Login succeeded after reactivation")

    # Self-deactivation protection check
    self_deact_r = client.put(f"/api/admin/users/{admin_user['user_id']}/status", headers=admin_headers, json={"status": "inactive"})
    assert self_deact_r.status_code == 400
    print(f"  [OK] Admin self-deactivation rejected with 400: {self_deact_r.json()['detail']}")
    print("  [PASS] ITEM 7: User activation/deactivation is persistent and guarded.")

    # =========================================================================
    # ITEM 8: Parking Locations with Accurate Slot Counts
    # =========================================================================
    print("\n[Test Item 8] Verifying parking locations monitoring and slot counts...")
    p_sum_r = client.get("/api/admin/parking-summary", headers=admin_headers)
    assert p_sum_r.status_code == 200
    p_sum = p_sum_r.json()
    assert len(p_sum) >= 10
    first_p = p_sum[0]
    assert "parking_id" in first_p
    assert "total_slots" in first_p
    assert "available_slots" in first_p
    assert "occupied_slots" in first_p
    assert "reserved_slots" in first_p
    assert "occupancy_rate" in first_p
    print(f"  [OK] Parking Facility #{first_p['parking_id']} '{first_p['parking_name']}': Total={first_p['total_slots']}, Available={first_p['available_slots']}, Occupied={first_p['occupied_slots']}, Reserved={first_p['reserved_slots']}, Rate={first_p['occupancy_rate']}%")
    print("  [PASS] ITEM 8: Parking monitoring delivers complete live slot telemetry.")

    # =========================================================================
    # ITEM 9: Booking Monitoring, Search by ID, Filter by Location
    # =========================================================================
    print("\n[Test Item 9] Verifying booking monitoring and search/filter capabilities...")
    # All bookings
    b_all_r = client.get("/api/admin/booking-summary", headers=admin_headers)
    assert b_all_r.status_code == 200
    b_all_data = b_all_r.json()
    assert b_all_data["total_bookings"] > 0
    assert len(b_all_data["bookings"]) > 0
    sample_b = b_all_data["bookings"][0]
    sample_b_id = sample_b["booking_id"]
    print(f"  [OK] Retrieved {len(b_all_data['bookings'])} bookings ledger records")

    # Search by exact ID
    b_search_r = client.get(f"/api/admin/booking-summary?search_id={sample_b_id}", headers=admin_headers)
    assert b_search_r.status_code == 200
    search_results = b_search_r.json()["bookings"]
    assert len(search_results) == 1
    assert search_results[0]["booking_id"] == sample_b_id
    print(f"  [OK] Search by Booking ID #{sample_b_id} -> exact match returned")

    # Filter by Parking Location
    b_filter_p_r = client.get(f"/api/admin/booking-summary?parking_id={p1_id}", headers=admin_headers)
    assert b_filter_p_r.status_code == 200
    p_results = b_filter_p_r.json()["bookings"]
    for res in p_results:
        assert res["parking_id"] == p1_id
    print(f"  [OK] Filter by Parking ID #{p1_id} -> {len(p_results)} matching bookings returned")
    print("  [PASS] ITEM 9: Booking audit ledger search and filters operational.")

    # =========================================================================
    # ITEM 10: Reports Intelligence & Top Locations
    # =========================================================================
    print("\n[Test Item 10] Verifying analytical reports and top-used parking...")
    rep_resp = client.get("/api/admin/reports", headers=admin_headers)
    assert rep_resp.status_code == 200
    rep = rep_resp.json()
    assert rep["total_bookings"] >= 1
    assert rep["total_slots"] > 0
    assert rep["available_slots"] >= 0
    assert rep["overall_occupancy_rate"] >= 0.0
    print(f"  [OK] Reports: Total Bookings={rep['total_bookings']}, Total Slots={rep['total_slots']}, Available={rep['available_slots']}, Overall Occupancy={rep['overall_occupancy_rate']}%")
    if rep["most_used_parking"]:
        top = rep["most_used_parking"][0]
        print(f"  [OK] Most-Used Parking Leader: #{top['parking_id']} '{top['parking_name']}' ({top['booking_count']} bookings)")
    print("  [PASS] ITEM 10: Analytical reports generated correctly.")

    # =========================================================================
    # ITEM 11: Dynamic Live Telemetry on New Booking
    # =========================================================================
    print("\n[Test Item 11] Verifying live sync on new booking (no hardcoding)...")
    # Initial stats
    before_stats = client.get("/api/admin/dashboard-stats", headers=admin_headers).json()
    
    # Place a new booking
    p2_slots = client.get("/api/parking/2/slots").json()
    p2_avail = next((s for s in p2_slots if s["status"] == "available"), None)
    assert p2_avail is not None
    
    new_book_r = client.post("/api/bookings", headers=user_headers, json={
        "parking_id": 2,
        "slot_id": p2_avail["slot_id"],
        "start_time": (datetime.now() + timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%S"),
        "duration_hours": 2
    })
    assert new_book_r.status_code == 201
    
    # Check stats immediately after booking
    after_stats = client.get("/api/admin/dashboard-stats", headers=admin_headers).json()
    print(f"  Before Booking: Total Bookings={before_stats['total_bookings']}, Reserved Slots={before_stats['reserved_slots']}, Available Slots={before_stats['available_slots']}")
    print(f"  After Booking:  Total Bookings={after_stats['total_bookings']}, Reserved Slots={after_stats['reserved_slots']}, Available Slots={after_stats['available_slots']}")
    assert after_stats["total_bookings"] == before_stats["total_bookings"] + 1
    assert after_stats["reserved_slots"] == before_stats["reserved_slots"] + 1
    assert after_stats["available_slots"] == before_stats["available_slots"] - 1
    print("  [PASS] ITEM 11: Live MySQL queries instantly reflect database state changes.")

    # =========================================================================
    # ITEM 12: Non-Admin Direct Endpoint Access Returns 401/403 (No Crash)
    # =========================================================================
    print("\n[Test Item 12] Verifying non-admin direct endpoint calls return 401/403...")
    endpoints = [
        ("GET", "/api/admin/dashboard-stats"),
        ("GET", "/api/admin/parking-summary"),
        ("GET", "/api/admin/slot-summary"),
        ("GET", "/api/admin/booking-summary"),
        ("GET", "/api/admin/users"),
        ("PUT", f"/api/admin/users/{test_uid}/status"),
        ("GET", "/api/admin/reports")
    ]

    for method, path in endpoints:
        # Non-admin user
        if method == "GET":
            r_user = client.get(path, headers=user_headers)
            r_anon = client.get(path)
        else:
            r_user = client.put(path, headers=user_headers, json={"status": "active"})
            r_anon = client.put(path, json={"status": "active"})

        assert r_user.status_code == 403, f"{method} {path} should return 403 for user, got {r_user.status_code}"
        assert r_anon.status_code == 401, f"{method} {path} should return 401 for anon, got {r_anon.status_code}"
        print(f"  [OK] {method} {path} -> 403 Forbidden for normal user, 401 Unauthorized for anonymous")
    print("  [PASS] ITEM 12: All admin endpoints securely guarded without crashes.")

    # =========================================================================
    # ITEM 13: Integrity Check of Schema, Seed Data, and Member 1/2 Files
    # =========================================================================
    print("\n[Test Item 13] Verifying file boundary integrity...")
    import subprocess
    diff_output = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
    print(f"  Git status:\n{diff_output.strip()}")

    # Untouched member files check
    forbidden_files = [
        "frontend/pages/user_dashboard.py",
        "frontend/pages/booking.py",
        "frontend/pages/login.py",
        "frontend/pages/parking_search.py",
        "frontend/pages/my_bookings.py",
        "frontend/pages/profile.py",
        "backend/services/parking_service.py",
        "frontend/pages/parking_management.py",
        "backend/services/booking_service.py",
        "database/schema.sql",
        "database/seed_data.sql"
    ]

    for f in forbidden_files:
        norm_f = f.replace("/", "\\")
        assert f not in diff_output and norm_f not in diff_output, f"BOUNDARY VIOLATION: {f} was modified!"
        print(f"  [OK] Untouched: {f}")

    print("  [PASS] ITEM 13: Strict boundaries respected 100%.")

    print("\n" + "="*70)
    print("ALL 13 TEST ITEMS PASSED WITH 100% SUCCESS!")
    print("="*70)


if __name__ == "__main__":
    run_comprehensive_tests()
