from datetime import datetime, date, time
from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict



# ==============================================================================
# Authentication Schemas
# ==============================================================================

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="John Doe")
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., min_length=6, max_length=100, example="password123")
    phone: Optional[str] = Field(None, max_length=20, example="9876543210")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., min_length=1, example="password123")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: str
    phone: Optional[str] = None
    role: str
    status: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


# ==============================================================================
# Parking Location & Slot Schemas
# ==============================================================================

class ParkingSlotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slot_id: int
    parking_id: int
    slot_number: str
    slot_type: str
    status: str


class ParkingLocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    parking_id: int
    parking_name: str
    area: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_slots: int
    available_slots: int = 0
    parking_fee: float
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    ev_available: bool
    accessible_available: bool
    status: str
    distance_km: Optional[float] = None


class ParkingDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    parking_id: int
    parking_name: str
    area: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_slots: int
    available_slots: int = 0
    parking_fee: float
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    ev_available: bool
    accessible_available: bool
    status: str
    slots: List[ParkingSlotResponse] = []


class ParkingLocationCreate(BaseModel):
    parking_name: str = Field(..., min_length=1, max_length=150)
    area: str = Field(..., min_length=1, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_slots: int = Field(0, ge=0)
    parking_fee: float = Field(0, ge=0)
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    ev_available: bool = False
    accessible_available: bool = False


class ParkingLocationUpdate(BaseModel):
    parking_name: Optional[str] = Field(None, min_length=1, max_length=150)
    area: Optional[str] = Field(None, min_length=1, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_slots: Optional[int] = Field(None, ge=0)
    parking_fee: Optional[float] = Field(None, ge=0)
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    ev_available: Optional[bool] = None
    accessible_available: Optional[bool] = None


class ParkingActiveStatusUpdate(BaseModel):
    is_active: bool


class ParkingSlotCreate(BaseModel):
    parking_id: int = Field(..., gt=0)
    slot_number: str = Field(..., min_length=1, max_length=20)
    slot_type: Literal["normal", "ev", "accessible"] = "normal"


class SlotStatusUpdate(BaseModel):
    status: Literal["available", "reserved", "occupied", "maintenance"]


# ==============================================================================
# Booking Schemas
# ==============================================================================

class BookingCreate(BaseModel):
    parking_id: int = Field(..., gt=0, example=1)
    slot_id: int = Field(..., gt=0, example=1)
    start_time: datetime = Field(..., example="2026-08-23T16:00:00")
    duration_hours: int = Field(..., ge=1, le=48, example=2)


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_id: int
    user_id: int
    parking_id: int
    parking_name: Optional[str] = None
    area: Optional[str] = None
    slot_id: int
    slot_number: Optional[str] = None
    booking_date: date
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime


class BookingMyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_id: int
    parking_id: int
    parking_name: str
    area: str
    slot_id: int
    slot_number: str
    slot_type: str
    booking_date: date
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime


# ==============================================================================
# Parking Session Schemas
# ==============================================================================

class CheckInRequest(BaseModel):
    booking_id: int = Field(..., gt=0, example=1)


class CheckOutRequest(BaseModel):
    booking_id: Optional[int] = Field(None, gt=0, example=1)
    session_id: Optional[int] = Field(None, gt=0, example=1)


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: int
    booking_id: int
    user_id: int
    parking_id: int
    parking_name: Optional[str] = None
    slot_id: int
    slot_number: Optional[str] = None
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: str


# ==============================================================================
# User Dashboard Schemas
# ==============================================================================

class UserDashboardStats(BaseModel):
    nearby_parking_count: int = 0
    available_slots_count: int = 0
    active_bookings_count: int = 0


class UserDashboardResponse(BaseModel):
    user: UserResponse
    stats: UserDashboardStats
    active_booking: Optional[BookingResponse] = None
    recent_bookings: List[BookingResponse] = []


# ==============================================================================
# Favorites Schemas
# ==============================================================================

class FavoriteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    favorite_id: int
    user_id: int
    parking_id: int
    parking_name: Optional[str] = None
    area: Optional[str] = None
    parking_fee: Optional[float] = None
    ev_available: Optional[bool] = None
    accessible_available: Optional[bool] = None
    created_at: datetime


# ==============================================================================
# Profile Edit & Password Change Schemas
# ==============================================================================

class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100, example="Jane Doe")
    phone: Optional[str] = Field(None, max_length=20, example="9876543210")


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, example="oldpassword123")
    new_password: str = Field(..., min_length=6, max_length=100, example="newpassword456")
    confirm_password: str = Field(..., min_length=6, max_length=100, example="newpassword456")


# ==============================================================================
# Admin & Dashboard Schemas (Member 3)
# ==============================================================================

class UserStatusUpdate(BaseModel):
    status: Literal["active", "inactive"]


class AdminDashboardStats(BaseModel):
    total_users: int = 0
    total_parking_locations: int = 0
    total_slots: int = 0
    available_slots: int = 0
    occupied_slots: int = 0
    reserved_slots: int = 0
    maintenance_slots: int = 0
    total_bookings: int = 0


class AdminParkingSummaryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    parking_id: int
    parking_name: str
    area: str
    address: Optional[str] = None
    parking_fee: float
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    ev_available: bool
    accessible_available: bool
    status: str
    total_slots: int
    available_slots: int
    occupied_slots: int
    reserved_slots: int
    maintenance_slots: int
    total_bookings: int
    occupancy_rate: float


class AdminSlotSummary(BaseModel):
    total_slots: int
    available_slots: int
    occupied_slots: int
    reserved_slots: int
    maintenance_slots: int
    normal_slots: int
    ev_slots: int
    accessible_slots: int
    by_location: List[Dict[str, Any]] = []


class AdminBookingItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_id: int
    user_id: int
    user_name: str
    user_email: str
    parking_id: int
    parking_name: str
    area: str
    slot_id: int
    slot_number: str
    slot_type: str
    booking_date: date
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime


class AdminBookingSummary(BaseModel):
    total_bookings: int
    reserved_count: int
    active_count: int
    completed_count: int
    cancelled_count: int
    bookings: List[AdminBookingItem] = []


class MostUsedParkingItem(BaseModel):
    parking_id: int
    parking_name: str
    area: str
    booking_count: int


class ParkingOccupancyItem(BaseModel):
    parking_id: int
    parking_name: str
    area: str
    total_slots: int
    occupied_slots: int
    available_slots: int
    reserved_slots: int
    occupancy_rate: float


class AdminReportsResponse(BaseModel):
    total_bookings: int
    total_slots: int
    available_slots: int
    occupied_slots: int
    reserved_slots: int
    overall_occupancy_rate: float
    most_used_parking: List[MostUsedParkingItem] = []
    parking_occupancy_list: List[ParkingOccupancyItem] = []
    booking_status_counts: Dict[str, int] = {}
    slot_status_counts: Dict[str, int] = {}
    bookings_by_parking: List[Dict[str, Any]] = []

