import os
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_all():
    print("==================================================")
    print("SMART PARKING FINDER - BACKEND TEST SUITE")
    print("==================================================")

    # 1. Health check
    print("\n[1] Testing Health & Root Endpoints...")
    r = client.get("/health")
    print(f"  GET /health -> Status {r.status_code}, Response: {r.json()}")
    assert r.status_code == 200, "Health check failed"

    r_root = client.get("/")
    print(f"  GET / -> Status {r_root.status_code}, Response: {r_root.json()}")
    assert r_root.status_code == 200

    # 2. Authentication
    print("\n[2] Testing Authentication Endpoints...")
    # Seeded user login
    login_resp = client.post("/api/auth/login", json={"email": "john@example.com", "password": "password123"})
    print(f"  POST /api/auth/login (john@example.com) -> Status {login_resp.status_code}")
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    user_info = login_resp.json()["user"]
    print(f"  Authenticated User: {user_info['name']} ({user_info['email']}) | Role: {user_info['role']}")
    headers = {"Authorization": f"Bearer {token}"}

    # Wrong password test
    wrong_resp = client.post("/api/auth/login", json={"email": "john@example.com", "password": "wrongpassword"})
    print(f"  POST /api/auth/login (invalid password) -> Status {wrong_resp.status_code} (Expected 401)")
    assert wrong_resp.status_code == 401

    # Registration test
    test_email = f"driver_{int(time.time())}@example.com"
    reg_resp = client.post("/api/auth/register", json={
        "name": "Karthik Raja",
        "email": test_email,
        "password": "mypassword123",
        "phone": "9840123456"
    })
    print(f"  POST /api/auth/register ({test_email}) -> Status {reg_resp.status_code}")
    assert reg_resp.status_code == 201
    assert reg_resp.json()["email"] == test_email

    # Duplicate registration test
    dup_resp = client.post("/api/auth/register", json={
        "name": "Karthik Raja",
        "email": test_email,
        "password": "mypassword123"
    })
    print(f"  POST /api/auth/register (duplicate email) -> Status {dup_resp.status_code} (Expected 400)")
    assert dup_resp.status_code == 400

    # 3. User Profile & Dashboard
    print("\n[3] Testing User Profile & Dashboard...")
    prof_resp = client.get("/api/user/profile", headers=headers)
    print(f"  GET /api/user/profile -> Status {prof_resp.status_code}, User: {prof_resp.json()['name']}")
    assert prof_resp.status_code == 200

    dash_resp = client.get("/api/user/dashboard", headers=headers)
    print(f"  GET /api/user/dashboard -> Status {dash_resp.status_code}, Stats: {dash_resp.json()['stats']}")
    assert dash_resp.status_code == 200

    # 4. Parking & Location APIs
    print("\n[4] Testing Location & Parking Endpoints...")
    areas_resp = client.get("/api/parking/areas")
    print(f"  GET /api/parking/areas -> {len(areas_resp.json())} areas: {areas_resp.json()[:5]}...")
    assert len(areas_resp.json()) >= 5

    # Search parking in Guindy
    guindy_resp = client.get("/api/parking?area=Guindy")
    print(f"  GET /api/parking?area=Guindy -> Found {len(guindy_resp.json())} locations:")
    for p in guindy_resp.json():
        print(f"    - {p['parking_name']} | Fee: Rs.{p['parking_fee']}/hr | Avail Slots: {p['available_slots']} | Dist: {p['distance_km']} km")
    assert len(guindy_resp.json()) > 0

    # Search parking in Tambaram
    tambaram_resp = client.get("/api/parking?area=Tambaram")
    print(f"  GET /api/parking?area=Tambaram -> Found {len(tambaram_resp.json())} locations")
    assert len(tambaram_resp.json()) > 0

    # Search parking in T Nagar
    tnagar_resp = client.get("/api/parking?area=T Nagar")
    print(f"  GET /api/parking?area=T Nagar -> Found {len(tnagar_resp.json())} locations")
    assert len(tnagar_resp.json()) > 0

    # Parking details & slots
    detail_resp = client.get("/api/parking/1")
    print(f"  GET /api/parking/1 -> {detail_resp.json()['parking_name']} ({detail_resp.json()['available_slots']} available slots)")
    assert detail_resp.status_code == 200

    slots_resp = client.get("/api/parking/1/slots")
    print(f"  GET /api/parking/1/slots -> {len(slots_resp.json())} slots retrieved")
    assert len(slots_resp.json()) > 0

    # 5. Booking & Session Lifecycle
    print("\n[5] Testing Booking, Concurrency, Check-in & Check-out...")
    available_slot = next((s for s in slots_resp.json() if s["status"] == "available"), None)
    assert available_slot is not None, "No available slot found for testing in parking_id=1"
    print(f"  Selected available slot: ID={available_slot['slot_id']}, Number={available_slot['slot_number']}, Type={available_slot['slot_type']}")

    start_time_iso = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")

    # Create Booking
    book_resp = client.post("/api/bookings", headers=headers, json={
        "parking_id": 1,
        "slot_id": available_slot["slot_id"],
        "start_time": start_time_iso,
        "duration_hours": 2
    })
    print(f"  POST /api/bookings -> Status {book_resp.status_code}, Booking ID: {book_resp.json().get('booking_id')}, Status: {book_resp.json().get('status')}")
    assert book_resp.status_code == 201
    booking_id = book_resp.json()["booking_id"]

    # Verify slot became reserved
    slots_check1 = client.get("/api/parking/1/slots").json()
    slot_after_book = next(s for s in slots_check1 if s["slot_id"] == available_slot["slot_id"])
    print(f"  Slot state after booking -> {slot_after_book['status']} (Expected 'reserved')")
    assert slot_after_book["status"] == "reserved"

    # Concurrency / Conflict test: attempt double booking on same slot
    conflict_resp = client.post("/api/bookings", headers=headers, json={
        "parking_id": 1,
        "slot_id": available_slot["slot_id"],
        "start_time": start_time_iso,
        "duration_hours": 2
    })
    print(f"  Double booking conflict check -> Status {conflict_resp.status_code} (Expected 409 Conflict)")
    assert conflict_resp.status_code == 409

    # Verify booking appears in My Bookings
    my_bookings_resp = client.get("/api/bookings/my", headers=headers)
    print(f"  GET /api/bookings/my -> {len(my_bookings_resp.json())} bookings found")
    assert any(b["booking_id"] == booking_id for b in my_bookings_resp.json())

    # Check-in
    checkin_resp = client.post("/api/sessions/check-in", headers=headers, json={"booking_id": booking_id})
    print(f"  POST /api/sessions/check-in -> Status {checkin_resp.status_code}, Session ID: {checkin_resp.json().get('session_id')}, Session Status: {checkin_resp.json().get('status')}")
    assert checkin_resp.status_code == 201
    session_id = checkin_resp.json()["session_id"]

    # Verify slot became occupied
    slots_check2 = client.get("/api/parking/1/slots").json()
    slot_after_checkin = next(s for s in slots_check2 if s["slot_id"] == available_slot["slot_id"])
    print(f"  Slot state after check-in -> {slot_after_checkin['status']} (Expected 'occupied')")
    assert slot_after_checkin["status"] == "occupied"

    # Check-out
    checkout_resp = client.post("/api/sessions/check-out", headers=headers, json={"session_id": session_id})
    print(f"  POST /api/sessions/check-out -> Status {checkout_resp.status_code}, Session Status: {checkout_resp.json().get('status')}")
    assert checkout_resp.status_code == 200
    assert checkout_resp.json()["status"] == "completed"

    # Verify slot returned to available
    slots_check3 = client.get("/api/parking/1/slots").json()
    slot_after_checkout = next(s for s in slots_check3 if s["slot_id"] == available_slot["slot_id"])
    print(f"  Slot state after check-out -> {slot_after_checkout['status']} (Expected 'available')")
    assert slot_after_checkout["status"] == "available"

    # 6. Cancellation test
    print("\n[6] Testing Reservation Cancellation...")
    avail_slot_2 = next((s for s in slots_check3 if s["status"] == "available"), None)
    if avail_slot_2:
        book2_resp = client.post("/api/bookings", headers=headers, json={
            "parking_id": 1,
            "slot_id": avail_slot_2["slot_id"],
            "start_time": (datetime.now() + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%S"),
            "duration_hours": 1
        })
        b2_id = book2_resp.json()["booking_id"]
        print(f"  Created test reservation for cancellation: ID {b2_id}")

        cancel_resp = client.put(f"/api/bookings/{b2_id}/cancel", headers=headers)
        print(f"  PUT /api/bookings/{b2_id}/cancel -> Status {cancel_resp.status_code}, Booking Status: {cancel_resp.json().get('status')}")
        assert cancel_resp.status_code == 200
        assert cancel_resp.json()["status"] == "cancelled"

        # Verify slot released back to available
        slots_check4 = client.get("/api/parking/1/slots").json()
        slot_after_cancel = next(s for s in slots_check4 if s["slot_id"] == avail_slot_2["slot_id"])
        print(f"  Slot state after cancellation -> {slot_after_cancel['status']} (Expected 'available')")
        assert slot_after_cancel["status"] == "available"

    print("\n==================================================")
    print("ALL 6 TEST PHASES PASSED WITH 100% SUCCESS!")
    print("==================================================")


if __name__ == "__main__":
    test_all()
