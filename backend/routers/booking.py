from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models import Booking, ParkingSession, User
from backend.schemas import (
    BookingCreate, BookingResponse, BookingMyResponse,
    CheckInRequest, CheckOutRequest, SessionResponse
)
from backend.services.auth_service import get_current_user
from backend.services.booking_service import (
    create_user_booking, cancel_user_booking,
    process_check_in, process_check_out
)

router = APIRouter(tags=["Bookings & Sessions"])


# ==============================================================================
# Booking Endpoints
# ==============================================================================

@router.post("/api/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_in: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new parking slot reservation for the authenticated user.
    Validates availability, ensures slot is not under maintenance, prevents double booking,
    and transitions slot status to 'reserved'.
    """
    booking = create_user_booking(current_user, booking_in, db)

    return BookingResponse(
        booking_id=booking.booking_id,
        user_id=booking.user_id,
        parking_id=booking.parking_id,
        parking_name=booking.parking.parking_name if booking.parking else None,
        area=booking.parking.area if booking.parking else None,
        slot_id=booking.slot_id,
        slot_number=booking.slot.slot_number if booking.slot else None,
        booking_date=booking.booking_date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        status=booking.status.value if hasattr(booking.status, "value") else str(booking.status),
        created_at=booking.created_at
    )


@router.get("/api/bookings/my", response_model=List[BookingMyResponse])
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all bookings made by the authenticated user, ordered from most recent to oldest.
    """
    bookings = db.query(Booking).filter(
        Booking.user_id == current_user.user_id
    ).order_by(desc(Booking.created_at)).all()

    return [
        BookingMyResponse(
            booking_id=b.booking_id,
            parking_id=b.parking_id,
            parking_name=b.parking.parking_name if b.parking else "Unknown Facility",
            area=b.parking.area if b.parking else "Unknown Area",
            slot_id=b.slot_id,
            slot_number=b.slot.slot_number if b.slot else "Unknown Slot",
            slot_type=b.slot.slot_type.value if b.slot and hasattr(b.slot.slot_type, "value") else "normal",
            booking_date=b.booking_date,
            start_time=b.start_time,
            end_time=b.end_time,
            status=b.status.value if hasattr(b.status, "value") else str(b.status),
            created_at=b.created_at
        )
        for b in bookings
    ]


@router.get("/api/bookings/{booking_id}", response_model=BookingResponse)
def get_booking_details(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve details for a specific booking. Users can only view their own bookings.
    """
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking reservation not found"
        )

    if booking.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this booking"
        )

    return BookingResponse(
        booking_id=booking.booking_id,
        user_id=booking.user_id,
        parking_id=booking.parking_id,
        parking_name=booking.parking.parking_name if booking.parking else None,
        area=booking.parking.area if booking.parking else None,
        slot_id=booking.slot_id,
        slot_number=booking.slot.slot_number if booking.slot else None,
        booking_date=booking.booking_date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        status=booking.status.value if hasattr(booking.status, "value") else str(booking.status),
        created_at=booking.created_at
    )


@router.put("/api/bookings/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel an existing reservation before check-in.
    Transitions booking status to 'cancelled' and releases slot status to 'available'.
    """
    booking = cancel_user_booking(current_user, booking_id, db)

    return BookingResponse(
        booking_id=booking.booking_id,
        user_id=booking.user_id,
        parking_id=booking.parking_id,
        parking_name=booking.parking.parking_name if booking.parking else None,
        area=booking.parking.area if booking.parking else None,
        slot_id=booking.slot_id,
        slot_number=booking.slot.slot_number if booking.slot else None,
        booking_date=booking.booking_date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        status=booking.status.value if hasattr(booking.status, "value") else str(booking.status),
        created_at=booking.created_at
    )


# ==============================================================================
# Parking Session Endpoints (Check-in / Check-out)
# ==============================================================================

@router.post("/api/sessions/check-in", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def check_in(
    check_in_in: CheckInRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform check-in for an active reservation.
    Creates parking session, updates booking status to 'active', and slot to 'occupied'.
    """
    session = process_check_in(current_user, check_in_in, db)

    return SessionResponse(
        session_id=session.session_id,
        booking_id=session.booking_id,
        user_id=session.user_id,
        parking_id=session.parking_id,
        parking_name=session.parking.parking_name if session.parking else None,
        slot_id=session.slot_id,
        slot_number=session.slot.slot_number if session.slot else None,
        check_in=session.check_in,
        check_out=session.check_out,
        status=session.status.value if hasattr(session.status, "value") else str(session.status)
    )


@router.post("/api/sessions/check-out", response_model=SessionResponse)
def check_out(
    check_out_in: CheckOutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform check-out for an active parking session.
    Sets check_out time, updates session to 'completed', booking to 'completed', and slot to 'available'.
    """
    session = process_check_out(current_user, check_out_in, db)

    return SessionResponse(
        session_id=session.session_id,
        booking_id=session.booking_id,
        user_id=session.user_id,
        parking_id=session.parking_id,
        parking_name=session.parking.parking_name if session.parking else None,
        slot_id=session.slot_id,
        slot_number=session.slot.slot_number if session.slot else None,
        check_in=session.check_in,
        check_out=session.check_out,
        status=session.status.value if hasattr(session.status, "value") else str(session.status)
    )


@router.get("/api/sessions/my", response_model=List[SessionResponse])
def get_my_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all parking check-in/check-out sessions for the authenticated user.
    """
    sessions = db.query(ParkingSession).filter(
        ParkingSession.user_id == current_user.user_id
    ).order_by(desc(ParkingSession.session_id)).all()

    return [
        SessionResponse(
            session_id=s.session_id,
            booking_id=s.booking_id,
            user_id=s.user_id,
            parking_id=s.parking_id,
            parking_name=s.parking.parking_name if s.parking else None,
            slot_id=s.slot_id,
            slot_number=s.slot.slot_number if s.slot else None,
            check_in=s.check_in,
            check_out=s.check_out,
            status=s.status.value if hasattr(s.status, "value") else str(s.status)
        )
        for s in sessions
    ]
