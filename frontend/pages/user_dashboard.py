import streamlit as st
from datetime import datetime
from frontend.components.api_client import api
from frontend.components.cards import render_kpi_card
from frontend.components.tables import render_booking_card, format_dt
from frontend.components.session_reminder import render_session_reminder


def render_user_dashboard():
    """
    Renders the rich User Dashboard with KPI stats, active booking banner,
    lifecycle action buttons (Check-in/out), and quick navigation shortcuts.
    Feature 1: Active session checkout reminder (via shared session_reminder).
    Feature 3: Refresh button, color-coded badges, columns layout, empty-state.
    """
    token = st.session_state.get("token")
    user = st.session_state.get("user", {})

    if not token:
        st.warning("Please log in to access your dashboard.")
        st.session_state["active_page"] = "login"
        st.rerun()

    # =========================================================================
    # Header & Greeting
    # =========================================================================
    header_html = (
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;'
        'flex-wrap:wrap;gap:14px;margin-bottom:22px;">'
        '<div>'
        '<h1 style="color:#ffffff;font-size:1.9rem;font-weight:800;margin:0;">'
        f'Welcome back, {user.get("name", "Driver")}! 👋'
        '</h1>'
        '<p style="color:#cbd5e1;font-size:0.95rem;margin:6px 0 0 0;">'
        'Find, reserve, and manage your parking sessions across Chennai with real-time slot tracking.'
        '</p>'
        '</div></div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    # =========================================================================
    # Feature 1: Active session checkout reminder (top of page)
    # =========================================================================
    render_session_reminder(token)

    # =========================================================================
    # Feature 3: Manual Refresh Button
    # =========================================================================
    refresh_col, _ = st.columns([1.2, 4.8])
    with refresh_col:
        if st.button("🔄 Refresh Data", key="btn_dash_refresh", use_container_width=True):
            st.rerun()

    # Fetch fresh dashboard data from FastAPI
    result = api.get_user_dashboard(token)
    if not result.get("success"):
        st.error(f"Failed to load dashboard data: {result.get('error')}")
        return

    data = result.get("data", {})
    stats = data.get("stats", {})
    active_booking = data.get("active_booking")
    recent_bookings = data.get("recent_bookings", [])

    # Action Handlers
    def handle_checkin(booking_id: int):
        with st.spinner("Processing check-in..."):
            res = api.check_in(token, booking_id)
            if res.get("success"):
                st.success("✅ Check-in successful! Your slot is now marked as Occupied.")
                st.rerun()
            else:
                st.error(f"❌ Check-in failed: {res.get('error')}")

    def handle_checkout(booking_id: int):
        with st.spinner("Processing check-out..."):
            res = api.check_out(token, booking_id=booking_id)
            if res.get("success"):
                st.success("🎉 Check-out complete! Thank you for using Smart Parking.")
                st.rerun()
            else:
                st.error(f"❌ Check-out failed: {res.get('error')}")

    def handle_cancel(booking_id: int):
        with st.spinner("Cancelling reservation..."):
            res = api.cancel_booking(token, booking_id)
            if res.get("success"):
                st.success("✅ Reservation cancelled and slot released.")
                st.rerun()
            else:
                st.error(f"❌ Cancellation failed: {res.get('error')}")

    # =========================================================================
    # High-contrast KPI cards
    # =========================================================================
    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        render_kpi_card(
            title="Nearby Parking",
            value=stats.get("nearby_parking_count", 0),
            subtitle="Active facilities in Chennai",
            icon="🏢",
            theme="blue",
        )

    with kpi2:
        render_kpi_card(
            title="Available Slots",
            value=stats.get("available_slots_count", 0),
            subtitle="Ready for reservation now",
            icon="🅿️",
            theme="green",
        )

    with kpi3:
        render_kpi_card(
            title="Active Bookings",
            value=stats.get("active_bookings_count", 0),
            subtitle="Reserved & active sessions",
            icon="🎫",
            theme="amber",
        )

    # =========================================================================
    # Quick Navigation Actions
    # =========================================================================
    st.markdown(
        "<h4 style='color:#f1f5f9;font-size:1.05rem;font-weight:700;margin:18px 0 10px 0;'>"
        "⚡ Quick Actions</h4>",
        unsafe_allow_html=True
    )
    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        if st.button("📍 Book New Slot", key="btn_dash_find_parking", use_container_width=True, type="primary"):
            st.session_state["active_page"] = "search"
            st.rerun()
    with qa2:
        if st.button("📅 View My Bookings", key="btn_dash_my_bookings", use_container_width=True):
            st.session_state["active_page"] = "my_bookings"
            st.rerun()
    with qa3:
        if st.button("👤 View My Profile", key="btn_dash_profile", use_container_width=True):
            st.session_state["active_page"] = "profile"
            st.rerun()

    st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # Current Active Booking
    # =========================================================================
    st.markdown(
        "<h3 style='color:#ffffff;font-size:1.3rem;font-weight:800;margin:22px 0 12px 0;'>"
        "🚗 Active Parking Session</h3>",
        unsafe_allow_html=True
    )

    if active_booking:
        booking_status = str(active_booking.get("status", "")).lower()
        if booking_status == "active":
            st.markdown(
                '<div style="background:rgba(59,130,246,0.15);border:1px solid rgba(59,130,246,0.4);'
                'border-radius:8px;padding:8px 14px;margin-bottom:10px;color:#93c5fd;'
                'font-size:0.9rem;font-weight:600;">⚡ Check-in Active — You are currently parked. '
                'Use the Check-out button when you are ready to leave.</div>',
                unsafe_allow_html=True
            )
        render_booking_card(
            active_booking,
            on_checkin_callback=handle_checkin,
            on_checkout_callback=handle_checkout,
            on_cancel_callback=handle_cancel
        )
    else:
        st.markdown(
            '<div style="background:rgba(30,41,59,0.5);border:1px dashed rgba(148,163,184,0.3);'
            'border-radius:12px;padding:26px;text-align:center;margin-bottom:20px;">'
            '<span style="font-size:2.2rem;">🏖️</span>'
            '<h4 style="color:#ffffff;margin:8px 0 4px 0;font-weight:700;">No Active Reservations</h4>'
            '<p style="color:#cbd5e1;font-size:0.9rem;margin:0 0 14px 0;">'
            'No bookings yet — search parking now to reserve your spot instantly.'
            '</p></div>',
            unsafe_allow_html=True
        )
        if st.button("📍 Search Parking Now", key="btn_dash_empty_search", type="primary"):
            st.session_state["active_page"] = "search"
            st.rerun()

    # =========================================================================
    # Feature 3: Recent Bookings — 2-column layout + color-coded status badges
    # =========================================================================
    st.markdown(
        "<h3 style='color:#ffffff;font-size:1.3rem;font-weight:800;margin:25px 0 12px 0;'>"
        "📜 Recent Bookings</h3>",
        unsafe_allow_html=True
    )

    if recent_bookings:
        # Color-coded status badge helper
        def _status_badge(status: str) -> str:
            s = status.lower()
            cfg = {
                "reserved":  ("#34d399", "rgba(16,185,129,0.2)", "✅ Confirmed"),
                "active":    ("#60a5fa", "rgba(59,130,246,0.2)", "⚡ Active"),
                "completed": ("#fbbf24", "rgba(245,158,11,0.2)", "🟠 Completed"),
                "cancelled": ("#f87171", "rgba(239,68,68,0.2)", "❌ Cancelled"),
            }
            color, bg, label = cfg.get(s, ("#94a3b8", "rgba(148,163,184,0.2)", status.capitalize()))
            return (
                f'<span style="background:{bg};color:{color};border:1px solid {color}80;'
                f'padding:3px 10px;border-radius:6px;font-size:0.78rem;font-weight:700;">'
                f'{label}</span>'
            )

        # Feature 3: Render in 2-column layout, max 4 recent
        displayed = recent_bookings[:4]
        rows = [displayed[i:i+2] for i in range(0, len(displayed), 2)]
        for row in rows:
            cols = st.columns(2)
            for idx, b in enumerate(row):
                with cols[idx]:
                    b_status = str(b.get("status", "")).lower()
                    border_color = {
                        "reserved": "#34d399", "active": "#60a5fa",
                        "completed": "#fbbf24", "cancelled": "#f87171"
                    }.get(b_status, "#94a3b8")
                    badge_html = _status_badge(b_status)
                    card_html = (
                        f'<div style="background:rgba(30,41,59,0.85);'
                        f'border:1px solid rgba(148,163,184,0.25);'
                        f'border-left:4px solid {border_color};border-radius:12px;'
                        f'padding:14px 18px;margin-bottom:14px;">'
                        f'<div style="display:flex;justify-content:space-between;'
                        f'align-items:flex-start;flex-wrap:wrap;gap:8px;">'
                        f'<div>'
                        f'<span style="font-size:1rem;font-weight:800;color:#ffffff;">'
                        f'{b.get("parking_name", "Parking Facility")}</span>'
                        f'<br><span style="color:#cbd5e1;font-size:0.82rem;">'
                        f'Slot <strong style="color:#60a5fa;">{b.get("slot_number","N/A")}</strong>'
                        f' • {format_dt(b.get("start_time"))}</span>'
                        f'</div>'
                        f'<div>{badge_html}</div>'
                        f'</div></div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)
                    # Show action buttons only for active/reserved bookings in recent list
                    if b_status in ["reserved", "active"]:
                        render_booking_card(
                            b,
                            on_checkin_callback=handle_checkin,
                            on_checkout_callback=handle_checkout,
                            on_cancel_callback=handle_cancel
                        )
    else:
        # Feature 3: Empty-state for no bookings at all
        st.markdown(
            '<div style="background:rgba(30,41,59,0.5);border:1px dashed rgba(148,163,184,0.3);'
            'border-radius:12px;padding:22px;text-align:center;margin-bottom:20px;">'
            '<span style="font-size:1.8rem;">📭</span>'
            '<h4 style="color:#ffffff;margin:8px 0 4px 0;font-weight:700;">No bookings yet</h4>'
            '<p style="color:#cbd5e1;font-size:0.9rem;margin:0 0 14px 0;">'
            'You haven\'t made any bookings yet. Search for parking now to get started!'
            '</p></div>',
            unsafe_allow_html=True
        )
        if st.button("📍 Search Parking Now", key="btn_dash_no_bookings_search", type="primary"):
            st.session_state["active_page"] = "search"
            st.rerun()
