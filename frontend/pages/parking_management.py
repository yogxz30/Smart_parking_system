import streamlit as st

from frontend.components.api_client import api


STATUS_COLORS = {
    "available": "#10b981", "reserved": "#f59e0b", "occupied": "#ef4444",
    "maintenance": "#64748b", "unknown": "#a78bfa",
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
        st.error("Parking management is restricted to managers and administrators.")
        return

    st.title("🅿️ Parking Management")
    st.caption("Manage parking locations, live slot states, and active sessions.")
    locations_result = api.get_managed_parking_locations(token)
    if not locations_result.get("success"):
        st.error(locations_result.get("error", "Unable to load parking locations."))
        return
    locations = locations_result.get("data", [])

    location_tab, slots_tab, sessions_tab = st.tabs(["Locations", "Slots", "Active Sessions"])
    with location_tab:
        with st.expander("Add parking location"):
            with st.form("add_parking_location"):
                name = st.text_input("Name")
                area = st.text_input("Area")
                address = st.text_input("Address")
                fee = st.number_input("Hourly fee", min_value=0.0, value=0.0)
                total_slots = st.number_input("Initial total slots", min_value=0, value=0, step=1)
                ev_available = st.checkbox("EV charging available")
                accessible_available = st.checkbox("Accessible parking available")
                if st.form_submit_button("Add location"):
                    if not name.strip() or not area.strip():
                        st.error("Name and area are required.")
                    else:
                        _show_result(api.create_parking_location(token, {
                            "parking_name": name.strip(), "area": area.strip(), "address": address.strip() or None,
                            "parking_fee": fee, "total_slots": total_slots, "ev_available": ev_available,
                            "accessible_available": accessible_available,
                        }), "Parking location added.")

        if not locations:
            st.info("No parking locations have been added.")
        for location in locations:
            active = str(location.get("status", "")).lower() == "active"
            label = "Active" if active else "Inactive"
            with st.expander(f"{location['parking_name']} — {label}"):
                with st.form(f"edit_location_{location['parking_id']}"):
                    name = st.text_input("Name", value=location["parking_name"])
                    area = st.text_input("Area", value=location["area"])
                    address = st.text_input("Address", value=location.get("address") or "")
                    fee = st.number_input("Hourly fee", min_value=0.0, value=float(location.get("parking_fee") or 0))
                    if st.form_submit_button("Save details"):
                        _show_result(api.update_parking_location(token, location["parking_id"], {
                            "parking_name": name.strip(), "area": area.strip(), "address": address.strip() or None,
                            "parking_fee": fee,
                        }), "Parking location updated.")
                if st.button("Deactivate" if active else "Activate", key=f"toggle_location_{location['parking_id']}"):
                    _show_result(api.set_parking_active_status(token, location["parking_id"], not active),
                                 f"Parking location {'activated' if not active else 'deactivated'}.")

    with slots_tab:
        if not locations:
            st.info("Add a parking location before managing slots.")
        else:
            choices = {f"{item['parking_name']} (#{item['parking_id']})": item for item in locations}
            selected = choices[st.selectbox("Parking location", list(choices))]
            with st.form("add_slot"):
                number = st.text_input("Slot number")
                slot_type = st.selectbox("Slot type", ["normal", "ev", "accessible"])
                if st.form_submit_button("Add slot"):
                    if not number.strip():
                        st.error("Slot number is required.")
                    else:
                        _show_result(api.create_slot(token, selected["parking_id"], number.strip(), slot_type), "Slot added.")
            slots_result = api.get_parking_slots(selected["parking_id"])
            if slots_result.get("success"):
                slots = slots_result.get("data", [])
                if slots:
                    cols = st.columns(4)
                    for index, slot in enumerate(slots):
                        slot_status = str(slot.get("status") or "unknown").lower()
                        with cols[index % 4]:
                            st.markdown(
                                f"<div style='border:2px solid {STATUS_COLORS.get(slot_status, STATUS_COLORS['unknown'])};"
                                f"border-radius:8px;padding:10px;margin:4px 0;text-align:center;'>"
                                f"<b>{slot['slot_number']}</b><br><small>{slot.get('slot_type', 'normal')} · {slot_status}</small></div>",
                                unsafe_allow_html=True,
                            )
                            target = st.selectbox("Set status", ["available", "reserved", "occupied", "maintenance"],
                                                  key=f"status_{slot['slot_id']}")
                            if st.button("Update", key=f"update_slot_{slot['slot_id']}"):
                                _show_result(api.update_slot_status(token, slot["slot_id"], target), "Slot status updated.")
                else:
                    st.info("No slots registered for this location.")
            else:
                st.error(slots_result.get("error", "Unable to load slots."))

    with sessions_tab:
        sessions_result = api.get_all_active_sessions(token)
        if sessions_result.get("success"):
            sessions = sessions_result.get("data", [])
            if sessions:
                st.dataframe(sessions, use_container_width=True, hide_index=True)
            else:
                st.info("There are no active parking sessions.")
        else:
            st.error(sessions_result.get("error", "Unable to load active sessions."))
