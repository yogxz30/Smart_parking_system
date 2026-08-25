"""Manager-facing parking location, slot, and session operations."""
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from backend.models import (
    ParkingLocation, ParkingLocationStatus, ParkingSession, ParkingSlot,
    SessionStatus, SlotStatus, SlotType,
)


SLOT_STATUS_TRANSITIONS = {
    SlotStatus.AVAILABLE: {SlotStatus.MAINTENANCE, SlotStatus.RESERVED},
    SlotStatus.RESERVED: {SlotStatus.OCCUPIED, SlotStatus.AVAILABLE},
    SlotStatus.OCCUPIED: {SlotStatus.AVAILABLE},
    SlotStatus.MAINTENANCE: {SlotStatus.AVAILABLE},
}


def _as_enum(enum_type: Any, value: Any):
    if isinstance(value, enum_type):
        return value
    try:
        return enum_type(value)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Invalid {enum_type.__name__} value: {value}")


def validate_slot_status_transition(current_status: SlotStatus, new_status: SlotStatus) -> None:
    """Reject slot state changes that are not part of the supported lifecycle."""
    current = _as_enum(SlotStatus, current_status)
    target = _as_enum(SlotStatus, new_status)
    if target not in SLOT_STATUS_TRANSITIONS[current]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(f"Invalid slot status transition: {current.value} -> {target.value}. "
                    "Allowed transitions are available->maintenance/reserved, "
                    "reserved->occupied/available, occupied->available, and "
                    "maintenance->available."),
        )


def create_parking_location(db: Session, **fields: Any) -> ParkingLocation:
    location = ParkingLocation(**fields)
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


def update_parking_location(parking_id: int, db: Session, **fields: Any) -> ParkingLocation:
    location = db.query(ParkingLocation).filter(ParkingLocation.parking_id == parking_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking facility not found")
    for field, value in fields.items():
        setattr(location, field, value)
    db.commit()
    db.refresh(location)
    return location


def set_parking_active_status(parking_id: int, is_active: bool, db: Session) -> ParkingLocation:
    return update_parking_location(
        parking_id, db, status=ParkingLocationStatus.ACTIVE if is_active else ParkingLocationStatus.INACTIVE
    )


def create_slot(parking_id: int, slot_number: str, slot_type: str, db: Session) -> ParkingSlot:
    location = db.query(ParkingLocation).filter(ParkingLocation.parking_id == parking_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking facility not found")
    slot = ParkingSlot(
        parking_id=parking_id,
        slot_number=slot_number.strip(),
        slot_type=_as_enum(SlotType, slot_type),
        status=SlotStatus.AVAILABLE,
    )
    db.add(slot)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="A slot with this number already exists at this parking facility")
    location.total_slots += 1
    db.commit()
    db.refresh(slot)
    return slot


def update_slot_status(slot_id: int, new_status: str, actor_role: str, db: Session) -> ParkingSlot:
    if str(getattr(actor_role, "value", actor_role)).lower() not in {"manager", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Manager or admin role is required to update slot status")
    slot = db.query(ParkingSlot).filter(ParkingSlot.slot_id == slot_id).with_for_update().first()
    if not slot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking slot not found")
    target = _as_enum(SlotStatus, new_status)
    validate_slot_status_transition(slot.status, target)
    slot.status = target
    db.commit()
    db.refresh(slot)
    return slot


def get_all_active_sessions(db: Session):
    return db.query(ParkingSession).options(
        joinedload(ParkingSession.parking), joinedload(ParkingSession.slot)
    ).filter(ParkingSession.status == SessionStatus.ACTIVE).order_by(ParkingSession.check_in.desc()).all()
