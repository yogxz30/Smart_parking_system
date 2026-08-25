import streamlit as st
from frontend.components.api_client import api


STATUS_COLORS = {
    "available": "#10b981",
    "reserved": "#f59e0b",
    "occupied": "#ef4444",
    "maintenance": "#64748b",
    "unknown": "#a78bfa",
}


def _show_result(result, success_message: str) -> None:
    if result.get("success"):
        st.success(success_message)
        st.rerun()
    else:
        st.error(result.get("error", "The operation could not be completed."))


def render_parking_management():
    """Manager/admin view for facility setup, slot operations, and active sessions."""
    user = st.session_state.get("user", {})
    token = st.session_state.get("token")
    if str(user.get("role", "")).lower() not in {"manager", "admin"}:
        st.error("⛔ Parking management is restricted to managers and administrators.")
        return

    # Header section
    header_html = (
        '<div style="margin-bottom:22px;">'
        '<div style="display:flex;align-items:center;gap:12px;">'
        '<h1 style="color:#ffffff;font-size:1.85rem;font-weight:800;margin:0;">🅿️ Parking Facility Management</h1>'
        '<span style="background:rgba(167,139,250,0.2);color:#c4b5fd;border:1px solid rgba(167,139,250,0.5);'
        'padding:3px 10px;border-radius:6px;font-size:0.75rem;font-weight:700;text-transform:uppercase;">'
        f'{str(user.get("role", "manager")).upper()} PORTAL</span>'
        '</div>'
        '<p style="color:#cbd5e1;font-size:0.95rem;margin:6px 0 0 0;">'
        'Configure parking locations, manage real-time slot statuses, and oversee active check-in sessions.'
        '</p></div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    locations_result = api.get_managed_parking_locations(token)
    if not locations_result.get("success"):
        st.error(locations_result.get("error", "Unable to load parking locations."))
        return
    locations = locations_result.get("data", [])

    location_tab, slots_tab, sessions_tab = st.tabs(["🏢 Facilities & Locations", "🅿️ Slot Operations", "🚗 Live Sessions"])

    # =========================================================================
    # TAB 1: Locations
    # =========================================================================
    with location_tab:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        with st.expander("➕ Add New Parking Location", expanded=(len(locations) == 0)):
            with st.form("add_parking_location"):
                f_c1, f_c2 = st.columns(2)
                with f_c1:
                    name = st.text_input("Facility Name", placeholder="e.g. Marina Beach Parking Hub")
                    area = st.text_input("Area / Locality", placeholder="e.g. Marina Beach, Chennai")
                    address = st.text_input("Full Address", placeholder="e.g. Kamarajar Salai, Triplicane")
                with f_c2:
                    fee = st.number_input("Hourly Fee (₹)", min_value=0.0, value=20.0, step=5.0)
                    total_slots = st.number_input("Initial Slot Capacity", min_value=0, value=10, step=1)
                    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
                    ev_available = st.checkbox("⚡ EV Charging Available", value=False)
                    accessible_available = st.checkbox("♿ Accessible Parking Available", value=False)

                st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
                if st.form_submit_button("➕ Register Location", type="primary", use_container_width=True):
                    if not name.strip() or not area.strip():
                        st.error("Name and area are required.")
                    else:
                        _show_result(api.create_parking_location(token, {
                            "parking_name": name.strip(),
                            "area": area.strip(),
                            "address": address.strip() or None,
                            "parking_fee": fee,
                            "total_slots": total_slots,
                            "ev_available": ev_available,
                            "accessible_available": accessible_available,
                        }), "✅ Parking location added successfully.")

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        if not locations:
            st.info("No parking locations registered yet. Use the form above to add one.")
        else:
            st.markdown(
                f"<p style='color:#cbd5e1;font-size:0.92rem;font-weight:600;margin-bottom:12px;'>"
                f"Registered Facilities (<strong style='color:#60a5fa;'>{len(locations)}</strong>):</p>",
                unsafe_allow_html=True
            )

        for location in locations:
            active = str(location.get("status", "")).lower() == "active"
            status_badge_icon = "🟢" if active else "🔴"
            status_text = "Active" if active else "Inactive"
            fee_val = float(location.get("parking_fee") or 0)
            slots_val = location.get("total_slots", 0)

            with st.expander(f"{status_badge_icon} {location['parking_name']} ({location.get('area')}) — {status_text} • ₹{fee_val:.2f}/hr"):
                # Summary info ribbon
                amenities = []
                if location.get("ev_available"):
                    amenities.append("⚡ EV Charging")
                if location.get("accessible_available"):
                    amenities.append("♿ Accessible")
                amenity_str = " &nbsp;|&nbsp; ".join(amenities) if amenities else "Standard"

                loc_info_html = (
                    '<div style="background:rgba(15,23,42,0.6);border:1px solid rgba(148,163,184,0.18);'
                    'border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:0.88rem;color:#cbd5e1;">'
                    f'📍 <strong>Address:</strong> {location.get("address") or location.get("area", "N/A")} &nbsp;|&nbsp; '
                    f'🚗 <strong>Total Slots:</strong> <strong style="color:#60a5fa;">{slots_val}</strong> &nbsp;|&nbsp; '
                    f'✨ <strong>Amenities:</strong> {amenity_str}'
                    '</div>'
                )
                st.markdown(loc_info_html, unsafe_allow_html=True)

                with st.form(f"edit_location_{location['parking_id']}"):
                    e_c1, e_c2 = st.columns(2)
                    with e_c1:
                        name = st.text_input("Facility Name", value=location["parking_name"])
                        area = st.text_input("Area", value=location["area"])
                    with e_c2:
                        address = st.text_input("Address", value=location.get("address") or "")
                        fee = st.number_input("Hourly Fee (₹)", min_value=0.0, value=fee_val, step=5.0)

                    if st.form_submit_button("💾 Save Details", type="primary", use_container_width=True):
                        _show_result(api.update_parking_location(token, location["parking_id"], {
                            "parking_name": name.strip(),
                            "area": area.strip(),
                            "address": address.strip() or None,
                            "parking_fee": fee,
                        }), "✅ Parking location updated.")

                toggle_btn_label = "🔴 Deactivate Facility" if active else "🟢 Activate Facility"
                if st.button(toggle_btn_label, key=f"toggle_location_{location['parking_id']}", use_container_width=True):
                    _show_result(api.set_parking_active_status(token, location["parking_id"], not active),
                                 f"Parking location {'activated' if not active else 'deactivated'}.")

    # =========================================================================
    # TAB 2: Slots
    # =========================================================================
    with slots_tab:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        if not locations:
            st.info("Add a parking location before managing slots.")
        else:
            choices = {f"{item['parking_name']} (#{item['parking_id']}) — {item.get('area', '')}": item for item in locations}
            selected = choices[st.selectbox("Select Parking Facility", list(choices))]

            with st.expander("➕ Add New Slot to Facility"):
                with st.form("add_slot"):
                    as_c1, as_c2 = st.columns(2)
                    with as_c1:
                        number = st.text_input("Slot Number / Code", placeholder="e.g. A-101")
                    with as_c2:
                        slot_type = st.selectbox("Slot Type", ["normal", "ev", "accessible"])

                    if st.form_submit_button("➕ Add Slot", type="primary", use_container_width=True):
                        if not number.strip():
                            st.error("Slot number is required.")
                        else:
                            _show_result(api.create_slot(token, selected["parking_id"], number.strip(), slot_type), "✅ Slot added successfully.")

            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            slots_result = api.get_parking_slots(selected["parking_id"])
            if slots_result.get("success"):
                slots = slots_result.get("data", [])
                if slots:
                    st.markdown(
                        f"<p style='color:#cbd5e1;font-size:0.92rem;font-weight:600;margin-bottom:12px;'>"
                        f"Live Slot Status for <strong style='color:#60a5fa;'>{selected['parking_name']}</strong> "
                        f"({len(slots)} slots):</p>",
                        unsafe_allow_html=True
                    )
                    cols = st.columns(4)
                    for index, slot in enumerate(slots):
                        slot_status = str(slot.get("status") or "unknown").lower()
                        s_type = slot.get("slot_type", "normal").lower()
                        type_icon = "⚡" if s_type == "ev" else ("♿" if s_type == "accessible" else "🚗")
                        border_color = STATUS_COLORS.get(slot_status, STATUS_COLORS["unknown"])
                        bg_color = f"{border_color}18"

                        with cols[index % 4]:
                            slot_card_html = (
                                f'<div style="background:{bg_color};border:1px solid {border_color};'
                                f'border-radius:10px;padding:12px 10px;text-align:center;margin-bottom:8px;'
                                f'box-shadow:0 2px 8px rgba(0,0,0,0.15);">'
                                f'<div style="font-size:1.15rem;font-weight:800;color:#ffffff;">'
                                f'{type_icon} {slot["slot_number"]}</div>'
                                f'<div style="color:#cbd5e1;font-size:0.75rem;font-weight:700;'
                                f'text-transform:uppercase;margin:2px 0 4px 0;">{s_type}</div>'
                                f'<span style="background:{border_color}30;color:{border_color};'
                                f'border:1px solid {border_color}70;padding:2px 8px;border-radius:5px;'
                                f'font-size:0.75rem;font-weight:700;text-transform:capitalize;">{slot_status}</span>'
                                f'</div>'
                            )
                            st.markdown(slot_card_html, unsafe_allow_html=True)
                            target = st.selectbox(
                                "Change Status",
                                ["available", "reserved", "occupied", "maintenance"],
                                index=["available", "reserved", "occupied", "maintenance"].index(slot_status) if slot_status in ["available", "reserved", "occupied", "maintenance"] else 0,
                                key=f"status_{slot['slot_id']}",
                                label_visibility="collapsed"
                            )
                            if st.button("Update Status", key=f"update_slot_{slot['slot_id']}", use_container_width=True):
                                _show_result(api.update_slot_status(token, slot["slot_id"], target), "✅ Slot status updated.")
                            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                else:
                    st.info("No slots registered for this location.")
            else:
                st.error(slots_result.get("error", "Unable to load slots."))

    # =========================================================================
    # TAB 3: Active Sessions
    # =========================================================================
    with sessions_tab:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        sessions_result = api.get_all_active_sessions(token)
        if sessions_result.get("success"):
            sessions = sessions_result.get("data", [])
            if sessions:
                st.markdown(
                    f"<p style='color:#cbd5e1;font-size:0.92rem;font-weight:600;margin-bottom:14px;'>"
                    f"Live Checked-In Vehicles across all managed facilities "
                    f"(<strong style='color:#34d399;'>{len(sessions)} active</strong>):</p>",
                    unsafe_allow_html=True
                )
                st.dataframe(sessions, use_container_width=True, hide_index=True)
            else:
                st.info("There are currently no active physical parking sessions.")
        else:
            st.error(sessions_result.get("error", "Unable to load active sessions."))
