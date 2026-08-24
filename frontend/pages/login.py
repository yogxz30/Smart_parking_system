import streamlit as st
import textwrap
from frontend.components.api_client import api


def render_login_page():
    """
    Renders the focused authentication portal with high-contrast inputs,
    clear typography, and quick demo credentials.
    """
    # Center container with max width
    col_left, col_center, col_right = st.columns([1, 1.8, 1])

    with col_center:
        # Header Branding
        header_html = """
<div style="text-align: center; margin-bottom: 28px; padding-top: 10px;">
    <div style="
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 68px;
        height: 68px;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        border-radius: 20px;
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.45);
        font-size: 2.4rem;
        margin-bottom: 12px;
    ">
        🅿️
    </div>
    <h1 style="color: #ffffff; font-size: 2rem; font-weight: 800; margin: 0; letter-spacing: -0.5px;">
        Smart Parking Finder
    </h1>
    <p style="color: #cbd5e1; font-size: 0.95rem; font-weight: 500; margin-top: 6px;">
        Find available parking in Chennai & reserve your slot instantly.
    </p>
</div>
"""
        st.markdown(textwrap.dedent(header_html).strip(), unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔐 Sign In", "✨ Create Account"])

        # =====================================================================
        # Tab 1: Sign In
        # =====================================================================
        with tab_login:
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            
            with st.form(key="login_form"):
                email = st.text_input("📧 Email Address", placeholder="e.g. john@example.com")
                password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
                
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                submit_login = st.form_submit_button("Sign In to Account", use_container_width=True, type="primary")

                if submit_login:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    else:
                        with st.spinner("Authenticating credentials..."):
                            result = api.login(email=email, password=password)
                            if result.get("success"):
                                data = result.get("data", {})
                                st.session_state["token"] = data.get("access_token")
                                st.session_state["user"] = data.get("user")
                                st.session_state["active_page"] = "dashboard"
                                st.success("✅ Signed in successfully! Redirecting to dashboard...")
                                st.rerun()
                            else:
                                st.error(f"❌ {result.get('error', 'Login failed.')}")

            # Demo Quick Login Card
            demo_box_html = """
<div style="
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 10px;
    padding: 14px;
    margin-top: 22px;
    text-align: center;
">
    <p style="color: #cbd5e1; font-size: 0.85rem; font-weight: 600; margin: 0 0 8px 0;">
        ⚡ Instant Demo Access (Password: <code style="color: #60a5fa; background: rgba(59, 130, 246, 0.15); padding: 2px 6px; border-radius: 4px;">password123</code>):
    </p>
</div>
"""
            st.markdown(textwrap.dedent(demo_box_html).strip(), unsafe_allow_html=True)

            demo_cols = st.columns(2)
            with demo_cols[0]:
                if st.button("👤 Demo: John Doe", key="btn_demo_john", use_container_width=True):
                    with st.spinner("Signing in as John Doe..."):
                        result = api.login("john@example.com", "password123")
                        if result.get("success"):
                            st.session_state["token"] = result["data"]["access_token"]
                            st.session_state["user"] = result["data"]["user"]
                            st.session_state["active_page"] = "dashboard"
                            st.rerun()
            with demo_cols[1]:
                if st.button("👤 Demo: Priya Sharma", key="btn_demo_priya", use_container_width=True):
                    with st.spinner("Signing in as Priya Sharma..."):
                        result = api.login("priya@example.com", "password123")
                        if result.get("success"):
                            st.session_state["token"] = result["data"]["access_token"]
                            st.session_state["user"] = result["data"]["user"]
                            st.session_state["active_page"] = "dashboard"
                            st.rerun()

        # =====================================================================
        # Tab 2: Create Account
        # =====================================================================
        with tab_register:
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            with st.form(key="register_form"):
                reg_name = st.text_input("👤 Full Name", placeholder="e.g. Anand Kumar")
                reg_email = st.text_input("📧 Email Address", placeholder="e.g. anand@example.com")
                reg_phone = st.text_input("📱 Phone Number (Optional)", placeholder="e.g. 9876543210")
                reg_password = st.text_input("🔑 Password (min 6 characters)", type="password", placeholder="Create a secure password")
                reg_confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter your password")

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                submit_reg = st.form_submit_button("Create My Account", use_container_width=True, type="primary")

                if submit_reg:
                    if not reg_name or not reg_email or not reg_password:
                        st.error("Please fill in all required fields.")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters long.")
                    elif reg_password != reg_confirm:
                        st.error("Passwords do not match.")
                    else:
                        with st.spinner("Creating your account..."):
                            result = api.register(
                                name=reg_name,
                                email=reg_email,
                                password=reg_password,
                                phone=reg_phone
                            )
                            if result.get("success"):
                                st.success("🎉 Account created successfully! Please sign in with your credentials on the Sign In tab.")
                            else:
                                st.error(f"❌ {result.get('error', 'Registration failed.')}")
