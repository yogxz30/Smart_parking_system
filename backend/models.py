import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, Numeric, Time, Date, DateTime, 
    Enum as SQLEnum, ForeignKey, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from backend.database import Base


# ==============================================================================
# Enum Definitions matching database/schema.sql
# ==============================================================================

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    MANAGER = "manager"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ParkingLocationStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class SlotType(str, enum.Enum):
    NORMAL = "normal"
    EV = "ev"
    ACCESSIBLE = "accessible"


class SlotStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


class BookingStatus(str, enum.Enum):
    RESERVED = "reserved"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    ACTIVE = "active"


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"


# ==============================================================================
# Table: users
# ==============================================================================
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]), default=UserRole.USER, nullable=False)
    status = Column(SQLEnum(UserStatus, values_callable=lambda x: [e.value for e in x]), default=UserStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("ParkingSession", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")


# ==============================================================================
# Table: parking_locations
# ==============================================================================
class ParkingLocation(Base):
    __tablename__ = "parking_locations"

    parking_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    parking_name = Column(String(150), nullable=False)
    area = Column(String(100), nullable=False, index=True)
    address = Column(String(255), nullable=True)
    latitude = Column(Numeric(10, 7), nullable=True)
    longitude = Column(Numeric(10, 7), nullable=True)
    total_slots = Column(Integer, default=0, nullable=False)
    parking_fee = Column(Numeric(10, 2), default=0.00, nullable=False)
    opening_time = Column(Time, nullable=True)
    closing_time = Column(Time, nullable=True)
    ev_available = Column(Boolean, default=False, nullable=False)
    accessible_available = Column(Boolean, default=False, nullable=False)
    status = Column(SQLEnum(ParkingLocationStatus, values_callable=lambda x: [e.value for e in x]), default=ParkingLocationStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    slots = relationship("ParkingSlot", back_populates="parking", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="parking", cascade="all, delete-orphan")
    sessions = relationship("ParkingSession", back_populates="parking", cascade="all, delete-orphan")
    favorited_by = relationship("Favorite", back_populates="parking", cascade="all, delete-orphan")


# ==============================================================================
# Table: parking_slots
# ==============================================================================
class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    slot_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    parking_id = Column(Integer, ForeignKey("parking_locations.parking_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    slot_number = Column(String(20), nullable=False)
    slot_type = Column(SQLEnum(SlotType, values_callable=lambda x: [e.value for e in x]), default=SlotType.NORMAL, nullable=False)
    status = Column(SQLEnum(SlotStatus, values_callable=lambda x: [e.value for e in x]), default=SlotStatus.AVAILABLE, nullable=False)

    __table_args__ = (
        UniqueConstraint("parking_id", "slot_number", name="uq_parking_slot"),
    )

    # Relationships
    parking = relationship("ParkingLocation", back_populates="slots")
    bookings = relationship("Booking", back_populates="slot", cascade="all, delete-orphan")
    sessions = relationship("ParkingSession", back_populates="slot", cascade="all, delete-orphan")


# ==============================================================================
# Table: bookings
# ==============================================================================
class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    parking_id = Column(Integer, ForeignKey("parking_locations.parking_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    slot_id = Column(Integer, ForeignKey("parking_slots.slot_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    booking_date = Column(Date, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(SQLEnum(BookingStatus, values_callable=lambda x: [e.value for e in x]), default=BookingStatus.RESERVED, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="bookings")
    parking = relationship("ParkingLocation", back_populates="bookings")
    slot = relationship("ParkingSlot", back_populates="bookings")
    session = relationship("ParkingSession", back_populates="booking", uselist=False, cascade="all, delete-orphan")


# ==============================================================================
# Table: parking_sessions
# ==============================================================================
class ParkingSession(Base):
    __tablename__ = "parking_sessions"

    session_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    parking_id = Column(Integer, ForeignKey("parking_locations.parking_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    slot_id = Column(Integer, ForeignKey("parking_slots.slot_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    status = Column(SQLEnum(SessionStatus, values_callable=lambda x: [e.value for e in x]), default=SessionStatus.ACTIVE, nullable=False)

    # Relationships
    booking = relationship("Booking", back_populates="session")
    user = relationship("User", back_populates="sessions")
    parking = relationship("ParkingLocation", back_populates="sessions")
    slot = relationship("ParkingSlot", back_populates="sessions")


# ==============================================================================
# Table: favorites
# ==============================================================================
class Favorite(Base):
    __tablename__ = "favorites"

    favorite_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    parking_id = Column(Integer, ForeignKey("parking_locations.parking_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "parking_id", name="uq_user_parking_fav"),
    )

    # Relationships
    user = relationship("User", back_populates="favorites")
    parking = relationship("ParkingLocation", back_populates="favorited_by")
