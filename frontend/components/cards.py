import streamlit as st
from typing import Dict, Any


def render_kpi_card(title: str, value: str | int, subtitle: str, icon: str, theme: str = "blue"):
    """
    Renders an elegant KPI card with gradient accent, modern typography, and clear visual hierarchy.
    Themes: 'blue', 'green', 'amber', 'purple'
    """
    color_map = {
        "blue": {
            "border": "#3b82f6",
            "bg_gradient": "linear-gradient(135deg, rgba(59, 130, 246, 0.18) 0%, rgba(30, 58, 138, 0.12) 100%)",
            "icon_bg": "rgba(59, 130, 246, 0.25)",
            "text_accent": "#93c5fd"
        },
        "green": {
            "border": "#10b981",
            "bg_gradient": "linear-gradient(135deg, rgba(16, 185, 129, 0.18) 0%, rgba(6, 78, 59, 0.12) 100%)",
            "icon_bg": "rgba(16, 185, 129, 0.25)",
            "text_accent": "#6ee7b7"
        },
        "amber": {
            "border": "#f59e0b",
            "bg_gradient": "linear-gradient(135deg, rgba(245, 158, 11, 0.18) 0%, rgba(120, 53, 15, 0.12) 100%)",
            "icon_bg": "rgba(245, 158, 11, 0.25)",
            "text_accent": "#fde68a"
        },
        "purple": {
            "border": "#8b5cf6",
            "bg_gradient": "linear-gradient(135deg, rgba(139, 92, 246, 0.18) 0%, rgba(76, 29, 149, 0.12) 100%)",
            "icon_bg": "rgba(139, 92, 246, 0.25)",
            "text_accent": "#c4b5fd"
        }
    }

    t = color_map.get(theme, color_map["blue"])

    card_html = (
        '<div style="background:{bg};border:1px solid {border};border-left:4px solid {border};'
        'border-radius:12px;padding:18px 20px;margin-bottom:15px;'
        'box-shadow:0 4px 15px rgba(0,0,0,0.25);min-height:116px;box-sizing:border-box;'
        'transition:transform 0.2s ease, box-shadow 0.2s ease;">'
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;">'
        '<div style="min-width:0;flex:1 1 130px;">'
        '<p style="color:#e2e8f0;font-size:0.85rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.6px;margin:0 0 4px 0;">{title}</p>'
        '<h2 style="color:#ffffff;font-size:2.2rem;font-weight:800;margin:0;line-height:1.1;">{value}</h2>'
        '<p style="color:{accent};font-size:0.82rem;margin:6px 0 0 0;font-weight:700;">{subtitle}</p>'
        '</div>'
        '<div style="background:{icon_bg};border:1px solid {border};border-radius:10px;width:46px;height:46px;'
        'display:flex;align-items:center;justify-content:center;font-size:1.5rem;line-height:1;flex:0 0 46px;'
        'box-shadow:0 2px 8px rgba(0,0,0,0.15);">{icon}</div>'
        '</div></div>'
    ).format(
        bg=t["bg_gradient"], border=t["border"], icon_bg=t["icon_bg"],
        accent=t["text_accent"], title=title, value=value, subtitle=subtitle, icon=icon
    )
    st.markdown(card_html, unsafe_allow_html=True)


def render_parking_summary_card(parking: Dict[str, Any]):
    """Renders a facility summary banner with distance, amenities, and available slots."""
    distance_tag = ""
    if parking.get("distance_km") is not None:
        distance_tag = f"""<span style="background: rgba(59, 130, 246, 0.25); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.5); padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; margin-right: 6px;">📍 {parking['distance_km']} km away</span>"""

    ev_tag = ""
    if parking.get("ev_available"):
        ev_tag = """<span style="background: rgba(16, 185, 129, 0.25); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.5); padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; margin-right: 6px;">⚡ EV Charging</span>"""

    acc_tag = ""
    if parking.get("accessible_available"):
        acc_tag = """<span style="background: rgba(139, 92, 246, 0.25); color: #c4b5fd; border: 1px solid rgba(139, 92, 246, 0.5); padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 700;">♿ Accessible</span>"""

    avail_count = parking.get("available_slots", 0)
    total_count = parking.get("total_slots", 0)
    avail_color = "#34d399" if avail_count > 0 else "#f87171"
    avail_bg = "rgba(16, 185, 129, 0.2)" if avail_count > 0 else "rgba(239, 68, 68, 0.2)"

    card_html = (
        '<div style="background:rgba(30,41,59,0.92);border:1px solid rgba(148,163,184,0.3);'
        'border-radius:12px;padding:18px 22px;margin-bottom:14px;box-shadow:0 4px 12px rgba(0,0,0,0.15);">'
        '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">'
        '<div style="min-width:0;flex:1 1 260px;">'
        '<h3 style="color:#ffffff;margin:0 0 6px 0;font-size:1.25rem;font-weight:700;">{name}</h3>'
        '<p style="color:#cbd5e1;font-size:0.9rem;margin:0 0 10px 0;">📍 {address}</p>'
        '<div style="margin-top:6px;">{distance}{ev}{accessible}</div>'
        '</div>'
        '<div style="text-align:right;flex:0 0 auto;">'
        '<div style="background:{avail_bg};color:{avail_color};border:1px solid {avail_color}60;'
        'padding:6px 16px;border-radius:8px;font-weight:800;font-size:1rem;display:inline-block;margin-bottom:6px;">'
        '{available} / {total} Available</div>'
        '<div style="color:#f1f5f9;font-size:0.95rem;font-weight:700;">₹{fee:.2f} / hr</div>'
        '</div></div></div>'
    ).format(
        name=parking.get("parking_name", "Parking Facility"),
        address=parking.get("address") or parking.get("area", ""),
        distance=distance_tag, ev=ev_tag, accessible=acc_tag,
        avail_bg=avail_bg, avail_color=avail_color, available=avail_count,
        total=total_count, fee=float(parking.get("parking_fee") or 0)
    )
    st.markdown(card_html, unsafe_allow_html=True)


def get_slot_status_badge(status: str) -> str:
    """Returns styled inline HTML badge for slot status."""
    status_lower = str(status).lower()
    styles = {
        "available": ("#34d399", "rgba(16, 185, 129, 0.25)", "🟢 Available"),
        "reserved": ("#fbbf24", "rgba(245, 158, 11, 0.25)", "🟡 Reserved"),
        "occupied": ("#f87171", "rgba(239, 68, 68, 0.25)", "🔴 Occupied"),
        "maintenance": ("#94a3b8", "rgba(100, 116, 139, 0.25)", "🔧 Maintenance")
    }
    color, bg, label = styles.get(status_lower, ("#94a3b8", "rgba(148, 163, 184, 0.25)", status.capitalize()))
    return f"""<span style="background: {bg}; color: {color}; border: 1px solid {color}70; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; display: inline-block;">{label}</span>"""
