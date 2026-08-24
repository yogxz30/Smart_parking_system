import streamlit as st
import textwrap
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime


def format_dt(dt_str: Optional[str]) -> str:
    """Format ISO datetime string into user-friendly format."""
    if not dt_str:
        return "—"
    try:
        if isinstance(dt_str, datetime):
            return dt_str.strftime("%b %d, %Y • %I:%M %p")
        cleaned = str(dt_str).replace("Z", "").split(".")[0]
        dt = datetime.fromisoformat(cleaned)
        return dt.strftime("%b %d, %Y • %I:%M %p")
    except Exception:
        return str(dt_str)


def render_booking_card(
    booking: Dict[str, Any],
    on_checkin_callback: Optional[Callable[[int], None]] = None,
    on_checkout_callback: Optional[Callable[[int], None]] = None,
    on_cancel_callback: Optional[Callable[[int], None]] = None
):
    """
    Renders an interactive booking card with status badge and lifecycle action buttons.
    """
    b_id = booking.get("booking_id")
    status = str(booking.get("status", "reserved")).lower()

    status_styles = {
        "reserved": ("#fbbf24", "rgba(245, 158, 11, 0.2)", "🟡 Reserved (Awaiting Arrival)"),
        "active": ("#60a5fa", "rgba(59, 130, 246, 0.2)", "⚡ Active (Parked)"),
        "completed": ("#34d399", "rgba(16, 185, 129, 0.2)", "✅ Completed"),
        "cancelled": ("#f87171", "rgba(239, 68, 68, 0.2)", "❌ Cancelled")
    }

    color, bg, status_text = status_styles.get(status, ("#94a3b8", "rgba(148, 163, 184, 0.2)", status.capitalize()))

    raw_html = f"""
<div style="
    background: rgba(30, 41, 59, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-left: 4px solid {color};
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 14px;
">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
        <div>
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                <span style="font-size: 1.2rem; font-weight: 800; color: #ffffff;">
                    {booking.get('parking_name', 'Parking Facility')}
                </span>
                <span style="
                    background: rgba(99, 102, 241, 0.25);
                    color: #c7d2fe;
                    border: 1px solid rgba(99, 102, 241, 0.5);
                    padding: 2px 10px;
                    border-radius: 6px;
                    font-size: 0.8rem;
                    font-weight: 700;
                ">
                    Booking #{b_id}
                </span>
            </div>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 0 0 8px 0;">
                📍 Area: <strong style="color: #ffffff;">{booking.get('area', 'N/A')}</strong> &nbsp;|&nbsp; 
                Slot: <strong style="color: #60a5fa; font-size: 1rem;">{booking.get('slot_number', 'N/A')}</strong> ({str(booking.get('slot_type', 'normal')).upper()})
            </p>
            <p style="color: #cbd5e1; font-size: 0.88rem; margin: 0;">
                🕒 <strong>From:</strong> {format_dt(booking.get('start_time'))} &nbsp; 
                <strong>To:</strong> {format_dt(booking.get('end_time'))}
            </p>
        </div>
        <div>
            <span style="
                background: {bg};
                color: {color};
                border: 1px solid {color}80;
                padding: 6px 14px;
                border-radius: 8px;
                font-weight: 800;
                font-size: 0.9rem;
                display: inline-block;
            ">
                {status_text}
            </span>
        </div>
    </div>
</div>
"""
    st.markdown(textwrap.dedent(raw_html).strip(), unsafe_allow_html=True)

    # Action Buttons Row
    if status in ["reserved", "active"]:
        cols = st.columns([1.5, 1.5, 3])
        if status == "reserved":
            with cols[0]:
                if st.button(f"⚡ Check-in Now", key=f"btn_ci_{b_id}", use_container_width=True, type="primary"):
                    if on_checkin_callback:
                        on_checkin_callback(b_id)
            with cols[1]:
                if st.button(f"❌ Cancel Booking", key=f"btn_cn_{b_id}", use_container_width=True):
                    if on_cancel_callback:
                        on_cancel_callback(b_id)
        elif status == "active":
            with cols[0]:
                if st.button(f"🏁 Complete & Check-out", key=f"btn_co_{b_id}", use_container_width=True, type="primary"):
                    if on_checkout_callback:
                        on_checkout_callback(b_id)


def render_sessions_table(sessions: List[Dict[str, Any]]):
    """Renders user parking check-in/out session logs in a clear structured view."""
    if not sessions:
        st.info("No physical parking sessions recorded yet.")
        return

    for s in sessions:
        status = str(s.get("status", "active")).lower()
        badge_color = "#60a5fa" if status == "active" else "#34d399"
        badge_text = "⚡ In Progress" if status == "active" else "✅ Completed"

        raw_html = f"""
<div style="
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
        <div>
            <strong style="color: #ffffff; font-size: 1.05rem;">
                {s.get('parking_name', 'Parking Facility')} • Slot {s.get('slot_number', 'N/A')}
            </strong>
            <div style="color: #cbd5e1; font-size: 0.85rem; margin-top: 6px;">
                📥 <strong>Check-in:</strong> {format_dt(s.get('check_in'))} &nbsp;|&nbsp; 
                📤 <strong>Check-out:</strong> {format_dt(s.get('check_out'))}
            </div>
        </div>
        <div>
            <span style="
                background: {badge_color}25;
                color: {badge_color};
                border: 1px solid {badge_color}70;
                padding: 4px 12px;
                border-radius: 6px;
                font-size: 0.8rem;
                font-weight: 800;
            ">
                {badge_text}
            </span>
        </div>
    </div>
</div>
"""
        st.markdown(textwrap.dedent(raw_html).strip(), unsafe_allow_html=True)
