import streamlit as st
import textwrap
from frontend.components.api_client import api
from frontend.components.tables import render_booking_card, render_sessions_table
from frontend.components.session_reminder import render_session_reminder


def render_my_bookings():
    """
    Renders the My Bookings & Parking Sessions page with cancellation,
    check-in, check-out, and complete session history tracking.
    Feature 1: Active session checkout reminder shown at top of Active & Upcoming tab.
    """
    token = st.session_state.get("token")
    if not token:
        st.warning("Please sign in to view your bookings.")
        st.session_state["active_page"] = "login"
        st.rerun()

    header_html = (
        '<div style="margin-bottom:20px;">'
        '<h1 style="color:#ffffff;font-size:1.8rem;font-weight:800;margin:0;">📅 My Parking Bookings</h1>'
        '<p style="color:#cbd5e1;font-size:0.95rem;margin:4px 0 0 0;">'
        'Track your active reservations, perform Check-in / Check-out, and view your complete parking history.'
        '</p></div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    # Action Handlers
    def handle_checkin(booking_id: int):
        with st.spinner("Checking in..."):
            res = api.check_in(token, booking_id)
            if res.get("success"):
                st.success("✅ Check-in successful! Your session is now active.")
                st.rerun()
            else:
                st.error(f"❌ Check-in failed: {res.get('error')}")

    def handle_checkout(booking_id: int):
        with st.spinner("Checking out..."):
            res = api.check_out(token, booking_id=booking_id)
            if res.get("success"):
                st.success("🎉 Check-out complete! Your parking slot has been released.")
                st.rerun()
            else:
                st.error(f"❌ Check-out failed: {res.get('error')}")

    def handle_cancel(booking_id: int):
        with st.spinner("Cancelling reservation..."):
            res = api.cancel_booking(token, booking_id)
            if res.get("success"):
                st.success("✅ Reservation cancelled and slot returned to available.")
                st.rerun()
            else:
                st.error(f"❌ Cancellation failed: {res.get('error')}")

    # Fetch user's bookings
    with st.spinner("Loading bookings..."):
        b_res = api.get_my_bookings(token)
        s_res = api.get_my_sessions(token)

    bookings = b_res.get("data", []) if b_res.get("success") else []
    sessions = s_res.get("data", []) if s_res.get("success") else []

    active_bookings = [b for b in bookings if str(b.get("status", "")).lower() in ["reserved", "active"]]
    past_bookings = [b for b in bookings if str(b.get("status", "")).lower() in ["completed", "cancelled"]]

    # Tabbed Interface
    tab_active, tab_history, tab_sessions = st.tabs([
        f"⚡ Active & Upcoming ({len(active_bookings)})",
        f"📜 Booking History ({len(past_bookings)})",
        f"🚗 Parking Sessions Log ({len(sessions)})"
    ])

    # =========================================================================
    # Tab 1: Active & Upcoming — Feature 1: session reminder at top
    # =========================================================================
    with tab_active:
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        # Feature 1: Show checkout reminder if an active session exists
        render_session_reminder(token)

        if active_bookings:
            for b in active_bookings:
                render_booking_card(
                    b,
                    on_checkin_callback=handle_checkin,
                    on_checkout_callback=handle_checkout,
                    on_cancel_callback=handle_cancel
                )
        else:
            st.info("You do not have any active or upcoming reservations.")
            if st.button("📍 Find a Parking Space Now", key="myb_btn_find_parking", type="primary"):
                st.session_state["active_page"] = "search"
                st.rerun()

    # =========================================================================
    # Tab 2: Booking History
    # =========================================================================
    with tab_history:
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        if past_bookings:
            for b in past_bookings:
                render_booking_card(b)
        else:
            st.info("No past bookings recorded yet.")

    # =========================================================================
    # Tab 3: Physical Sessions Log
    # =========================================================================
    with tab_sessions:
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        render_sessions_table(sessions)
