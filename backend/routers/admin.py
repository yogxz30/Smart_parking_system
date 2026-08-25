from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import (
    User, UserRole, UserStatus,
    ParkingLocation, ParkingLocationStatus,
    ParkingSlot, SlotStatus, SlotType,
    Booking, BookingStatus,
    ParkingSession, SessionStatus
)
from backend.schemas import (
    UserResponse, UserStatusUpdate,
    AdminDashboardStats, AdminParkingSummaryItem,
    AdminSlotSummary, AdminBookingItem,
    AdminBookingSummary, MostUsedParkingItem,
    ParkingOccupancyItem, AdminReportsResponse
)
from backend.services.auth_service import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin & Dashboard"])


# ==============================================================================
# Security Dependency: Require Admin Role
# ==============================================================================
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency ensuring only users with the 'admin' role can access admin endpoints.
    Raises HTTP 403 Forbidden for non-admin accounts.
    """
    role_val = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role_val.lower() != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ==============================================================================
# 1. Summary Cards / Dashboard Statistics
# ==============================================================================
@router.get("/dashboard-stats", response_model=AdminDashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Returns live aggregate counts for dashboard summary cards:
    Total Users, Total Parking Locations, Total Slots, Available Slots,
    Occupied Slots, Reserved Slots, Maintenance Slots, and Total Bookings.
    """
    total_users = db.query(func.count(User.user_id)).scalar() or 0
    total_locations = db.query(func.count(ParkingLocation.parking_id)).scalar() or 0
    total_slots = db.query(func.count(ParkingSlot.slot_id)).scalar() or 0
    available_slots = db.query(func.count(ParkingSlot.slot_id)).filter(ParkingSlot.status == SlotStatus.AVAILABLE).scalar() or 0
    occupied_slots = db.query(func.count(ParkingSlot.slot_id)).filter(ParkingSlot.status == SlotStatus.OCCUPIED).scalar() or 0
    reserved_slots = db.query(func.count(ParkingSlot.slot_id)).filter(ParkingSlot.status == SlotStatus.RESERVED).scalar() or 0
    maintenance_slots = db.query(func.count(ParkingSlot.slot_id)).filter(ParkingSlot.status == SlotStatus.MAINTENANCE).scalar() or 0
    total_bookings = db.query(func.count(Booking.booking_id)).scalar() or 0

    return AdminDashboardStats(
        total_users=total_users,
        total_parking_locations=total_locations,
        total_slots=total_slots,
        available_slots=available_slots,
        occupied_slots=occupied_slots,
        reserved_slots=reserved_slots,
        maintenance_slots=maintenance_slots,
        total_bookings=total_bookings
    )


# ==============================================================================
# 2. Parking Summary & Monitoring
# ==============================================================================
@router.get("/parking-summary", response_model=List[AdminParkingSummaryItem])
def get_parking_summary(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Returns live parking facility summaries with slot availability counts,
    occupancy rates, and booking totals per location.
    """
    locations = db.query(ParkingLocation).order_by(ParkingLocation.parking_id.asc()).all()
    results = []

    for loc in locations:
        slots = loc.slots or []
        total_slots_count = len(slots) if slots else loc.total_slots
        available_count = sum(1 for s in slots if (s.status.value if hasattr(s.status, 'value') else str(s.status)) == SlotStatus.AVAILABLE.value)
        occupied_count = sum(1 for s in slots if (s.status.value if hasattr(s.status, 'value') else str(s.status)) == SlotStatus.OCCUPIED.value)
        reserved_count = sum(1 for s in slots if (s.status.value if hasattr(s.status, 'value') else str(s.status)) == SlotStatus.RESERVED.value)
        maintenance_count = sum(1 for s in slots if (s.status.value if hasattr(s.status, 'value') else str(s.status)) == SlotStatus.MAINTENANCE.value)

        total_bookings = db.query(func.count(Booking.booking_id)).filter(Booking.parking_id == loc.parking_id).scalar() or 0
        occupancy_rate = round((occupied_count / total_slots_count * 100), 1) if total_slots_count > 0 else 0.0

        loc_status = loc.status.value if hasattr(loc.status, 'value') else str(loc.status)

        results.append(AdminParkingSummaryItem(
            parking_id=loc.parking_id,
            parking_name=loc.parking_name,
            area=loc.area,
            address=loc.address,
            parking_fee=float(loc.parking_fee),
            opening_time=loc.opening_time.strftime("%H:%M") if loc.opening_time else None,
            closing_time=loc.closing_time.strftime("%H:%M") if loc.closing_time else None,
            ev_available=loc.ev_available,
            accessible_available=loc.accessible_available,
            status=loc_status,
            total_slots=total_slots_count,
            available_slots=available_count,
            occupied_slots=occupied_count,
            reserved_slots=reserved_count,
            maintenance_slots=maintenance_count,
            total_bookings=total_bookings,
            occupancy_rate=occupancy_rate
        ))

    return results


# ==============================================================================
# 3. Slot Summary Breakdown
# ==============================================================================
@router.get("/slot-summary", response_model=AdminSlotSummary)
def get_slot_summary(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Returns system-wide slot breakdown by status (available, occupied, reserved, maintenance),
    type (normal, ev, accessible), and per-location metrics.
    """
    total_slots = db.query(func.count(ParkingSlot.slot_id)).scalar() or 0
    available_slots = db.query(func.count(ParkingSlot.slot_id)).filter(ParkingSlot.status == SlotStatus.AVAILABLE).scalar() or 0
    occupied_slots = db.query(func.count(ParkingSlot.slot_id)).filter(ParkingSlot.status == SlotStatus.OCCUPIED).scalar() or 0
    reserved_slots = db.query(func.count(ParkingSlot.slot_id)).filter(ParkingSlot.status == SlotStatus.RESERVED).scalar() or 0
    maintenance_slots = db.query(func.count(ParkingSlot.slot_id)).filter(ParkingSlot.status == SlotStatus.MAINTENANCE).scalar() or 0

    normal_slots = db.query(func.count(ParkingSlot.slot_id)).filter(ParkingSlot.slot_type == SlotType.NORMAL).scalar() or 0
    ev_slots = db.query(func.count(ParkingSlot.slot_id)).filter(ParkingSlot.slot_type == SlotType.EV).scalar() or 0
    accessible_slots = db.query(func.count(ParkingSlot.slot_id)).filter(ParkingSlot.slot_type == SlotType.ACCESSIBLE).scalar() or 0

    locations = db.query(ParkingLocation).order_by(ParkingLocation.parking_id.asc()).all()
    by_location = []
    for loc in locations:
        slots = loc.slots or []
        t_count = len(slots) if slots else loc.total_slots
        a_count = sum(1 for s in slots if (s.status.value if hasattr(s.status, 'value') else str(s.status)) == SlotStatus.AVAILABLE.value)
        o_count = sum(1 for s in slots if (s.status.value if hasattr(s.status, 'value') else str(s.status)) == SlotStatus.OCCUPIED.value)
        r_count = sum(1 for s in slots if (s.status.value if hasattr(s.status, 'value') else str(s.status)) == SlotStatus.RESERVED.value)
        m_count = sum(1 for s in slots if (s.status.value if hasattr(s.status, 'value') else str(s.status)) == SlotStatus.MAINTENANCE.value)
        by_location.append({
            "parking_id": loc.parking_id,
            "parking_name": loc.parking_name,
            "area": loc.area,
            "total_slots": t_count,
            "available_slots": a_count,
            "occupied_slots": o_count,
            "reserved_slots": r_count,
            "maintenance_slots": m_count
        })

    return AdminSlotSummary(
        total_slots=total_slots,
        available_slots=available_slots,
        occupied_slots=occupied_slots,
        reserved_slots=reserved_slots,
        maintenance_slots=maintenance_slots,
        normal_slots=normal_slots,
        ev_slots=ev_slots,
        accessible_slots=accessible_slots,
        by_location=by_location
    )


# ==============================================================================
# 4. Booking Summary & Monitoring
# ==============================================================================
@router.get("/booking-summary", response_model=AdminBookingSummary)
def get_booking_summary(
    parking_id: Optional[int] = Query(None, description="Filter by parking location ID"),
    status_filter: Optional[str] = Query(None, description="Filter by booking status"),
    search_id: Optional[int] = Query(None, description="Search by exact booking ID"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Returns all bookings with full user, location, and slot context.
    Supports filtering by parking_id, status, and searching by booking ID.
    Includes system-wide booking status counts.
    """
    # System-wide status counts
    reserved_count = db.query(func.count(Booking.booking_id)).filter(Booking.status == BookingStatus.RESERVED).scalar() or 0
    active_count = db.query(func.count(Booking.booking_id)).filter(Booking.status == BookingStatus.ACTIVE).scalar() or 0
    completed_count = db.query(func.count(Booking.booking_id)).filter(Booking.status == BookingStatus.COMPLETED).scalar() or 0
    cancelled_count = db.query(func.count(Booking.booking_id)).filter(Booking.status == BookingStatus.CANCELLED).scalar() or 0
    total_bookings = db.query(func.count(Booking.booking_id)).scalar() or 0

    # Query bookings with filters
    query = db.query(Booking).join(User, Booking.user_id == User.user_id)\
                             .join(ParkingLocation, Booking.parking_id == ParkingLocation.parking_id)\
                             .join(ParkingSlot, Booking.slot_id == ParkingSlot.slot_id)

    if search_id:
        query = query.filter(Booking.booking_id == search_id)
    if parking_id:
        query = query.filter(Booking.parking_id == parking_id)
    if status_filter and status_filter.strip().lower() != "all":
        query = query.filter(Booking.status == status_filter.strip().lower())

    bookings = query.order_by(desc(Booking.created_at)).all()

    booking_items = []
    for b in bookings:
        b_status = b.status.value if hasattr(b.status, 'value') else str(b.status)
        s_type = b.slot.slot_type.value if hasattr(b.slot.slot_type, 'value') else str(b.slot.slot_type)

        booking_items.append(AdminBookingItem(
            booking_id=b.booking_id,
            user_id=b.user_id,
            user_name=b.user.name if b.user else "Unknown",
            user_email=b.user.email if b.user else "Unknown",
            parking_id=b.parking_id,
            parking_name=b.parking.parking_name if b.parking else "Unknown",
            area=b.parking.area if b.parking else "Unknown",
            slot_id=b.slot_id,
            slot_number=b.slot.slot_number if b.slot else "Unknown",
            slot_type=s_type,
            booking_date=b.booking_date,
            start_time=b.start_time,
            end_time=b.end_time,
            status=b_status,
            created_at=b.created_at
        ))

    return AdminBookingSummary(
        total_bookings=total_bookings,
        reserved_count=reserved_count,
        active_count=active_count,
        completed_count=completed_count,
        cancelled_count=cancelled_count,
        bookings=booking_items
    )


# ==============================================================================
# 5. User Management (Read & Activate/Deactivate)
# ==============================================================================
@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Returns all registered users with sanitized profile fields.
    Passwords and hash strings are NEVER exposed.
    """
    users = db.query(User).order_by(User.user_id.asc()).all()
    return users


@router.put("/users/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Activate or deactivate a user account.
    Prevents the current admin from deactivating their own account.
    """
    target_user = db.query(User).filter(User.user_id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    # Protect current admin from accidental lockout
    if admin.user_id == target_user.user_id and status_update.status == "inactive":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own admin account"
        )

    target_user.status = UserStatus.ACTIVE if status_update.status == "active" else UserStatus.INACTIVE
    db.commit()
    db.refresh(target_user)

    return target_user


# ==============================================================================
# 6. Analytics & Reports
# ==============================================================================
@router.get("/reports", response_model=AdminReportsResponse)
def get_admin_reports(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Returns comprehensive analytical reports including most-used parking locations,
    occupancy rates, slot utilization, and booking status distribution.
    """
    # Live counts
    total_bookings = db.query(func.count(Booking.booking_id)).scalar() or 0
    total_slots = db.query(func.count(ParkingSlot.slot_id)).scalar() or 0
    available_slots = db.query(func.count(ParkingSlot.slot_id)).filter(ParkingSlot.status == SlotStatus.AVAILABLE).scalar() or 0
    occupied_slots = db.query(func.count(ParkingSlot.slot_id)).filter(ParkingSlot.status == SlotStatus.OCCUPIED).scalar() or 0
    reserved_slots = db.query(func.count(ParkingSlot.slot_id)).filter(ParkingSlot.status == SlotStatus.RESERVED).scalar() or 0
    maintenance_slots = db.query(func.count(ParkingSlot.slot_id)).filter(ParkingSlot.status == SlotStatus.MAINTENANCE).scalar() or 0

    overall_occupancy = round((occupied_slots / total_slots * 100), 1) if total_slots > 0 else 0.0

    # Most used parking locations by booking count
    top_parking_query = (
        db.query(
            ParkingLocation.parking_id,
            ParkingLocation.parking_name,
            ParkingLocation.area,
            func.count(Booking.booking_id).label("booking_count")
        )
        .join(Booking, ParkingLocation.parking_id == Booking.parking_id)
        .group_by(ParkingLocation.parking_id, ParkingLocation.parking_name, ParkingLocation.area)
        .order_by(desc("booking_count"))
        .limit(10)
        .all()
    )

    most_used = [
        MostUsedParkingItem(
            parking_id=row[0],
            parking_name=row[1],
            area=row[2],
            booking_count=row[3]
        )
        for row in top_parking_query
    ]

    # Per-location occupancy details
    locations = db.query(ParkingLocation).order_by(ParkingLocation.parking_id.asc()).all()
    parking_occupancy_list = []
    bookings_by_parking = []

    for loc in locations:
        slots = loc.slots or []
        t_count = len(slots) if slots else loc.total_slots
        o_count = sum(1 for s in slots if (s.status.value if hasattr(s.status, 'value') else str(s.status)) == SlotStatus.OCCUPIED.value)
        a_count = sum(1 for s in slots if (s.status.value if hasattr(s.status, 'value') else str(s.status)) == SlotStatus.AVAILABLE.value)
        r_count = sum(1 for s in slots if (s.status.value if hasattr(s.status, 'value') else str(s.status)) == SlotStatus.RESERVED.value)
        occ_rate = round((o_count / t_count * 100), 1) if t_count > 0 else 0.0

        b_count = db.query(func.count(Booking.booking_id)).filter(Booking.parking_id == loc.parking_id).scalar() or 0

        parking_occupancy_list.append(ParkingOccupancyItem(
            parking_id=loc.parking_id,
            parking_name=loc.parking_name,
            area=loc.area,
            total_slots=t_count,
            occupied_slots=o_count,
            available_slots=a_count,
            reserved_slots=r_count,
            occupancy_rate=occ_rate
        ))

        bookings_by_parking.append({
            "parking_id": loc.parking_id,
            "parking_name": loc.parking_name,
            "area": loc.area,
            "booking_count": b_count
        })

    # Booking status counts
    reserved_b = db.query(func.count(Booking.booking_id)).filter(Booking.status == BookingStatus.RESERVED).scalar() or 0
    active_b = db.query(func.count(Booking.booking_id)).filter(Booking.status == BookingStatus.ACTIVE).scalar() or 0
    completed_b = db.query(func.count(Booking.booking_id)).filter(Booking.status == BookingStatus.COMPLETED).scalar() or 0
    cancelled_b = db.query(func.count(Booking.booking_id)).filter(Booking.status == BookingStatus.CANCELLED).scalar() or 0

    booking_status_counts = {
        "Reserved": reserved_b,
        "Active": active_b,
        "Completed": completed_b,
        "Cancelled": cancelled_b
    }

    slot_status_counts = {
        "Available": available_slots,
        "Occupied": occupied_slots,
        "Reserved": reserved_slots,
        "Maintenance": maintenance_slots
    }

    return AdminReportsResponse(
        total_bookings=total_bookings,
        total_slots=total_slots,
        available_slots=available_slots,
        occupied_slots=occupied_slots,
        reserved_slots=reserved_slots,
        overall_occupancy_rate=overall_occupancy,
        most_used_parking=most_used,
        parking_occupancy_list=parking_occupancy_list,
        booking_status_counts=booking_status_counts,
        slot_status_counts=slot_status_counts,
        bookings_by_parking=bookings_by_parking
    )
