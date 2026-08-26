import streamlit as st
from typing import Dict, Any, Optional
from frontend.components.api_client import api


def render_sidebar(current_user: Optional[Dict[str, Any]] = None):
    """
    Renders the modern sidebar with brand identity, user info,
    navigation links, system status, and logout button.
    """
    with st.sidebar:
        # Brand Logo & Title
        st.markdown(
            """
            <div style="text-align: center; padding: 10px 0 20px 0; border-bottom: 1px solid rgba(148, 163, 184, 0.15);">
                <div style="
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 52px;
                    height: 52px;
                    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                    border-radius: 14px;
                    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
                    font-size: 1.8rem;
                    margin-bottom: 8px;
                ">
                    <span class="material-symbols-rounded">local_parking</span>
                </div>
                <h2 style="color: #f8fafc; font-size: 1.25rem; font-weight: 700; margin: 0;">Smart Parking</h2>
                <p style="color: #60a5fa; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin: 2px 0 0 0;">
                    Finder & Management
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # Authenticated User Info Card
        if current_user:
            role_label = str(current_user.get("role", "user")).upper()
            role_color = "#38bdf8" if role_label == "ADMIN" else ("#a78bfa" if role_label == "MANAGER" else "#34d399")
            role_bg = "rgba(56, 189, 248, 0.18)" if role_label == "ADMIN" else ("rgba(167, 139, 250, 0.18)" if role_label == "MANAGER" else "rgba(52, 211, 153, 0.18)")
            st.markdown(
                f"""
                <div style="
                    background: rgba(30, 41, 59, 0.75);
                    border: 1px solid rgba(148, 163, 184, 0.22);
                    border-radius: 12px;
                    padding: 12px 14px;
                    margin-bottom: 20px;
                ">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="
                            width: 40px;
                            height: 40px;
                            border-radius: 50%;
                            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                            color: #ffffff;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-weight: 800;
                            font-size: 1.05rem;
                            flex-shrink: 0;
                        ">
                            {current_user.get('name', 'U')[0].upper()}
                        </div>
                        <div style="overflow: hidden; flex: 1;">
                            <div style="color: #f1f5f9; font-weight: 700; font-size: 0.92rem; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">
                                {current_user.get('name', 'User')}
                            </div>
                            <div style="display: flex; align-items: center; gap: 6px; margin-top: 2px;">
                                <span style="background: {role_bg}; color: {role_color}; border: 1px solid {role_color}50; padding: 1px 7px; border-radius: 5px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;">
                                    {role_label}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Navigation Options
        st.markdown("<p style='color: #64748b; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px;'>Navigation</p>", unsafe_allow_html=True)
        
        pages = {
            "dashboard": (":material/dashboard: User Dashboard", "dashboard"),
            "search": (":material/search: Find Parking", "search"),
            "my_bookings": (":material/calendar_month: My Bookings", "my_bookings"),
            "profile": (":material/person: User Profile", "profile")
        }
        role = str(current_user.get("role", "user")).lower() if current_user else "user"
        if role in {"manager", "admin"}:
            pages["parking_management"] = (":material/local_parking: Parking Management", "parking_management")
        if role == "admin":
            pages["admin_dashboard"] = (":material/admin_panel_settings: Admin Dashboard", "admin_dashboard")


        # Determine current active page
        current_page = st.session_state.get("active_page", "dashboard")

        # If currently inside the booking flow, show an active indicator
        if current_page == "booking":
            st.markdown(
                """
                <div style="
                    background: rgba(59, 130, 246, 0.15);
                    border: 1px solid rgba(59, 130, 246, 0.4);
                    border-radius: 8px;
                    padding: 8px 12px;
                    margin-bottom: 10px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                ">
                    <span class="material-symbols-rounded" style="font-size: 1rem;">pending_actions</span>
                    <span style="color: #93c5fd; font-weight: 600; font-size: 0.8rem;">Booking in Progress</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Render styled navigation action buttons
        for page_key, (page_label, _) in pages.items():
            is_active = (current_page == page_key)
            btn_type = "primary" if is_active else "secondary"
            if st.button(page_label, key=f"nav_btn_{page_key}", use_container_width=True, type=btn_type):
                st.session_state["active_page"] = page_key
                st.rerun()

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # System Health Status
        health = api.check_health()
        status_color = "#10b981" if health.get("success") else "#ef4444"
        status_text = "FastAPI Backend Online" if health.get("success") else "Backend Offline"
        
        st.markdown(
            f"""
            <div style="
                background: rgba(15, 23, 42, 0.5);
                border: 1px solid rgba(148, 163, 184, 0.1);
                border-radius: 8px;
                padding: 8px 12px;
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 20px;
            ">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: {status_color};"></div>
                <span style="color: #94a3b8; font-size: 0.75rem; font-weight: 500;">{status_text}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Logout Button
        if st.button(":material/logout: Log Out", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()
