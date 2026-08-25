import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

# Backend API Base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


class APIClient:
    """Centralized API client for communicating with FastAPI backend."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Process response and extract JSON or raise meaningful exceptions."""
        try:
            data = response.json()
        except Exception:
            data = {"detail": response.text}

        if not response.ok:
            error_msg = data.get("detail", "An unexpected error occurred.")
            if isinstance(error_msg, list):
                # Pydantic validation errors format
                error_msg = "; ".join([f"{e.get('loc', [''])[ -1]}: {e.get('msg', '')}" for e in error_msg])
            return {"success": False, "status_code": response.status_code, "error": str(error_msg)}

        return {"success": True, "status_code": response.status_code, "data": data}

    # =========================================================================
    # Health & System
    # =========================================================================
    def check_health(self) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Cannot connect to backend server: {str(e)}"}

    # =========================================================================
    # Authentication
    # =========================================================================
    def login(self, email: str, password: str) -> Dict[str, Any]:
        try:
            resp = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"email": email.strip(), "password": password},
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def register(self, name: str, email: str, password: str, phone: Optional[str] = None) -> Dict[str, Any]:
        try:
            payload = {
                "name": name.strip(),
                "email": email.strip().lower(),
                "password": password,
                "phone": phone.strip() if phone else None
            }
            resp = requests.post(
                f"{self.base_url}/api/auth/register",
                json=payload,
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    # =========================================================================
    # User Profile & Dashboard
    # =========================================================================
    def get_user_profile(self, token: str) -> Dict[str, Any]:
        try:
            resp = requests.get(
                f"{self.base_url}/api/user/profile",
                headers=self._get_headers(token),
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def get_user_dashboard(self, token: str) -> Dict[str, Any]:
        try:
            resp = requests.get(
                f"{self.base_url}/api/user/dashboard",
                headers=self._get_headers(token),
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    # =========================================================================
    # Parking Locations & Slots
    # =========================================================================
    def get_areas(self) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/api/parking/areas", timeout=8)
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def search_parking(
        self,
        area: Optional[str] = None,
        ev_only: Optional[bool] = None,
        accessible_only: Optional[bool] = None,
        sort_by: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            params = {}
            if area and area != "All Areas":
                params["area"] = area
            if ev_only:
                params["ev_only"] = "true"
            if accessible_only:
                params["accessible_only"] = "true"
            if sort_by:
                params["sort_by"] = sort_by

            resp = requests.get(
                f"{self.base_url}/api/parking",
                params=params,
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def get_parking_details(self, parking_id: int) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/api/parking/{parking_id}", timeout=8)
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def get_parking_slots(self, parking_id: int) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/api/parking/{parking_id}/slots", timeout=8)
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    # =========================================================================
    # Manager Parking Operations
    # =========================================================================
    def get_managed_parking_locations(self, token: str) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/api/parking/management/all", headers=self._get_headers(token), timeout=8)
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def create_parking_location(self, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            resp = requests.post(f"{self.base_url}/api/parking", json=payload, headers=self._get_headers(token), timeout=8)
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def update_parking_location(self, token: str, parking_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            resp = requests.put(f"{self.base_url}/api/parking/{parking_id}", json=payload, headers=self._get_headers(token), timeout=8)
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def set_parking_active_status(self, token: str, parking_id: int, is_active: bool) -> Dict[str, Any]:
        try:
            resp = requests.put(f"{self.base_url}/api/parking/{parking_id}/status", json={"is_active": is_active}, headers=self._get_headers(token), timeout=8)
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def create_slot(self, token: str, parking_id: int, slot_number: str, slot_type: str) -> Dict[str, Any]:
        try:
            resp = requests.post(f"{self.base_url}/api/slots", json={"parking_id": parking_id, "slot_number": slot_number, "slot_type": slot_type}, headers=self._get_headers(token), timeout=8)
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def update_slot_status(self, token: str, slot_id: int, new_status: str) -> Dict[str, Any]:
        try:
            resp = requests.put(f"{self.base_url}/api/slots/{slot_id}/status", json={"status": new_status}, headers=self._get_headers(token), timeout=8)
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def get_all_active_sessions(self, token: str) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/api/sessions/all", headers=self._get_headers(token), timeout=8)
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    # =========================================================================
    # Bookings & Sessions
    # =========================================================================
    def create_booking(
        self,
        token: str,
        parking_id: int,
        slot_id: int,
        start_time_iso: str,
        duration_hours: int
    ) -> Dict[str, Any]:
        try:
            payload = {
                "parking_id": parking_id,
                "slot_id": slot_id,
                "start_time": start_time_iso,
                "duration_hours": duration_hours
            }
            resp = requests.post(
                f"{self.base_url}/api/bookings",
                json=payload,
                headers=self._get_headers(token),
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def get_my_bookings(self, token: str) -> Dict[str, Any]:
        try:
            resp = requests.get(
                f"{self.base_url}/api/bookings/my",
                headers=self._get_headers(token),
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def cancel_booking(self, token: str, booking_id: int) -> Dict[str, Any]:
        try:
            resp = requests.put(
                f"{self.base_url}/api/bookings/{booking_id}/cancel",
                headers=self._get_headers(token),
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def check_in(self, token: str, booking_id: int) -> Dict[str, Any]:
        try:
            resp = requests.post(
                f"{self.base_url}/api/sessions/check-in",
                json={"booking_id": booking_id},
                headers=self._get_headers(token),
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def check_out(self, token: str, session_id: Optional[int] = None, booking_id: Optional[int] = None) -> Dict[str, Any]:
        try:
            payload = {}
            if session_id:
                payload["session_id"] = session_id
            if booking_id:
                payload["booking_id"] = booking_id

            resp = requests.post(
                f"{self.base_url}/api/sessions/check-out",
                json=payload,
                headers=self._get_headers(token),
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def get_my_sessions(self, token: str) -> Dict[str, Any]:
        try:
            resp = requests.get(
                f"{self.base_url}/api/sessions/my",
                headers=self._get_headers(token),
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    # =========================================================================
    # Favorites
    # =========================================================================
    def get_favorites(self, token: str) -> Dict[str, Any]:
        try:
            resp = requests.get(
                f"{self.base_url}/api/user/favorites",
                headers=self._get_headers(token),
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def add_favorite(self, token: str, parking_id: int) -> Dict[str, Any]:
        try:
            resp = requests.post(
                f"{self.base_url}/api/user/favorites",
                params={"parking_id": parking_id},
                headers=self._get_headers(token),
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def remove_favorite(self, token: str, parking_id: int) -> Dict[str, Any]:
        try:
            resp = requests.delete(
                f"{self.base_url}/api/user/favorites/{parking_id}",
                headers=self._get_headers(token),
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    # =========================================================================
    # Profile Edit & Password Change
    # =========================================================================
    def update_profile(self, token: str, name: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, Any]:
        try:
            payload = {}
            if name is not None:
                payload["name"] = name
            if phone is not None:
                payload["phone"] = phone
            resp = requests.put(
                f"{self.base_url}/api/user/profile",
                json=payload,
                headers=self._get_headers(token),
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def change_password(self, token: str, current_password: str, new_password: str, confirm_password: str) -> Dict[str, Any]:
        try:
            payload = {
                "current_password": current_password,
                "new_password": new_password,
                "confirm_password": confirm_password
            }
            resp = requests.post(
                f"{self.base_url}/api/user/change-password",
                json=payload,
                headers=self._get_headers(token),
                timeout=8
            )
            return self._handle_response(resp)
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}


# Global singleton instance for Streamlit pages
api = APIClient()
