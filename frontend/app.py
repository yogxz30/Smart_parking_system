import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from frontend.components.navigation import render_sidebar
from frontend.pages.login import render_login_page
from frontend.pages.user_dashboard import render_user_dashboard
from frontend.pages.parking_search import render_parking_search
from frontend.pages.booking import render_booking_flow
from frontend.pages.my_bookings import render_my_bookings
from frontend.pages.profile import render_user_profile
from frontend.pages.parking_management import render_parking_management
from frontend.pages.admin_dashboard import render_admin_dashboard



# ==============================================================================
# Page Configuration
# ==============================================================================
st.set_page_config(
    page_title="Smart Parking Finder & Management",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# Global Custom CSS for High-Contrast, Polished Modern Aesthetics
# ==============================================================================
CUSTOM_CSS = """
<style>
    /* Google Fonts & Base Theme */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Main background styling */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 55%, #020617 100%);
        color: #f8fafc;
    }

    /* Hide Default Multipage Nav completely */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #090d16 !important;
        border-right: 1px solid rgba(148, 163, 184, 0.15) !important;
    }

    /* High-contrast Form Label Styling */
    .stTextInput > label, 
    .stSelectbox > label, 
    .stDateInput > label, 
    .stTimeInput > label,
    .stSlider > label,
    .stNumberInput > label,
    .stRadio > label {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.2px !important;
        margin-bottom: 4px !important;
    }

    /* Inputs, Selects, NumberInputs and Textboxes */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div > div, 
    .stDateInput > div > div > input, 
    .stTimeInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: rgba(30, 41, 59, 0.9) !important;
        border: 1px solid rgba(148, 163, 184, 0.3) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #94a3b8 !important;
    }

    .stTextInput > div > div > input:focus, 
    .stSelectbox > div > div > div:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4) !important;
    }

    /* Button Styling */
    .stButton > button,
    .stDownloadButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
        transition: all 0.2s ease-in-out !important;
        border: 1px solid rgba(148, 163, 184, 0.25) !important;
        color: #f8fafc !important;
        background-color: rgba(30, 41, 59, 0.8) !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3) !important;
        border-color: #3b82f6 !important;
        background-color: rgba(51, 65, 85, 0.9) !important;
    }

    /* Primary Button Gradient */
    .stButton > button[kind="primary"],
    .stDownloadButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        border: none !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4) !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.55) !important;
    }

    /* Streamlit Built-in Metric Cards Styling */
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(148, 163, 184, 0.22) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    }

    [data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.85rem !important;
    }

    [data-testid="stMetricDelta"] {
        font-weight: 700 !important;
        font-size: 0.82rem !important;
    }

    /* Expander Container */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.85) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
    }

    .streamlit-expanderContent {
        background-color: rgba(15, 23, 42, 0.7) !important;
        border-bottom-left-radius: 10px !important;
        border-bottom-right-radius: 10px !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-top: none !important;
    }

    /* Tab Header Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background-color: transparent !important;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 8px !important;
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        padding: 10px 18px !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(59, 130, 246, 0.25) !important;
        border-color: #3b82f6 !important;
        color: #ffffff !important;
    }

    /* Dataframe Table Dark Theme Polish */
    [data-testid="stDataFrame"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* Alert Boxes (Info, Warning, Error, Success) */
    .stAlert {
        border-radius: 10px !important;
        border-width: 1px !important;
        font-weight: 500 !important;
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #090d16;
    }
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #475569;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================================
# Session Routing & Application Controller
# ==============================================================================
def main():
    token = st.session_state.get("token")
    user = st.session_state.get("user")

    if not token or not user:
        # Hide sidebar on Login/Register page for a clean, focused view
        st.markdown(
            "<style>[data-testid='stSidebar'] { display: none !important; }</style>",
            unsafe_allow_html=True
        )
        # Show Login / Registration View
        render_login_page()
    else:
        # Render Persistent Sidebar Navigation for Authenticated User
        render_sidebar(user)

        # Route to Selected Page
        active_page = st.session_state.get("active_page", "dashboard")

        if active_page == "dashboard":
            render_user_dashboard()
        elif active_page == "search":
            render_parking_search()
        elif active_page == "booking":
            render_booking_flow()
        elif active_page == "my_bookings":
            render_my_bookings()
        elif active_page == "profile":
            render_user_profile()
        elif active_page == "parking_management":
            if str(user.get("role", "user")).lower() in {"manager", "admin"}:
                render_parking_management()
            else:
                st.session_state["active_page"] = "dashboard"
                st.rerun()
        elif active_page in {"admin_dashboard", "admin"}:
            if str(user.get("role", "user")).lower() == "admin":
                render_admin_dashboard()
            else:
                st.session_state["active_page"] = "dashboard"
                st.rerun()
        else:
            render_user_dashboard()



if __name__ == "__main__":
    main()
