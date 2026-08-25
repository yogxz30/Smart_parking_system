import streamlit as st
import textwrap
from datetime import datetime, timedelta, time
from frontend.components.api_client import api
from frontend.components.tables import format_dt


def render_booking_flow():
    """
    Renders the slot reservation flow with datetime selection,
    duration calculation, pricing estimate, and transactional confirmation.
    Feature 2: Cash payment selection step added (frontend-only, no DB column needed).
    Feature 7: Booking receipt/summary card + "Download as text" button after confirmation.
    """
    token = st.session_state.get("token")
    if not token:
        st.warning("Please sign in to make a parking reservation.")
        st.session_state["active_page"] = "login"
        st.rerun()

    parking = st.session_state.get("selected_parking")
    slot = st.session_state.get("selected_slot")

    st.markdown(
        '<div style="margin-bottom:20px;">'
        '<h1 style="color:#ffffff;font-size:1.8rem;font-weight:800;margin:0;">🎫 Reserve Parking Slot</h1>'
        '<p style="color:#cbd5e1;font-size:0.95rem;margin:4px 0 0 0;">'
        'Review slot details, choose your parking duration, select payment method, and confirm your reservation.'
        '</p></div>',
        unsafe_allow_html=True
    )

    if not parking or not slot:
        st.warning("⚠️ No parking slot currently selected. Please choose a parking facility and available slot first.")
        if st.button("📍 Browse Parking Locations", key="btn_book_browse", type="primary"):
            st.session_state["active_page"] = "search"
            st.rerun()
        return

    # =========================================================================
    # Feature 7: Show booking receipt after successful confirmation
    # =========================================================================
    if st.session_state.get("last_booking_receipt"):
        receipt = st.session_state["last_booking_receipt"]
        _render_booking_receipt(receipt)
        return

    # Two column layout: Details on left, Duration & Confirmation on right
    col_left, col_right = st.columns([1.2, 1.8])

    with col_left:
        facility_card_html = (
            '<div style="background:rgba(30,41,59,0.85);border:1px solid rgba(148,163,184,0.25);'
            'border-radius:12px;padding:20px;margin-bottom:15px;box-shadow:0 4px 14px rgba(0,0,0,0.2);">'
            '<p style="color:#60a5fa;font-size:0.8rem;font-weight:800;text-transform:uppercase;'
            'letter-spacing:1px;margin:0 0 6px 0;">Selected Facility</p>'
            '<h3 style="color:#ffffff;font-size:1.25rem;font-weight:700;margin:0 0 8px 0;">'
            '{parking_name}</h3>'
            '<p style="color:#cbd5e1;font-size:0.88rem;margin:0 0 14px 0;">'
            '📍 {address}</p>'
            '<hr style="border:0;border-top:1px solid rgba(148,163,184,0.2);margin:12px 0;">'
            '<div style="display:flex;justify-content:space-between;margin-bottom:8px;">'
            '<span style="color:#94a3b8;font-size:0.88rem;font-weight:600;">Slot Number:</span>'
            '<strong style="color:#34d399;font-size:1.1rem;">{slot_number}</strong>'
            '</div>'
            '<div style="display:flex;justify-content:space-between;margin-bottom:8px;">'
            '<span style="color:#94a3b8;font-size:0.88rem;font-weight:600;">Slot Type:</span>'
            '<strong style="color:#ffffff;font-size:0.95rem;text-transform:uppercase;">{slot_type}</strong>'
            '</div>'
            '<div style="display:flex;justify-content:space-between;margin-bottom:6px;">'
            '<span style="color:#94a3b8;font-size:0.88rem;font-weight:600;">Rate:</span>'
            '<strong style="color:#60a5fa;font-size:1.05rem;">₹{parking_fee:.2f} / hr</strong>'
            '</div></div>'
        ).format(
            parking_name=parking.get("parking_name", ""),
            address=parking.get("address") or parking.get("area", ""),
            slot_number=slot.get("slot_number", ""),
            slot_type=slot.get("slot_type", "normal"),
            parking_fee=float(parking.get("parking_fee", 0))
        )
        st.markdown(facility_card_html, unsafe_allow_html=True)

        if st.button("⬅️ Choose Different Slot", key="btn_book_change_slot", use_container_width=True):
            st.session_state["selected_parking"] = None
            st.session_state["selected_slot"] = None
            st.session_state["active_page"] = "search"
            st.rerun()

    with col_right:
        st.markdown(
            '<div style="background:rgba(15,23,42,0.7);border:1px solid rgba(148,163,184,0.2);'
            'border-radius:12px;padding:16px 20px;margin-bottom:12px;">'
            '<h4 style="color:#ffffff;font-size:1.1rem;font-weight:700;margin:0;">'
            '⏰ Parking Schedule & Duration</h4></div>',
            unsafe_allow_html=True
        )

        now = datetime.now()

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            start_date = st.date_input("Start Date", value=now.date(), min_value=now.date(), key="book_start_date")
        with d_col2:
            default_time = (now + timedelta(minutes=15)).time()
            start_time_val = st.time_input("Start Time", value=time(default_time.hour, default_time.minute), key="book_start_time")

        duration_hours = st.slider(
            "Parking Duration (Hours)",
            min_value=1,
            max_value=12,
            value=2,
            step=1,
            help="Select how many hours you intend to reserve this slot",
            key="book_duration_slider"
        )

        # Calculate exact start_time and end_time
        start_datetime = datetime.combine(start_date, start_time_val)
        end_datetime = start_datetime + timedelta(hours=duration_hours)
        total_fee = float(parking.get("parking_fee", 0)) * duration_hours

        # Summary Breakdown Card
        summary_html = (
            '<div style="background:rgba(30,41,59,0.95);border:1px solid rgba(59,130,246,0.45);'
            'border-radius:10px;padding:16px 20px;margin:15px 0;">'
            '<div style="display:flex;justify-content:space-between;margin-bottom:6px;">'
            '<span style="color:#94a3b8;font-size:0.88rem;font-weight:600;">Arrival Time:</span>'
            '<strong style="color:#ffffff;font-size:0.95rem;">{start}</strong>'
            '</div>'
            '<div style="display:flex;justify-content:space-between;margin-bottom:6px;">'
            '<span style="color:#94a3b8;font-size:0.88rem;font-weight:600;">Departure Time:</span>'
            '<strong style="color:#ffffff;font-size:0.95rem;">{end}</strong>'
            '</div>'
            '<div style="display:flex;justify-content:space-between;margin-bottom:6px;">'
            '<span style="color:#94a3b8;font-size:0.88rem;font-weight:600;">Duration:</span>'
            '<strong style="color:#60a5fa;font-size:0.95rem;">{duration} Hour(s)</strong>'
            '</div>'
            '<hr style="border:0;border-top:1px solid rgba(148,163,184,0.25);margin:8px 0;">'
            '<div style="display:flex;justify-content:space-between;align-items:center;">'
            '<span style="color:#ffffff;font-weight:700;font-size:1.05rem;">Total Parking Fee:</span>'
            '<span style="color:#34d399;font-weight:800;font-size:1.4rem;">₹{fee:.2f}</span>'
            '</div></div>'
        ).format(
            start=format_dt(start_datetime),
            end=format_dt(end_datetime),
            duration=duration_hours,
            fee=total_fee
        )
        st.markdown(summary_html, unsafe_allow_html=True)

        # =====================================================================
        # Feature 2: Payment Method Step (frontend-only — no DB column)
        # =====================================================================
        st.markdown(
            '<div style="background:rgba(15,23,42,0.7);border:1px solid rgba(148,163,184,0.2);'
            'border-radius:12px;padding:14px 20px;margin-bottom:14px;">'
            '<h4 style="color:#ffffff;font-size:1.05rem;font-weight:700;margin:0 0 8px 0;">'
            '💳 Payment Method</h4>'
            '<p style="color:#cbd5e1;font-size:0.85rem;margin:0;">'
            'Select how you will pay for this parking session.</p>'
            '</div>',
            unsafe_allow_html=True
        )

        payment_method = st.radio(
            "Select Payment Method",
            options=["💵 Cash"],
            index=0,
            key="book_payment_method",
            help="Pay the parking fee physically at the facility counter or booth.",
            label_visibility="collapsed"
        )

        st.markdown(
            '<div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.35);'
            'border-radius:8px;padding:10px 14px;margin-bottom:14px;color:#6ee7b7;font-size:0.88rem;">'
            '💵 <strong>Cash Payment:</strong> Please pay the parking fee physically at the parking '
            'facility counter or booth upon arrival.'
            '</div>',
            unsafe_allow_html=True
        )

        # Confirm Reservation Button
        if st.button("🔒 Confirm & Reserve Slot", key="btn_book_submit", use_container_width=True, type="primary"):
            with st.spinner("Submitting your reservation to backend..."):
                start_iso = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")
                res = api.create_booking(
                    token=token,
                    parking_id=parking.get("parking_id"),
                    slot_id=slot.get("slot_id"),
                    start_time_iso=start_iso,
                    duration_hours=duration_hours
                )

                if res.get("success"):
                    booking_data = res.get("data", {})
                    # Feature 7: Store receipt data in session_state to show receipt
                    st.session_state["last_booking_receipt"] = {
                        "booking_id": booking_data.get("booking_id"),
                        "parking_name": parking.get("parking_name"),
                        "area": parking.get("address") or parking.get("area"),
                        "slot_number": slot.get("slot_number"),
                        "slot_type": slot.get("slot_type", "normal"),
                        "start_time": format_dt(start_datetime),
                        "end_time": format_dt(end_datetime),
                        "duration_hours": duration_hours,
                        "total_fee": total_fee,
                        "payment_method": "Cash",
                        "created_at": datetime.now().strftime("%b %d, %Y • %I:%M %p")
                    }
                    st.session_state["selected_parking"] = None
                    st.session_state["selected_slot"] = None
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ Reservation failed: {res.get('error')}")


def _render_booking_receipt(receipt: dict):
    """
    Feature 7: Renders the post-confirmation booking receipt/summary card
    with a 'Download as text' button. No payment simulation.
    """
    st.markdown(
        '<div style="margin-bottom:20px;">'
        '<h1 style="color:#ffffff;font-size:1.8rem;font-weight:800;margin:0;">'
        '🎉 Booking Confirmed!</h1>'
        '<p style="color:#cbd5e1;font-size:0.95rem;margin:4px 0 0 0;">'
        'Your parking slot has been successfully reserved. Here is your booking summary.'
        '</p></div>',
        unsafe_allow_html=True
    )

    # Success banner
    st.success(f"✅ Booking #{receipt.get('booking_id')} confirmed! Your slot is reserved.")

    # Receipt Card
    receipt_html = (
        '<div style="background:rgba(30,41,59,0.95);border:1px solid rgba(59,130,246,0.5);'
        'border-left:5px solid #3b82f6;border-radius:12px;padding:24px;margin:16px 0;">'
        '<div style="display:flex;align-items:center;gap:10px;margin-bottom:18px;">'
        '<span style="font-size:1.4rem;">🧾</span>'
        '<h3 style="color:#ffffff;margin:0;font-size:1.25rem;font-weight:800;">Booking Receipt</h3>'
        '<span style="background:rgba(99,102,241,0.25);color:#c7d2fe;border:1px solid rgba(99,102,241,0.5);'
        'padding:2px 10px;border-radius:6px;font-size:0.8rem;font-weight:700;">'
        'Booking #{booking_id}</span>'
        '</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">'
        '<div><p style="color:#94a3b8;font-size:0.8rem;font-weight:600;margin:0 0 2px;">Parking Facility</p>'
        '<strong style="color:#ffffff;font-size:1rem;">{parking_name}</strong></div>'
        '<div><p style="color:#94a3b8;font-size:0.8rem;font-weight:600;margin:0 0 2px;">Location</p>'
        '<strong style="color:#cbd5e1;font-size:0.95rem;">{area}</strong></div>'
        '<div><p style="color:#94a3b8;font-size:0.8rem;font-weight:600;margin:0 0 2px;">Slot Number</p>'
        '<strong style="color:#34d399;font-size:1.1rem;">{slot_number}</strong></div>'
        '<div><p style="color:#94a3b8;font-size:0.8rem;font-weight:600;margin:0 0 2px;">Slot Type</p>'
        '<strong style="color:#ffffff;font-size:0.95rem;text-transform:uppercase;">{slot_type}</strong></div>'
        '<div><p style="color:#94a3b8;font-size:0.8rem;font-weight:600;margin:0 0 2px;">Arrival Time</p>'
        '<strong style="color:#ffffff;font-size:0.9rem;">{start_time}</strong></div>'
        '<div><p style="color:#94a3b8;font-size:0.8rem;font-weight:600;margin:0 0 2px;">Departure Time</p>'
        '<strong style="color:#ffffff;font-size:0.9rem;">{end_time}</strong></div>'
        '<div><p style="color:#94a3b8;font-size:0.8rem;font-weight:600;margin:0 0 2px;">Duration</p>'
        '<strong style="color:#60a5fa;font-size:0.95rem;">{duration} Hour(s)</strong></div>'
        '<div><p style="color:#94a3b8;font-size:0.8rem;font-weight:600;margin:0 0 2px;">Booking Date</p>'
        '<strong style="color:#cbd5e1;font-size:0.9rem;">{created_at}</strong></div>'
        '</div>'
        '<hr style="border:0;border-top:1px solid rgba(148,163,184,0.25);margin:16px 0;">'
        '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">'
        '<div>'
        '<p style="color:#94a3b8;font-size:0.8rem;font-weight:600;margin:0 0 2px;">Payment Method</p>'
        '<strong style="color:#fbbf24;font-size:1.05rem;">💵 {payment_method}</strong>'
        '</div>'
        '<div style="text-align:right;">'
        '<p style="color:#94a3b8;font-size:0.8rem;font-weight:600;margin:0 0 2px;">Total Fee</p>'
        '<strong style="color:#34d399;font-size:1.6rem;font-weight:800;">₹{total_fee:.2f}</strong>'
        '</div>'
        '</div>'
        '<div style="background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.4);'
        'border-radius:8px;padding:10px 14px;margin-top:14px;color:#fde68a;font-size:0.88rem;">'
        '💵 <strong>Payment Instruction:</strong> Please pay ₹{total_fee:.2f} in cash at the '
        'parking facility counter or booth upon arrival. Keep this receipt as your booking proof.'
        '</div>'
        '</div>'
    ).format(**receipt)

    st.markdown(receipt_html, unsafe_allow_html=True)

    # Feature 7: Download as text button
    txt_content = _generate_receipt_txt(receipt)
    st.download_button(
        label="📥 Download Booking Receipt (.txt)",
        data=txt_content,
        file_name=f"booking_receipt_{receipt.get('booking_id', 'unknown')}.txt",
        mime="text/plain",
        key="btn_download_receipt",
        use_container_width=True
    )

    # Navigation buttons
    nav_col1, nav_col2 = st.columns(2)
    with nav_col1:
        if st.button("📅 View My Bookings", key="btn_receipt_my_bookings", use_container_width=True, type="primary"):
            st.session_state.pop("last_booking_receipt", None)
            st.session_state["active_page"] = "my_bookings"
            st.rerun()
    with nav_col2:
        if st.button("🏠 Go to Dashboard", key="btn_receipt_dashboard", use_container_width=True):
            st.session_state.pop("last_booking_receipt", None)
            st.session_state["active_page"] = "dashboard"
            st.rerun()


def _generate_receipt_txt(receipt: dict) -> str:
    """Generate a plain-text booking receipt for download. No payment simulation."""
    lines = [
        "=" * 55,
        "        SMART PARKING FINDER & MANAGEMENT SYSTEM",
        "                  BOOKING RECEIPT",
        "=" * 55,
        f"  Booking ID     : #{receipt.get('booking_id', 'N/A')}",
        f"  Booking Date   : {receipt.get('created_at', 'N/A')}",
        "-" * 55,
        f"  Parking Name   : {receipt.get('parking_name', 'N/A')}",
        f"  Location       : {receipt.get('area', 'N/A')}",
        f"  Slot Number    : {receipt.get('slot_number', 'N/A')}",
        f"  Slot Type      : {str(receipt.get('slot_type', 'Normal')).upper()}",
        "-" * 55,
        f"  Arrival Time   : {receipt.get('start_time', 'N/A')}",
        f"  Departure Time : {receipt.get('end_time', 'N/A')}",
        f"  Duration       : {receipt.get('duration_hours', 0)} Hour(s)",
        "-" * 55,
        f"  Total Fee      : Rs. {receipt.get('total_fee', 0):.2f}",
        f"  Payment Method : {receipt.get('payment_method', 'Cash')}",
        "-" * 55,
        "  PAYMENT INSTRUCTION:",
        f"  Please pay Rs. {receipt.get('total_fee', 0):.2f} in cash at the",
        "  parking facility counter or booth upon arrival.",
        "=" * 55,
        "  This document serves as your booking proof.",
        "  Smart Parking Finder & Management System",
        "=" * 55,
    ]
    return "\n".join(lines)
