from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.models import (
    Booking, ParkingLocation, ParkingSlot, ParkingSession,
    User, BookingStatus, SlotStatus, SessionStatus, ParkingLocationStatus
)
from backend.schemas import BookingCreate, CheckInRequest, CheckOutRequest
from backend.services.parking_service import validate_slot_status_transition


def create_user_booking(
    user: User, 
    booking_in: BookingCreate, 
    db: Session
) -> Booking:
    """
    Validates slot availability and time conflicts, creates a booking record,
    and updates slot status to 'reserved' in a safe transaction.
    """
    # 1. Verify parking facility exists and is active
    parking = db.query(ParkingLocation).filter(
        ParkingLocation.parking_id == booking_in.parking_id,
        ParkingLocation.status == ParkingLocationStatus.ACTIVE
    ).first()
    if not parking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking facility not found or is currently inactive"
        )

    # 2. Verify slot exists and belongs to this parking facility
    slot = db.query(ParkingSlot).filter(
        ParkingSlot.slot_id == booking_in.slot_id,
        ParkingSlot.parking_id == booking_in.parking_id
    ).with_for_update().first()

    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking slot not found in the selected facility"
        )

    if slot.status == SlotStatus.MAINTENANCE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The selected slot is currently under maintenance and cannot be booked"
        )

    if slot.status == SlotStatus.OCCUPIED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The selected slot is currently occupied"
        )

    # 3. Calculate start and end times
    start_time = booking_in.start_time
    # Ensure start_time does not have timezone issues when comparing with naive DB timestamps
    if hasattr(start_time, "tzinfo") and start_time.tzinfo is not None:
        start_time = start_time.replace(tzinfo=None)

    end_time = start_time + timedelta(hours=booking_in.duration_hours)
    booking_date = start_time.date()

    # 4. Check for overlapping reservations on the same slot
    overlapping_booking = db.query(Booking).filter(
        Booking.slot_id == slot.slot_id,
        Booking.status.in_([BookingStatus.RESERVED, BookingStatus.ACTIVE]),
        and_(
            Booking.start_time < end_time,
            Booking.end_time > start_time
        )
    ).first()

    if overlapping_booking:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This slot is already reserved for the requested time period"
        )

    # 5. Create new Booking
    new_booking = Booking(
        user_id=user.user_id,
        parking_id=parking.parking_id,
        slot_id=slot.slot_id,
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
        status=BookingStatus.RESERVED
    )

    # 6. Update slot status to reserved
    slot.status = SlotStatus.RESERVED

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking


def cancel_user_booking(
    user: User, 
    booking_id: int, 
    db: Session
) -> Booking:
    """
    Cancels a user's eligible reservation before check-in and releases the slot to 'available'.
    """
    booking = db.query(Booking).filter(
        Booking.booking_id == booking_id
    ).with_for_update().first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking reservation not found"
        )

    if booking.user_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to cancel this booking"
        )

    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled"
        )

    if booking.status == BookingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a completed booking"
        )

    if booking.status == BookingStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel an active parking session. Please check out instead."
        )

    # Update booking and slot status
    booking.status = BookingStatus.CANCELLED

    slot = db.query(ParkingSlot).filter(ParkingSlot.slot_id == booking.slot_id).first()
    if slot and slot.status == SlotStatus.RESERVED:
        validate_slot_status_transition(slot.status, SlotStatus.AVAILABLE)
        slot.status = SlotStatus.AVAILABLE

    db.commit()
    db.refresh(booking)

    return booking


def process_check_in(
    user: User, 
    check_in_in: CheckInRequest, 
    db: Session
) -> ParkingSession:
    """
    Processes check-in for a confirmed reservation:
    - Verifies ownership and reserved state
    - Creates an active parking_session
    - Transitions booking -> active, slot -> occupied
    """
    booking = db.query(Booking).filter(
        Booking.booking_id == check_in_in.booking_id
    ).with_for_update().first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking reservation not found"
        )

    if booking.user_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to check in for this booking"
        )

    if booking.status != BookingStatus.RESERVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot check in: booking is in '{booking.status.value}' status"
        )

    # Check if a session already exists
    existing_session = db.query(ParkingSession).filter(
        ParkingSession.booking_id == booking.booking_id
    ).first()
    if existing_session and existing_session.status == SessionStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An active parking session is already in progress for this booking"
        )

    # Create parking session
    now = datetime.now()
    session = ParkingSession(
        booking_id=booking.booking_id,
        user_id=user.user_id,
        parking_id=booking.parking_id,
        slot_id=booking.slot_id,
        check_in=now,
        check_out=None,
        status=SessionStatus.ACTIVE
    )

    # Update booking and slot statuses
    booking.status = BookingStatus.ACTIVE
    slot = db.query(ParkingSlot).filter(ParkingSlot.slot_id == booking.slot_id).first()
    if not slot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking slot not found for this booking")
    validate_slot_status_transition(slot.status, SlotStatus.OCCUPIED)
    slot.status = SlotStatus.OCCUPIED

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def process_check_out(
    user: User, 
    check_out_in: CheckOutRequest, 
    db: Session
) -> ParkingSession:
    """
    Processes check-out for an active parking session:
    - Sets check_out timestamp
    - Transitions session -> completed, booking -> completed, slot -> available
    """
    query = db.query(ParkingSession).filter(
        ParkingSession.user_id == user.user_id,
        ParkingSession.status == SessionStatus.ACTIVE
    )

    if check_out_in.session_id:
        query = query.filter(ParkingSession.session_id == check_out_in.session_id)
    elif check_out_in.booking_id:
        query = query.filter(ParkingSession.booking_id == check_out_in.booking_id)

    session = query.with_for_update().first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active parking session found for check-out"
        )

    now = datetime.now()
    session.check_out = now
    session.status = SessionStatus.COMPLETED

    # Update booking status to completed
    booking = db.query(Booking).filter(Booking.booking_id == session.booking_id).first()
    if booking:
        booking.status = BookingStatus.COMPLETED

    # Release slot back to available
    slot = db.query(ParkingSlot).filter(ParkingSlot.slot_id == session.slot_id).first()
    if not slot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking slot not found for this session")
    validate_slot_status_transition(slot.status, SlotStatus.AVAILABLE)
    slot.status = SlotStatus.AVAILABLE

    db.commit()
    db.refresh(session)

    return session
