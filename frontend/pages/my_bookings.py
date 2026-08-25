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
        st.markdown(
            '<div style="background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.4);'
            'border-left:4px solid #f59e0b;border-radius:10px;padding:14px 18px;color:#fde68a;'
            'font-weight:600;margin-bottom:16px;">⚠️ Please sign in to view your bookings.</div>',
            unsafe_allow_html=True
        )
        st.session_state["active_page"] = "login"
        st.rerun()

    # ── Header ──────────────────────────────────────────────────────────────
    header_html = (
        '<div style="margin-bottom:20px;">'
        '<div style="display:flex;align-items:center;gap:12px;">'
        '<h1 style="color:#f8fafc;font-size:1.9rem;font-weight:800;margin:0;">📅 My Parking Bookings</h1>'
        '</div>'
        '<p style="color:#94a3b8;font-size:0.95rem;margin:6px 0 0 0;">'
        'Track your active reservations, perform Check-in / Check-out, and view your complete parking history.'
        '</p></div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    # ── Action Handlers ──────────────────────────────────────────────────────
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

    # ── Fetch bookings ───────────────────────────────────────────────────────
    with st.spinner("Loading bookings..."):
        b_res = api.get_my_bookings(token)
        s_res = api.get_my_sessions(token)

    bookings = b_res.get("data", []) if b_res.get("success") else []
    sessions = s_res.get("data", []) if s_res.get("success") else []

    active_bookings = [b for b in bookings if str(b.get("status", "")).lower() in ["reserved", "active"]]
    past_bookings = [b for b in bookings if str(b.get("status", "")).lower() in ["completed", "cancelled"]]

    # ── Tabbed Interface ─────────────────────────────────────────────────────
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
            # Styled empty state
            st.markdown(
                """
                <div style="
                    background: rgba(30, 41, 59, 0.6);
                    border: 1px solid rgba(148, 163, 184, 0.2);
                    border-radius: 14px;
                    padding: 36px 24px;
                    text-align: center;
                    margin: 12px 0;
                ">
                    <div style="font-size: 2.5rem; margin-bottom: 12px;">📭</div>
                    <div style="color: #f1f5f9; font-size: 1.05rem; font-weight: 700; margin-bottom: 6px;">
                        No Active or Upcoming Reservations
                    </div>
                    <div style="color: #94a3b8; font-size: 0.88rem;">
                        You don't have any confirmed bookings right now. Find a spot to get started!
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            if st.button("📍 Find a Parking Space Now", key="myb_btn_find_parking", type="primary", use_container_width=False):
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
            st.markdown(
                """
                <div style="
                    background: rgba(30, 41, 59, 0.6);
                    border: 1px solid rgba(148, 163, 184, 0.2);
                    border-radius: 14px;
                    padding: 36px 24px;
                    text-align: center;
                    margin: 12px 0;
                ">
                    <div style="font-size: 2.5rem; margin-bottom: 12px;">📂</div>
                    <div style="color: #f1f5f9; font-size: 1.05rem; font-weight: 700; margin-bottom: 6px;">
                        No Booking History Yet
                    </div>
                    <div style="color: #94a3b8; font-size: 0.88rem;">
                        Completed and cancelled bookings will appear here once you start using the system.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # =========================================================================
    # Tab 3: Physical Sessions Log
    # =========================================================================
    with tab_sessions:
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        render_sessions_table(sessions)
