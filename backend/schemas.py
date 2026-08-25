from datetime import datetime, date, time
from typing import Optional, List, Literal
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
