import streamlit as st
import textwrap
from typing import Dict, Any, List, Set
from frontend.components.api_client import api
from frontend.components.cards import render_parking_summary_card, get_slot_status_badge


def render_parking_search():
    """
    Renders the Parking Search and Real-Time Slot Explorer page with
    area proximity sorting, amenity filters, and interactive slot selection.
    Feature 4: Favorite/saved parking (⭐ toggle) + My Favorites section.
    Feature 5: EV/accessible filters — already implemented, preserved as-is.
    Feature 6: Sort dropdown (Nearest first / Cheapest first).
    """
    token = st.session_state.get("token")

    st.markdown(
        '<div style="margin-bottom:20px;">'
        '<h1 style="color:#ffffff;font-size:1.8rem;font-weight:800;margin:0;">🔍 Find Parking Locations</h1>'
        '<p style="color:#cbd5e1;font-size:0.95rem;margin:4px 0 0 0;">'
        'Select your destination area in Chennai to find nearby parking facilities sorted by proximity.'
        '</p></div>',
        unsafe_allow_html=True
    )

    # =========================================================================
    # Feature 4: Load favorites for logged-in users (used for star toggle)
    # =========================================================================
    favorite_parking_ids: Set[int] = set()
    if token:
        fav_res = api.get_favorites(token)
        if fav_res.get("success"):
            for f in fav_res.get("data", []):
                favorite_parking_ids.add(f.get("parking_id"))

    # =========================================================================
    # Feature 4: My Favorites Section
    # =========================================================================
    if token and favorite_parking_ids:
        with st.expander(f"⭐ My Favorites ({len(favorite_parking_ids)})", expanded=False):
            fav_list_res = api.get_favorites(token)
            if fav_list_res.get("success"):
                fav_items = fav_list_res.get("data", [])
                if fav_items:
                    fav_cols = st.columns(min(len(fav_items), 3))
                    for idx, fav in enumerate(fav_items):
                        with fav_cols[idx % 3]:
                            fav_html = (
                                '<div style="background:rgba(245,158,11,0.12);'
                                'border:1px solid rgba(245,158,11,0.4);border-radius:10px;'
                                'padding:12px;margin-bottom:10px;text-align:center;">'
                                '<div style="font-size:1.2rem;">⭐</div>'
                                '<strong style="color:#ffffff;font-size:0.9rem;">{name}</strong>'
                                '<div style="color:#cbd5e1;font-size:0.78rem;">{area}</div>'
                                '<div style="color:#fbbf24;font-size:0.85rem;font-weight:700;">'
                                '₹{fee:.2f}/hr</div>'
                                '</div>'
                            ).format(
                                name=fav.get("parking_name", ""),
                                area=fav.get("area", ""),
                                fee=float(fav.get("parking_fee") or 0)
                            )
                            st.markdown(fav_html, unsafe_allow_html=True)
                            if st.button(
                                "Remove ⭐",
                                key=f"fav_remove_top_{fav.get('parking_id')}",
                                use_container_width=True
                            ):
                                res = api.remove_favorite(token, fav.get("parking_id"))
                                if res.get("success"):
                                    st.success("Removed from favorites.")
                                    st.rerun()
                                else:
                                    st.error(res.get("error", "Failed to remove."))
                else:
                    st.info("No favorites saved yet. Star a parking location below to save it!")

    # =========================================================================
    # 1. Fetch available Chennai areas
    # =========================================================================
    areas_result = api.get_areas()
    supported_areas = ["All Areas"] + (areas_result.get("data", []) if areas_result.get("success") else [])

    # =========================================================================
    # Search, Filter & Sort Controls
    # =========================================================================
    with st.container():
        f_col1, f_col2, f_col3, f_col4 = st.columns([2.5, 1, 1, 1.5])

        with f_col1:
            selected_area = st.selectbox(
                "📍 Destination Area / Locality",
                options=supported_areas,
                index=1 if len(supported_areas) > 1 else 0,
                help="Choose an area to calculate distances to nearby parking lots",
                key="search_area_select"
            )

        with f_col2:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            ev_filter = st.checkbox("⚡ EV Charging", value=False, key="filter_ev")

        with f_col3:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            acc_filter = st.checkbox("♿ Accessible", value=False, key="filter_acc")

        with f_col4:
            # Feature 6: Sort dropdown
            sort_options = {
                "📍 Nearest first": "nearest",
                "💰 Cheapest first": "fee_asc",
                "💸 Most expensive first": "fee_desc",
            }
            sort_label = st.selectbox(
                "Sort by",
                options=list(sort_options.keys()),
                index=0,
                key="search_sort_by"
            )
            sort_by_value = sort_options[sort_label]
            # "nearest" maps to None (default API behavior)
            api_sort_by = None if sort_by_value == "nearest" else sort_by_value

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # 2. Fetch parking locations matching filters + sort
    # =========================================================================
    search_area = None if selected_area == "All Areas" else selected_area
    with st.spinner("Searching nearby parking locations..."):
        search_res = api.search_parking(
            area=search_area,
            ev_only=ev_filter,
            accessible_only=acc_filter,
            sort_by=api_sort_by
        )

    if not search_res.get("success"):
        st.error(f"Failed to fetch parking locations: {search_res.get('error')}")
        return

    parking_list = search_res.get("data", [])

    if not parking_list:
        st.warning("⚠️ No parking locations found matching your selected criteria. Try selecting 'All Areas' or clearing filters.")
        return

    st.markdown(
        f"<p style='color:#cbd5e1;font-size:0.95rem;'>Found "
        f"<strong style='color:#60a5fa;'>{len(parking_list)}</strong> parking facilities in/near "
        f"<strong style='color:#ffffff;'>{selected_area}</strong>:</p>",
        unsafe_allow_html=True
    )

    # =========================================================================
    # 3. Render Parking Facilities with Slot Exploration + Favorite toggle
    # =========================================================================
    for loc in parking_list:
        p_id = loc.get("parking_id")
        is_fav = p_id in favorite_parking_ids

        with st.expander(
            f"{'⭐' if is_fav else '🏢'} {loc.get('parking_name')}  —  "
            f"₹{loc.get('parking_fee', 0):.2f}/hr  •  {loc.get('available_slots', 0)} Available",
            expanded=(len(parking_list) == 1)
        ):
            # Feature 4: Favorite toggle button at top of expander
            if token:
                fav_col, info_col = st.columns([1, 4])
                with fav_col:
                    if is_fav:
                        if st.button(
                            "⭐ Saved",
                            key=f"fav_btn_{p_id}",
                            help="Click to remove from favorites",
                            use_container_width=True
                        ):
                            res = api.remove_favorite(token, p_id)
                            if res.get("success"):
                                st.success(f"Removed {loc.get('parking_name')} from favorites.")
                                st.rerun()
                            else:
                                st.error(res.get("error", "Failed to remove."))
                    else:
                        if st.button(
                            "☆ Save",
                            key=f"fav_btn_{p_id}",
                            help="Click to add to favorites",
                            use_container_width=True
                        ):
                            res = api.add_favorite(token, p_id)
                            if res.get("success"):
                                st.success(f"⭐ {loc.get('parking_name')} added to favorites!")
                                st.rerun()
                            else:
                                # Handle "already favorited" gracefully
                                err = res.get("error", "")
                                if "already" in str(err).lower():
                                    st.info("Already in favorites.")
                                else:
                                    st.error(err)

            render_parking_summary_card(loc)

            # Operating hours and details
            hours_html = (
                '<div style="color:#cbd5e1;font-size:0.88rem;margin-bottom:14px;'
                'background:rgba(15,23,42,0.5);padding:8px 14px;border-radius:8px;'
                'border:1px solid rgba(148,163,184,0.15);">'
                '⏰ <strong>Operating Hours:</strong> '
                f'{loc.get("opening_time", "06:00:00")} - {loc.get("closing_time", "23:00:00")}'
                ' &nbsp;|&nbsp; '
                '🏷️ <strong>Status:</strong> '
                '<span style="color:#34d399;font-weight:700;">Active</span>'
                '</div>'
            )
            st.markdown(hours_html, unsafe_allow_html=True)

            # Slot Grid Viewer
            st.markdown(
                "<h4 style='color:#ffffff;font-size:1.05rem;font-weight:700;margin:12px 0 10px 0;'>"
                "🅿️ Parking Slot Availability Grid</h4>",
                unsafe_allow_html=True
            )

            slots_res = api.get_parking_slots(p_id)
            if slots_res.get("success"):
                slots = slots_res.get("data", [])

                # Render Slot Cards Grid
                if slots:
                    cols_per_row = 4
                    slot_rows = [slots[i:i + cols_per_row] for i in range(0, len(slots), cols_per_row)]

                    for r_idx, row in enumerate(slot_rows):
                        cols = st.columns(cols_per_row)
                        for idx, slot in enumerate(row):
                            with cols[idx]:
                                s_id = slot.get("slot_id")
                                s_num = slot.get("slot_number")
                                s_type = slot.get("slot_type", "normal").lower()
                                s_status = slot.get("status", "available").lower()

                                type_icon = "⚡" if s_type == "ev" else ("♿" if s_type == "accessible" else "🚗")
                                is_available = (s_status == "available")

                                # Slot card styling
                                bg_color = (
                                    "rgba(16,185,129,0.18)" if is_available
                                    else ("rgba(245,158,11,0.18)" if s_status == "reserved"
                                          else ("rgba(239,68,68,0.18)" if s_status == "occupied"
                                                else "rgba(100,116,139,0.18)"))
                                )
                                border_color = (
                                    "#10b981" if is_available
                                    else ("#f59e0b" if s_status == "reserved"
                                          else ("#ef4444" if s_status == "occupied"
                                                else "#64748b"))
                                )

                                slot_card_html = (
                                    '<div style="background:{bg};border:1px solid {bc};'
                                    'border-radius:10px;padding:12px 10px;text-align:center;margin-bottom:8px;">'
                                    '<div style="font-size:1.15rem;font-weight:800;color:#ffffff;">'
                                    '{icon} {num}</div>'
                                    '<div style="color:#cbd5e1;font-size:0.75rem;font-weight:700;'
                                    'text-transform:uppercase;margin:3px 0 6px 0;">{stype}</div>'
                                    '<div style="margin-top:4px;">{badge}</div>'
                                    '</div>'
                                ).format(
                                    bg=bg_color, bc=border_color,
                                    icon=type_icon, num=s_num, stype=s_type,
                                    badge=get_slot_status_badge(s_status)
                                )
                                st.markdown(slot_card_html, unsafe_allow_html=True)

                                # Book button for available slots
                                if is_available:
                                    if st.button(f"Book {s_num}", key=f"btn_book_p{p_id}_s{s_id}", use_container_width=True, type="primary"):
                                        st.session_state["selected_parking"] = loc
                                        st.session_state["selected_slot"] = slot
                                        st.session_state["active_page"] = "booking"
                                        st.rerun()
                                else:
                                    st.button(f"Unavailable", key=f"btn_unavail_p{p_id}_s{s_id}", use_container_width=True, disabled=True)
                else:
                    st.info("No slots registered for this facility.")
            else:
                st.error("Failed to load slot status.")
