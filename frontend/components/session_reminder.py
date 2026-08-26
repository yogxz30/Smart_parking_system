"""
session_reminder.py  Shared in-app reminder component (Feature 1).

Renders checkout reminders for users who have an active parking session.
Reads existing check_in + booking end_time fields  no new backend logic.
Only uses st.markdown with custom HTML  no push notifications.
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
      - info    session active, time remaining
      - warning  within 15 minutes of end_time
      - error   end_time has already passed (overtime)

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
        # No end_time available  show generic active session reminder
        st.markdown(
            f"""
            <div style="
                background: rgba(56, 189, 248, 0.12);
                border: 1px solid rgba(56, 189, 248, 0.45);
                border-left: 4px solid #38bdf8;
                border-radius: 10px;
                padding: 14px 18px;
                margin-bottom: 16px;
                display: flex;
                align-items: flex-start;
                gap: 12px;
            ">
                <span class="material-symbols-rounded" style="font-size: 1.4rem; line-height: 1;">notifications</span>
                <div>
                    <div style="color: #38bdf8; font-weight: 700; font-size: 0.92rem; margin-bottom: 3px;">
                        Active Parking Session
                    </div>
                    <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.5;">
                        You are checked in at <strong style="color: #f1f5f9;">{parking_name}</strong>,
                        Slot <strong style="color: #f1f5f9;">{slot_number}</strong>.
                        Please check out when you leave the parking facility.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return active_session

    minutes_remaining = (end_time - now).total_seconds() / 60

    if minutes_remaining < 0:
        # Overtime  red alert
        overtime_mins = abs(int(minutes_remaining))
        st.markdown(
            f"""
            <div style="
                background: rgba(239, 68, 68, 0.12);
                border: 1px solid rgba(239, 68, 68, 0.45);
                border-left: 4px solid #ef4444;
                border-radius: 10px;
                padding: 14px 18px;
                margin-bottom: 16px;
                display: flex;
                align-items: flex-start;
                gap: 12px;
            ">
                <span class="material-symbols-rounded" style="font-size: 1.4rem; line-height: 1;">warning</span>
                <div>
                    <div style="color: #f87171; font-weight: 700; font-size: 0.92rem; margin-bottom: 3px;">
                        Parking Time Has Ended  Overtime!
                    </div>
                    <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.5;">
                        You have been parked at <strong style="color: #f1f5f9;">{parking_name}</strong>
                        (Slot <strong style="color: #f1f5f9;">{slot_number}</strong>) for
                        <strong style="color: #f87171;">{overtime_mins} minute(s)</strong> past your booked duration.
                        Please check out immediately using the <strong>Complete &amp; Check-out</strong> button.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif minutes_remaining <= 15:
        # Warning: within 15 minutes of end
        mins_left = int(minutes_remaining)
        st.markdown(
            f"""
            <div style="
                background: rgba(245, 158, 11, 0.12);
                border: 1px solid rgba(245, 158, 11, 0.45);
                border-left: 4px solid #f59e0b;
                border-radius: 10px;
                padding: 14px 18px;
                margin-bottom: 16px;
                display: flex;
                align-items: flex-start;
                gap: 12px;
            ">
                <span class="material-symbols-rounded" style="font-size: 1.4rem; line-height: 1;">schedule</span>
                <div>
                    <div style="color: #fbbf24; font-weight: 700; font-size: 0.92rem; margin-bottom: 3px;">
                        Parking Time Ending Soon!
                    </div>
                    <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.5;">
                        Your session at <strong style="color: #f1f5f9;">{parking_name}</strong>
                        (Slot <strong style="color: #f1f5f9;">{slot_number}</strong>) ends in
                        <strong style="color: #fbbf24;">{mins_left} minute(s)</strong>.
                        Please prepare to check out.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Normal active session  info blue
        hours_left = int(minutes_remaining // 60)
        mins_left = int(minutes_remaining % 60)
        time_str = f"{hours_left}h {mins_left}m" if hours_left > 0 else f"{mins_left}m"
        st.markdown(
            f"""
            <div style="
                background: rgba(56, 189, 248, 0.12);
                border: 1px solid rgba(56, 189, 248, 0.45);
                border-left: 4px solid #38bdf8;
                border-radius: 10px;
                padding: 14px 18px;
                margin-bottom: 16px;
                display: flex;
                align-items: flex-start;
                gap: 12px;
            ">
                <span class="material-symbols-rounded" style="font-size: 1.4rem; line-height: 1;">notifications</span>
                <div>
                    <div style="color: #38bdf8; font-weight: 700; font-size: 0.92rem; margin-bottom: 3px;">
                        Active Parking Session
                    </div>
                    <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.5;">
                        You are checked in at <strong style="color: #f1f5f9;">{parking_name}</strong>
                        (Slot <strong style="color: #f1f5f9;">{slot_number}</strong>).
                        Approximately <strong style="color: #38bdf8;">~{time_str}</strong> remaining.
                        Please check out when you leave the parking facility.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    return active_session
