import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

from frontend.components.api_client import api


def render_admin_dashboard():
    """
    Main entry point for the Admin & Dashboard module (Member 3).
    Provides role-gated monitoring, live metric cards, occupancy & status charts,
    user account management (with activation/deactivation), parking & slot monitoring,
    booking audit logs, and analytical reports.
    """
    token = st.session_state.get("token")
    user = st.session_state.get("user")

    # 1. Role-Checked Security Gate
    if not token or not user:
        st.warning("⚠️ Please log in to access the system.")
        st.session_state["active_page"] = "login"
        st.rerun()
        return

    user_role = str(user.get("role", "user")).lower()
    if user_role != "admin":
        st.error("⛔ Access Denied: Administrator role required to view this dashboard.")
        if st.button("⬅️ Return to User Dashboard", type="primary"):
            st.session_state["active_page"] = "dashboard"
            st.rerun()
        return

    # Header section with title and Live Refresh button
    col_hdr1, col_hdr2 = st.columns([3, 1])
    with col_hdr1:
        st.markdown(
            """
            <div style="margin-bottom: 20px;">
                <h1 style="color: #f8fafc; font-size: 2.2rem; font-weight: 800; margin: 0; display: flex; align-items: center; gap: 12px;">
                    <span>🛡️</span> System Admin Dashboard
                </h1>
                <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 6px;">
                    Live monitoring, user governance, slot telemetry, and system analytics.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_hdr2:
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Live Data", use_container_width=True, type="primary"):
            st.rerun()

    # Load initial live dashboard statistics
    stats_res = api.get_admin_dashboard_stats(token)
    if not stats_res.get("success"):
        st.error(f"❌ Failed to load live dashboard metrics: {stats_res.get('error')}")
        return

    stats: Dict[str, Any] = stats_res.get("data", {})

    # Create organized tabs for clean modular layout
    tab_overview, tab_users, tab_parking, tab_bookings, tab_reports = st.tabs([
        "📊 System Overview",
        "👥 User Management",
        "🅿️ Parking Monitoring",
        "📅 Booking Monitoring",
        "📈 Reports & Analytics"
    ])

    # =========================================================================
    # TAB 1: System Overview (Summary Cards & 4 Charts)
    # =========================================================================
    with tab_overview:
        st.markdown("<h3 style='color: #f1f5f9; font-weight: 700; margin-bottom: 16px;'>Live Operational Metrics</h3>", unsafe_allow_html=True)

        # 2. Summary Metric Cards (7 Required Counts)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric(
                label="👥 Total Users",
                value=stats.get("total_users", 0),
                help="Total registered accounts in the system"
            )
        with c2:
            st.metric(
                label="🅿️ Parking Locations",
                value=stats.get("total_parking_locations", 0),
                help="Total active and managed parking facilities"
            )
        with c3:
            st.metric(
                label="🚗 Total Slots",
                value=stats.get("total_slots", 0),
                help="Aggregate parking capacity across all facilities"
            )
        with c4:
            st.metric(
                label="📋 Total Bookings",
                value=stats.get("total_bookings", 0),
                help="All-time booking reservations placed"
            )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        c5, c6, c7, c8 = st.columns(4)
        with c5:
            st.metric(
                label="🟢 Available Slots",
                value=stats.get("available_slots", 0),
                delta=f"{round(stats.get('available_slots', 0) / max(stats.get('total_slots', 1), 1) * 100, 1)}% free" if stats.get("total_slots", 0) > 0 else None,
                help="Currently open slots ready for immediate booking"
            )
        with c6:
            st.metric(
                label="🔴 Occupied Slots",
                value=stats.get("occupied_slots", 0),
                delta=f"{round(stats.get('occupied_slots', 0) / max(stats.get('total_slots', 1), 1) * 100, 1)}% busy" if stats.get("total_slots", 0) > 0 else None,
                delta_color="inverse",
                help="Slots currently in active check-in session"
            )
        with c7:
            st.metric(
                label="🟡 Reserved Slots",
                value=stats.get("reserved_slots", 0),
                help="Slots reserved for upcoming confirmed bookings"
            )
        with c8:
            st.metric(
                label="🔧 Maintenance Slots",
                value=stats.get("maintenance_slots", 0),
                help="Slots offline for inspection or repair"
            )

        st.markdown("<hr style='border: 1px solid rgba(148, 163, 184, 0.15); margin: 25px 0;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #f1f5f9; font-weight: 700; margin-bottom: 16px;'>Visual Breakdowns & Telemetry</h3>", unsafe_allow_html=True)

        # 3. Charts: 4 Required Breakdowns
        # Load reports data for comprehensive charts
        rep_res = api.get_admin_reports(token)
        reports_data = rep_res.get("data", {}) if rep_res.get("success") else {}

        chart_row1_col1, chart_row1_col2 = st.columns(2)
        with chart_row1_col1:
            st.markdown("##### 📍 1. Parking-Wise Occupancy Rate (%)")
            occ_list = reports_data.get("parking_occupancy_list", [])
            if occ_list:
                df_occ = pd.DataFrame(occ_list)
                df_occ_chart = df_occ[["parking_name", "occupancy_rate"]].copy()
                df_occ_chart.columns = ["Parking Facility", "Occupancy Rate (%)"]
                df_occ_chart = df_occ_chart.set_index("Parking Facility")
                st.bar_chart(df_occ_chart, height=280)
            else:
                st.info("No parking location occupancy data available.")

        with chart_row1_col2:
            st.markdown("##### 📈 2. Bookings by Parking Location")
            loc_bookings = reports_data.get("bookings_by_parking", [])
            if loc_bookings:
                df_loc_b = pd.DataFrame(loc_bookings)
                df_loc_b_chart = df_loc_b[["parking_name", "booking_count"]].copy()
                df_loc_b_chart.columns = ["Parking Facility", "Total Bookings"]
                df_loc_b_chart = df_loc_b_chart.set_index("Parking Facility")
                st.bar_chart(df_loc_b_chart, height=280)
            else:
                st.info("No booking data per location recorded yet.")

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        chart_row2_col1, chart_row2_col2 = st.columns(2)
        with chart_row2_col1:
            st.markdown("##### 📊 3. Slot Status Breakdown")
            slot_counts = reports_data.get("slot_status_counts", {
                "Available": stats.get("available_slots", 0),
                "Occupied": stats.get("occupied_slots", 0),
                "Reserved": stats.get("reserved_slots", 0),
                "Maintenance": stats.get("maintenance_slots", 0)
            })
            df_slot_counts = pd.DataFrame(list(slot_counts.items()), columns=["Slot Status", "Count"]).set_index("Slot Status")
            st.bar_chart(df_slot_counts, height=280)

        with chart_row2_col2:
            st.markdown("##### 📋 4. Booking Status Breakdown")
            booking_counts = reports_data.get("booking_status_counts", {
                "Reserved": 0, "Active": 0, "Completed": 0, "Cancelled": 0
            })
            df_booking_counts = pd.DataFrame(list(booking_counts.items()), columns=["Booking Status", "Count"]).set_index("Booking Status")
            st.bar_chart(df_booking_counts, height=280)

    # =========================================================================
    # TAB 2: User Management (View All, Details, Activate/Deactivate)
    # =========================================================================
    with tab_users:
        st.markdown("<h3 style='color: #f1f5f9; font-weight: 700; margin-bottom: 8px;'>👥 User Management</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 0.88rem; margin-bottom: 20px;'>Inspect user records and toggle account statuses. Password hashes are strictly concealed.</p>", unsafe_allow_html=True)

        users_res = api.get_admin_users(token)
        if not users_res.get("success"):
            st.error(f"❌ Failed to fetch user records: {users_res.get('error')}")
        else:
            users_list = users_res.get("data", [])

            # Filter controls
            col_uf1, col_uf2, col_uf3 = st.columns([2, 1, 1])
            with col_uf1:
                search_user_query = st.text_input("🔍 Search Users (Name or Email)", placeholder="Type name or email...").strip().lower()
            with col_uf2:
                role_filter = st.selectbox("Filter Role", ["All Roles", "user", "manager", "admin"])
            with col_uf3:
                status_filter_user = st.selectbox("Filter Status", ["All Statuses", "active", "inactive"])

            filtered_users = []
            for u in users_list:
                name_match = (search_user_query in u.get("name", "").lower()) or (search_user_query in u.get("email", "").lower())
                role_match = (role_filter == "All Roles") or (u.get("role") == role_filter)
                stat_match = (status_filter_user == "All Statuses") or (u.get("status") == status_filter_user)
                if name_match and role_match and stat_match:
                    filtered_users.append(u)

            st.caption(f"Showing {len(filtered_users)} of {len(users_list)} registered users")

            if filtered_users:
                # Format users display table
                table_rows = []
                for u in filtered_users:
                    created_str = u.get("created_at", "")
                    if created_str:
                        try:
                            created_str = datetime.fromisoformat(created_str.replace("Z", "")).strftime("%Y-%m-%d %H:%M")
                        except Exception:
                            pass

                    table_rows.append({
                        "User ID": u.get("user_id"),
                        "Full Name": u.get("name"),
                        "Email Address": u.get("email"),
                        "Phone": u.get("phone") or "—",
                        "Role": u.get("role", "").upper(),
                        "Account Status": "🟢 Active" if u.get("status") == "active" else "🔴 Inactive",
                        "Joined Date": created_str
                    })

                df_users_display = pd.DataFrame(table_rows)
                st.dataframe(df_users_display, use_container_width=True, hide_index=True)

                st.markdown("<hr style='border: 1px solid rgba(148, 163, 184, 0.15); margin: 20px 0;'>", unsafe_allow_html=True)
                st.markdown("#### ⚡ Manage User Account Status")

                user_options = {f"ID #{u['user_id']} — {u['name']} ({u['email']}) [{u['status'].upper()}]": u for u in filtered_users}
                selected_user_label = st.selectbox("Select User Account to Inspect or Update", list(user_options.keys()))
                target_user = user_options[selected_user_label]

                col_ud1, col_ud2 = st.columns([2, 1])
                with col_ud1:
                    st.markdown(
                        f"""
                        <div style="
                            background: rgba(30, 41, 59, 0.7);
                            border: 1px solid rgba(148, 163, 184, 0.2);
                            border-radius: 10px;
                            padding: 16px 20px;
                            line-height: 1.6;
                        ">
                            <h4 style="color: #60a5fa; margin: 0 0 10px 0;">👤 User Profile Details</h4>
                            <div style="color: #f1f5f9; font-size: 0.95rem;">
                                <strong>User ID:</strong> #{target_user.get('user_id')}<br>
                                <strong>Name:</strong> {target_user.get('name')}<br>
                                <strong>Email:</strong> {target_user.get('email')}<br>
                                <strong>Phone:</strong> {target_user.get('phone') or 'Not provided'}<br>
                                <strong>Role:</strong> <span style="background: rgba(99, 102, 241, 0.3); padding: 2px 8px; border-radius: 4px; font-size: 0.85rem;">{target_user.get('role', '').upper()}</span><br>
                                <strong>Current Status:</strong> 
                                <span style="color: {'#34d399' if target_user.get('status') == 'active' else '#f87171'}; font-weight: 700;">
                                    {target_user.get('status', '').upper()}
                                </span><br>
                                <strong>Created At:</strong> {target_user.get('created_at', '')}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col_ud2:
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    current_stat = target_user.get("status", "active")
                    is_self = (user.get("user_id") == target_user.get("user_id"))

                    if current_stat == "active":
                        st.markdown("<p style='color: #94a3b8; font-size: 0.85rem;'>This account is currently active and permitted to login.</p>", unsafe_allow_html=True)
                        if is_self:
                            st.info("🔒 You cannot deactivate your own admin account.")
                        else:
                            if st.button("🚫 Deactivate Account", type="secondary", use_container_width=True):
                                update_res = api.update_admin_user_status(token, target_user["user_id"], "inactive")
                                if update_res.get("success"):
                                    st.success(f"User #{target_user['user_id']} has been deactivated successfully.")
                                    st.rerun()
                                else:
                                    st.error(f"Error deactivating user: {update_res.get('error')}")
                    else:
                        st.markdown("<p style='color: #f87171; font-size: 0.85rem;'>This account is currently inactive (login blocked).</p>", unsafe_allow_html=True)
                        if st.button("✅ Activate Account", type="primary", use_container_width=True):
                            update_res = api.update_admin_user_status(token, target_user["user_id"], "active")
                            if update_res.get("success"):
                                st.success(f"User #{target_user['user_id']} has been activated successfully.")
                                st.rerun()
                            else:
                                st.error(f"Error activating user: {update_res.get('error')}")
            else:
                st.info("No users found matching your search filters.")

    # =========================================================================
    # TAB 3: Parking Monitoring (Read-Only)
    # =========================================================================
    with tab_parking:
        st.markdown("<h3 style='color: #f1f5f9; font-weight: 700; margin-bottom: 8px;'>🅿️ Parking Location Telemetry & Monitoring</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 0.88rem; margin-bottom: 20px;'>Live status and slot capacity distribution across all facilities (Read-Only).</p>", unsafe_allow_html=True)

        parking_res = api.get_admin_parking_summary(token)
        if not parking_res.get("success"):
            st.error(f"❌ Failed to retrieve parking summaries: {parking_res.get('error')}")
        else:
            parking_list = parking_res.get("data", [])

            # Filter controls
            col_pf1, col_pf2 = st.columns([2, 1])
            with col_pf1:
                areas = sorted(list({p.get("area") for p in parking_list if p.get("area")}))
                selected_area = st.selectbox("Filter Area", ["All Areas"] + areas)
            with col_pf2:
                selected_p_status = st.selectbox("Facility Status", ["All Statuses", "active", "inactive"])

            filtered_parking = [
                p for p in parking_list
                if (selected_area == "All Areas" or p.get("area") == selected_area)
                and (selected_p_status == "All Statuses" or p.get("status") == selected_p_status)
            ]

            st.caption(f"Displaying {len(filtered_parking)} of {len(parking_list)} parking locations")

            # Main parking summary table
            p_table_rows = []
            for p in filtered_parking:
                p_table_rows.append({
                    "ID": p.get("parking_id"),
                    "Facility Name": p.get("parking_name"),
                    "Area": p.get("area"),
                    "Total Slots": p.get("total_slots", 0),
                    "🟢 Available": p.get("available_slots", 0),
                    "🔴 Occupied": p.get("occupied_slots", 0),
                    "🟡 Reserved": p.get("reserved_slots", 0),
                    "🔧 Maint.": p.get("maintenance_slots", 0),
                    "Occupancy": f"{p.get('occupancy_rate', 0)}%",
                    "Total Bookings": p.get("total_bookings", 0),
                    "Hourly Fee": f"₹{p.get('parking_fee', 0.0):.2f}",
                    "Status": "🟢 Active" if p.get("status") == "active" else "🔴 Inactive"
                })

            if p_table_rows:
                df_parking_display = pd.DataFrame(p_table_rows)
                st.dataframe(df_parking_display, use_container_width=True, hide_index=True)

                st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                st.markdown("#### 🔍 Facility Details Inspector")

                p_options = {f"#{p['parking_id']} — {p['parking_name']} ({p['area']})": p for p in filtered_parking}
                chosen_p_label = st.selectbox("Select Facility for Deep Inspection", list(p_options.keys()))
                chosen_p = p_options[chosen_p_label]

                col_pi1, col_pi2, col_pi3 = st.columns([1.5, 1.2, 1.3])
                with col_pi1:
                    st.markdown(
                        f"""
                        <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 10px; padding: 14px 18px;">
                            <h5 style="color: #60a5fa; margin: 0 0 8px 0;">📍 Location Information</h5>
                            <p style="color: #f1f5f9; font-size: 0.88rem; margin: 0; line-height: 1.6;">
                                <strong>Facility:</strong> {chosen_p.get('parking_name')}<br>
                                <strong>Area:</strong> {chosen_p.get('area')}<br>
                                <strong>Address:</strong> {chosen_p.get('address') or 'N/A'}<br>
                                <strong>Hourly Rate:</strong> ₹{chosen_p.get('parking_fee', 0):.2f}/hr<br>
                                <strong>Hours:</strong> {chosen_p.get('opening_time') or '24/7'} – {chosen_p.get('closing_time') or '24/7'}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col_pi2:
                    st.markdown(
                        f"""
                        <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 10px; padding: 14px 18px;">
                            <h5 style="color: #34d399; margin: 0 0 8px 0;">⚡ Amenities & Status</h5>
                            <p style="color: #f1f5f9; font-size: 0.88rem; margin: 0; line-height: 1.6;">
                                <strong>EV Charging:</strong> {'⚡ Yes' if chosen_p.get('ev_available') else '❌ No'}<br>
                                <strong>Accessible Parking:</strong> {'♿ Yes' if chosen_p.get('accessible_available') else '❌ No'}<br>
                                <strong>Facility Status:</strong> <span style="color: {'#34d399' if chosen_p.get('status') == 'active' else '#f87171'}; font-weight: 700;">{chosen_p.get('status', '').upper()}</span><br>
                                <strong>Total Lifetime Bookings:</strong> {chosen_p.get('total_bookings', 0)}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col_pi3:
                    st.markdown(
                        f"""
                        <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 10px; padding: 14px 18px;">
                            <h5 style="color: #fbbf24; margin: 0 0 8px 0;">📊 Slot Breakdown</h5>
                            <p style="color: #f1f5f9; font-size: 0.88rem; margin: 0; line-height: 1.6;">
                                <strong>Total Capacity:</strong> {chosen_p.get('total_slots', 0)} slots<br>
                                <strong>🟢 Available:</strong> {chosen_p.get('available_slots', 0)}<br>
                                <strong>🔴 Occupied:</strong> {chosen_p.get('occupied_slots', 0)}<br>
                                <strong>🟡 Reserved:</strong> {chosen_p.get('reserved_slots', 0)}<br>
                                <strong>Occupancy Rate:</strong> {chosen_p.get('occupancy_rate', 0)}%
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No parking locations found for the selected filter.")

    # =========================================================================
    # TAB 4: Booking Monitoring (Read-Only)
    # =========================================================================
    with tab_bookings:
        st.markdown("<h3 style='color: #f1f5f9; font-weight: 700; margin-bottom: 8px;'>📅 Booking Audit & Monitoring</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 0.88rem; margin-bottom: 20px;'>Search and filter live reservations and parking sessions (Read-Only).</p>", unsafe_allow_html=True)

        # Filters: Search by booking ID, filter by parking location, status
        col_bf1, col_bf2, col_bf3 = st.columns([1, 2, 1])
        with col_bf1:
            search_bid = st.text_input("🔍 Search Booking ID", placeholder="e.g. 1").strip()
            search_bid_int = int(search_bid) if search_bid.isdigit() else None
        with col_bf2:
            # Fetch locations for dropdown
            p_res = api.get_admin_parking_summary(token)
            p_list = p_res.get("data", []) if p_res.get("success") else []
            p_filter_opts = {"All Locations": None}
            for p in p_list:
                p_filter_opts[f"#{p['parking_id']} — {p['parking_name']} ({p['area']})"] = p["parking_id"]
            selected_p_label_filter = st.selectbox("Filter Parking Location", list(p_filter_opts.keys()))
            chosen_pid = p_filter_opts[selected_p_label_filter]
        with col_bf3:
            booking_stat_filter = st.selectbox("Filter Status", ["All", "reserved", "active", "completed", "cancelled"])

        # Fetch bookings with filters
        bookings_res = api.get_admin_booking_summary(
            token,
            parking_id=chosen_pid,
            status_filter=booking_stat_filter,
            search_id=search_bid_int
        )

        if not bookings_res.get("success"):
            st.error(f"❌ Failed to load bookings: {bookings_res.get('error')}")
        else:
            b_data = bookings_res.get("data", {})
            bookings_list = b_data.get("bookings", [])

            # Booking Status KPI Ribbon
            st.markdown(
                f"""
                <div style="
                    display: flex;
                    gap: 15px;
                    flex-wrap: wrap;
                    margin-bottom: 15px;
                ">
                    <span style="background: rgba(59, 130, 246, 0.2); border: 1px solid rgba(59, 130, 246, 0.4); padding: 4px 12px; border-radius: 6px; font-size: 0.82rem; color: #93c5fd;">
                        Total: <strong>{b_data.get('total_bookings', 0)}</strong>
                    </span>
                    <span style="background: rgba(234, 179, 8, 0.2); border: 1px solid rgba(234, 179, 8, 0.4); padding: 4px 12px; border-radius: 6px; font-size: 0.82rem; color: #fde047;">
                        🟡 Reserved: <strong>{b_data.get('reserved_count', 0)}</strong>
                    </span>
                    <span style="background: rgba(59, 130, 246, 0.2); border: 1px solid rgba(59, 130, 246, 0.4); padding: 4px 12px; border-radius: 6px; font-size: 0.82rem; color: #60a5fa;">
                        🔵 Active: <strong>{b_data.get('active_count', 0)}</strong>
                    </span>
                    <span style="background: rgba(34, 197, 94, 0.2); border: 1px solid rgba(34, 197, 94, 0.4); padding: 4px 12px; border-radius: 6px; font-size: 0.82rem; color: #86efac;">
                        🟢 Completed: <strong>{b_data.get('completed_count', 0)}</strong>
                    </span>
                    <span style="background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.4); padding: 4px 12px; border-radius: 6px; font-size: 0.82rem; color: #fca5a5;">
                        🔴 Cancelled: <strong>{b_data.get('cancelled_count', 0)}</strong>
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.caption(f"Showing {len(bookings_list)} matching booking records")

            if bookings_list:
                b_table_rows = []
                for b in bookings_list:
                    start_str = b.get("start_time", "")
                    end_str = b.get("end_time", "")
                    created_str = b.get("created_at", "")
                    try:
                        start_str = datetime.fromisoformat(start_str.replace("Z", "")).strftime("%Y-%m-%d %H:%M")
                        end_str = datetime.fromisoformat(end_str.replace("Z", "")).strftime("%H:%M")
                        created_str = datetime.fromisoformat(created_str.replace("Z", "")).strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        pass

                    status_badge = {
                        "reserved": "🟡 Reserved",
                        "active": "🔵 Active",
                        "completed": "🟢 Completed",
                        "cancelled": "🔴 Cancelled"
                    }.get(b.get("status", "").lower(), b.get("status", "").upper())

                    b_table_rows.append({
                        "Booking ID": f"#{b.get('booking_id')}",
                        "User": f"{b.get('user_name')} (#{b.get('user_id')})",
                        "Email": b.get("user_email"),
                        "Parking Facility": f"{b.get('parking_name')} ({b.get('area')})",
                        "Slot": f"{b.get('slot_number')} ({b.get('slot_type')})",
                        "Date": str(b.get("booking_date")),
                        "Schedule": f"{start_str} – {end_str}",
                        "Status": status_badge,
                        "Booked On": created_str
                    })

                df_b_display = pd.DataFrame(b_table_rows)
                st.dataframe(df_b_display, use_container_width=True, hide_index=True)
            else:
                st.info("No bookings found matching your search and filter criteria.")

    # =========================================================================
    # TAB 5: Reports & Analytics
    # =========================================================================
    with tab_reports:
        st.markdown("<h3 style='color: #f1f5f9; font-weight: 700; margin-bottom: 8px;'>📈 Analytical Reports & Utilization Intelligence</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 0.88rem; margin-bottom: 20px;'>Live aggregated insights, facility demand ranking, and system-wide capacity metrics.</p>", unsafe_allow_html=True)

        rep_res = api.get_admin_reports(token)
        if not rep_res.get("success"):
            st.error(f"❌ Failed to compute reports: {rep_res.get('error')}")
        else:
            r_data = rep_res.get("data", {})

            # Executive High-Level KPI Summary
            rk1, rk2, rk3, rk4 = st.columns(4)
            with rk1:
                st.metric("Total All-Time Bookings", r_data.get("total_bookings", 0))
            with rk2:
                st.metric("Overall Occupancy Rate", f"{r_data.get('overall_occupancy_rate', 0)}%")
            with rk3:
                st.metric("Total System Slots", r_data.get("total_slots", 0))
            with rk4:
                st.metric("Available Slots Free", r_data.get("available_slots", 0))

            st.markdown("<hr style='border: 1px solid rgba(148, 163, 184, 0.15); margin: 20px 0;'>", unsafe_allow_html=True)

            # Report 1: Most-Used Parking Facilities Leaderboard
            col_rep1, col_rep2 = st.columns([1.2, 1])
            with col_rep1:
                st.markdown("#### 🏆 Most-Used Parking Locations (By Total Bookings)")
                most_used = r_data.get("most_used_parking", [])
                if most_used:
                    mu_rows = []
                    for rank, item in enumerate(most_used, start=1):
                        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
                        mu_rows.append({
                            "Rank": medal,
                            "Facility Name": item.get("parking_name"),
                            "Area": item.get("area"),
                            "Booking Count": item.get("booking_count", 0)
                        })
                    df_mu = pd.DataFrame(mu_rows)
                    st.dataframe(df_mu, use_container_width=True, hide_index=True)
                else:
                    st.info("No bookings recorded yet to determine top facilities.")

            with col_rep2:
                st.markdown("#### 📊 System Slot Utilization Breakdown")
                slot_breakdown = r_data.get("slot_status_counts", {})
                if slot_breakdown:
                    sb_rows = [
                        {"Status": "🟢 Available (Free)", "Slots": slot_breakdown.get("Available", 0)},
                        {"Status": "🔴 Occupied (Active Check-In)", "Slots": slot_breakdown.get("Occupied", 0)},
                        {"Status": "🟡 Reserved (Pre-Booked)", "Slots": slot_breakdown.get("Reserved", 0)},
                        {"Status": "🔧 Maintenance", "Slots": slot_breakdown.get("Maintenance", 0)}
                    ]
                    df_sb = pd.DataFrame(sb_rows)
                    st.dataframe(df_sb, use_container_width=True, hide_index=True)

            st.markdown("<hr style='border: 1px solid rgba(148, 163, 184, 0.15); margin: 20px 0;'>", unsafe_allow_html=True)

            # Report 2: Full Per-Location Occupancy & Capacity Ledger
            st.markdown("#### 📍 Facility-by-Facility Occupancy & Slot Availability Ledger")
            p_occ_list = r_data.get("parking_occupancy_list", [])
            if p_occ_list:
                occ_ledger_rows = []
                for p in p_occ_list:
                    occ_ledger_rows.append({
                        "ID": p.get("parking_id"),
                        "Facility Name": p.get("parking_name"),
                        "Area": p.get("area"),
                        "Total Slots": p.get("total_slots", 0),
                        "🟢 Available": p.get("available_slots", 0),
                        "🔴 Occupied": p.get("occupied_slots", 0),
                        "🟡 Reserved": p.get("reserved_slots", 0),
                        "Occupancy Rate": f"{p.get('occupancy_rate', 0)}%"
                    })
                df_occ_ledger = pd.DataFrame(occ_ledger_rows)
                st.dataframe(df_occ_ledger, use_container_width=True, hide_index=True)
            else:
                st.info("No facility occupancy data found.")
