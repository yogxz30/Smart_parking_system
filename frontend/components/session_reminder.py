"""
session_reminder.py — Shared in-app reminder component (Feature 1).

Renders checkout reminders for users who have an active parking session.
Reads existing check_in + booking end_time fields — no new backend logic.
Only uses st.info / st.warning / st.error — no push notifications.
"""
import streamlit as st
from datetime import datetime
from typing import Optional
from frontend.components.api_client import api


def render_session_reminder(token: str) -> Optional[dict]:
    """
    Check if the authenticated user has an active (checked-in, not checked-out)
    parking session and render the appropriate Streamlit alert.

    Returns the active session dict if found, or None.
    Shows:
      - st.info   → session active, time remaining
      - st.warning → within 15 minutes of end_time
      - st.error  → end_time has already passed (overtime)

    Does NOT auto checkout, does NOT change slot/booking status.
    """
    sessions_res = api.get_my_sessions(token)
    bookings_res = api.get_my_bookings(token)

    if not sessions_res.get("success") or not bookings_res.get("success"):
        return None

    sessions = sessions_res.get("data", [])
    bookings = bookings_res.get("data", [])

    # Find the active session (check_in set, check_out is None/null)
    active_session = None
    for s in sessions:
        if str(s.get("status", "")).lower() == "active" and s.get("check_in") and not s.get("check_out"):
            active_session = s
            break

    if not active_session:
        return None

    # Find matching booking to get end_time (expected parking duration end)
    booking_id = active_session.get("booking_id")
    matched_booking = None
    for b in bookings:
        if b.get("booking_id") == booking_id:
            matched_booking = b
            break

    now = datetime.now()
    end_time = None

    if matched_booking and matched_booking.get("end_time"):
        try:
            end_str = str(matched_booking["end_time"]).replace("Z", "").split(".")[0]
            end_time = datetime.fromisoformat(end_str)
        except Exception:
            end_time = None

    parking_name = active_session.get("parking_name", "your parking facility")
    slot_number = active_session.get("slot_number", "N/A")

    if end_time is None:
        # No end_time available — show generic active session reminder
        st.info(
            f"🔔 **Active Parking Session** — You are checked in at **{parking_name}**, "
            f"Slot **{slot_number}**. Please check out when you leave the parking facility.",
            icon="🔔"
        )
        return active_session

    minutes_remaining = (end_time - now).total_seconds() / 60

    if minutes_remaining < 0:
        # Overtime
        overtime_mins = abs(int(minutes_remaining))
        st.error(
            f"⚠️ **Your parking time has ended!** You have been parked at **{parking_name}** "
            f"(Slot **{slot_number}**) for **{overtime_mins} minute(s)** past your booked duration. "
            f"Please check out immediately using the **Complete & Check-out** button.",
            icon="⚠️"
        )
    elif minutes_remaining <= 15:
        # Warning: within 15 minutes of end
        mins_left = int(minutes_remaining)
        st.warning(
            f"⏰ **Parking time ending soon!** Your session at **{parking_name}** "
            f"(Slot **{slot_number}**) ends in **{mins_left} minute(s)**. "
            f"Please prepare to check out.",
            icon="⏰"
        )
    else:
        # Normal active session
        hours_left = int(minutes_remaining // 60)
        mins_left = int(minutes_remaining % 60)
        time_str = f"{hours_left}h {mins_left}m" if hours_left > 0 else f"{mins_left}m"
        st.info(
            f"🔔 **Your parking session is still active.** You are checked in at **{parking_name}** "
            f"(Slot **{slot_number}**). ~{time_str} remaining. "
            f"Please check out when you leave the parking facility.",
            icon="🔔"
        )

    return active_session
