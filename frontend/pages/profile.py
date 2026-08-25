import streamlit as st
from datetime import datetime
from frontend.components.api_client import api
from frontend.components.tables import format_dt


def render_user_profile():
    """
    Renders the User Profile and Account Information view.
    BUG FIX: Raw HTML no longer shown as literal text — all st.markdown calls
    use unsafe_allow_html=True and HTML is built with clean string formatting
    (no textwrap.dedent on f-strings, which caused newline-prefixed HTML
    to be treated as code blocks in some Streamlit versions).
    Feature 8: Profile edit (name/phone) and password change forms added.
    """
    token = st.session_state.get("token")
    if not token:
        st.warning("Please sign in to view your profile.")
        st.session_state["active_page"] = "login"
        st.rerun()

    with st.spinner("Loading profile..."):
        prof_res = api.get_user_profile(token)
        book_res = api.get_my_bookings(token)
        sess_res = api.get_my_sessions(token)

    if not prof_res.get("success"):
        st.error(f"Failed to fetch profile: {prof_res.get('error')}")
        return

    user = prof_res.get("data", {})
    bookings = book_res.get("data", []) if book_res.get("success") else []
    sessions = sess_res.get("data", []) if sess_res.get("success") else []

    # =========================================================================
    # Header — BUG FIX: use direct string (no textwrap.dedent on f-string)
    # =========================================================================
    st.markdown(
        '<div style="margin-bottom:20px;">'
        '<h1 style="color:#ffffff;font-size:1.8rem;font-weight:800;margin:0;">👤 User Profile</h1>'
        '<p style="color:#cbd5e1;font-size:0.95rem;margin:4px 0 0 0;">'
        'Manage your account information and view your activity summary.'
        '</p></div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1.5, 1])

    # =========================================================================
    # Left column: Profile card
    # BUG FIX: Build HTML as a plain string with .format() so no nested
    # indentation issues that confused textwrap.dedent + f-string.
    # =========================================================================
    with col1:
        initial = user.get("name", "U")[0].upper()
        name_val = user.get("name", "")
        role_val = str(user.get("role", "user")).upper()
        email_val = user.get("email", "")
        phone_val = user.get("phone") or "Not provided"
        status_val = user.get("status", "active")
        created_val = format_dt(user.get("created_at"))

        role_color = "#38bdf8" if role_val == "ADMIN" else ("#a78bfa" if role_val == "MANAGER" else "#34d399")
        role_bg = "rgba(56, 189, 248, 0.18)" if role_val == "ADMIN" else ("rgba(167, 139, 250, 0.18)" if role_val == "MANAGER" else "rgba(52, 211, 153, 0.18)")

        user_card_html = (
            '<div style="background:rgba(30,41,59,0.85);border:1px solid rgba(148,163,184,0.25);'
            'border-radius:12px;padding:24px;margin-bottom:20px;box-shadow:0 4px 14px rgba(0,0,0,0.2);">'
            '<div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;">'
            '<div style="width:56px;height:56px;border-radius:50%;'
            'background:linear-gradient(135deg,#3b82f6 0%,#1d4ed8 100%);color:#ffffff;'
            'display:flex;align-items:center;justify-content:center;'
            'font-weight:800;font-size:1.6rem;box-shadow:0 4px 12px rgba(59,130,246,0.4);">{initial}</div>'
            '<div>'
            '<h2 style="color:#ffffff;font-size:1.35rem;font-weight:800;margin:0;">{name}</h2>'
            '<span style="background:{role_bg};color:{role_color};'
            'border:1px solid {role_color}60;padding:2px 10px;border-radius:6px;'
            'font-size:0.78rem;font-weight:700;text-transform:uppercase;'
            'display:inline-block;margin-top:5px;">{role} Account</span>'
            '</div></div>'
            '<div style="margin-bottom:14px;">'
            '<p style="color:#94a3b8;font-size:0.82rem;font-weight:600;margin:0 0 2px 0;">Email Address</p>'
            '<strong style="color:#ffffff;font-size:1.02rem;">{email}</strong>'
            '</div>'
            '<div style="margin-bottom:14px;">'
            '<p style="color:#94a3b8;font-size:0.82rem;font-weight:600;margin:0 0 2px 0;">Phone Number</p>'
            '<strong style="color:#ffffff;font-size:1.02rem;">{phone}</strong>'
            '</div>'
            '<div style="margin-bottom:14px;">'
            '<p style="color:#94a3b8;font-size:0.82rem;font-weight:600;margin:0 0 2px 0;">Account Status</p>'
            '<strong style="color:#34d399;font-size:1.02rem;text-transform:capitalize;">{status}</strong>'
            '</div>'
            '<div>'
            '<p style="color:#94a3b8;font-size:0.82rem;font-weight:600;margin:0 0 2px 0;">Member Since</p>'
            '<strong style="color:#cbd5e1;font-size:0.92rem;">{created}</strong>'
            '</div></div>'
        ).format(
            initial=initial, name=name_val, role=role_val, role_color=role_color, role_bg=role_bg,
            email=email_val, phone=phone_val, status=status_val, created=created_val
        )
        st.markdown(user_card_html, unsafe_allow_html=True)

    # =========================================================================
    # Right column: Activity overview + sign out
    # =========================================================================
    with col2:
        activity_card_html = (
            '<div style="background:rgba(15,23,42,0.85);border:1px solid rgba(148,163,184,0.25);'
            'border-radius:12px;padding:24px;text-align:center;margin-bottom:20px;box-shadow:0 4px 14px rgba(0,0,0,0.2);">'
            '<h3 style="color:#ffffff;font-size:1.2rem;font-weight:800;margin:0 0 16px 0;">'
            '📊 Activity Overview</h3>'
            '<div style="background:rgba(59,130,246,0.15);border:1px solid rgba(59,130,246,0.4);'
            'border-radius:10px;padding:16px;margin-bottom:14px;">'
            '<p style="color:#cbd5e1;font-size:0.85rem;font-weight:600;margin:0 0 4px 0;">'
            'Total Bookings Created</p>'
            '<h2 style="color:#60a5fa;font-size:2rem;font-weight:800;margin:0;">{total_bookings}</h2>'
            '</div>'
            '<div style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.4);'
            'border-radius:10px;padding:16px;">'
            '<p style="color:#cbd5e1;font-size:0.85rem;font-weight:600;margin:0 0 4px 0;">'
            'Completed Parking Sessions</p>'
            '<h2 style="color:#34d399;font-size:2rem;font-weight:800;margin:0;">{total_sessions}</h2>'
            '</div></div>'
        ).format(total_bookings=len(bookings), total_sessions=len(sessions))
        st.markdown(activity_card_html, unsafe_allow_html=True)

        if st.button("🚪 Sign Out", key="btn_profile_signout", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()

    # =========================================================================
    # Feature 8: Profile Edit Form
    # =========================================================================
    st.markdown(
        '<h3 style="color:#ffffff;font-size:1.3rem;font-weight:800;margin:28px 0 14px 0;">'
        '✏️ Edit Profile</h3>',
        unsafe_allow_html=True
    )

    with st.form("form_edit_profile", clear_on_submit=False):
        st.markdown(
            '<p style="color:#cbd5e1;font-size:0.9rem;margin:0 0 12px 0;">'
            'Update your display name and phone number. Leave a field blank to keep current value.</p>',
            unsafe_allow_html=True
        )
        edit_col1, edit_col2 = st.columns(2)
        with edit_col1:
            new_name = st.text_input(
                "Full Name",
                value=user.get("name", ""),
                placeholder="Enter your full name",
                key="edit_name_input"
            )
        with edit_col2:
            new_phone = st.text_input(
                "Phone Number",
                value=user.get("phone") or "",
                placeholder="e.g. 9876543210",
                key="edit_phone_input"
            )

        submitted_profile = st.form_submit_button(
            "💾 Save Profile Changes", use_container_width=True, type="primary"
        )

    if submitted_profile:
        # Validate
        errors = []
        name_stripped = new_name.strip()
        phone_stripped = new_phone.strip()

        if name_stripped and len(name_stripped) < 2:
            errors.append("Name must be at least 2 characters.")
        if phone_stripped:
            import re
            if not re.match(r'^[\d\s\+\-\(\)]{7,20}$', phone_stripped):
                errors.append("Phone number format is invalid. Use digits, spaces, +, -, () only.")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            with st.spinner("Saving profile..."):
                res = api.update_profile(
                    token=token,
                    name=name_stripped if name_stripped else None,
                    phone=phone_stripped if phone_stripped else None
                )
            if res.get("success"):
                st.success("✅ Profile updated successfully!")
                # Update session state user info
                updated_user = res.get("data", {})
                if st.session_state.get("user"):
                    st.session_state["user"]["name"] = updated_user.get("name", name_stripped)
                    st.session_state["user"]["phone"] = updated_user.get("phone", phone_stripped)
                st.rerun()
            else:
                st.error(f"❌ Update failed: {res.get('error')}")

    # =========================================================================
    # Feature 8: Password Change Form
    # =========================================================================
    st.markdown(
        '<h3 style="color:#ffffff;font-size:1.3rem;font-weight:800;margin:28px 0 14px 0;">'
        '🔐 Change Password</h3>',
        unsafe_allow_html=True
    )

    with st.form("form_change_password", clear_on_submit=True):
        st.markdown(
            '<p style="color:#cbd5e1;font-size:0.9rem;margin:0 0 12px 0;">'
            'Enter your current password to verify, then choose a new password (min 6 characters).</p>',
            unsafe_allow_html=True
        )
        pw_col1, pw_col2, pw_col3 = st.columns(3)
        with pw_col1:
            current_pw = st.text_input(
                "Current Password", type="password",
                placeholder="Current password", key="pw_current"
            )
        with pw_col2:
            new_pw = st.text_input(
                "New Password", type="password",
                placeholder="Min 6 characters", key="pw_new"
            )
        with pw_col3:
            confirm_pw = st.text_input(
                "Confirm New Password", type="password",
                placeholder="Repeat new password", key="pw_confirm"
            )

        submitted_pw = st.form_submit_button(
            "🔑 Update Password", use_container_width=True, type="primary"
        )

    if submitted_pw:
        pw_errors = []
        if not current_pw:
            pw_errors.append("Current password is required.")
        if not new_pw or len(new_pw) < 6:
            pw_errors.append("New password must be at least 6 characters.")
        if new_pw != confirm_pw:
            pw_errors.append("New password and confirmation do not match.")

        if pw_errors:
            for e in pw_errors:
                st.error(f"❌ {e}")
        else:
            with st.spinner("Updating password..."):
                res = api.change_password(
                    token=token,
                    current_password=current_pw,
                    new_password=new_pw,
                    confirm_password=confirm_pw
                )
            if res.get("success"):
                st.success("✅ Password changed successfully! Please log in again with your new password.")
            else:
                st.error(f"❌ Password change failed: {res.get('error')}")
