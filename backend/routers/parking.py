from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models import ParkingLocation, ParkingSlot, ParkingLocationStatus, SlotStatus, User, UserRole, ParkingSession
from backend.schemas import (
    ParkingLocationResponse, ParkingDetailResponse, ParkingSlotResponse, SessionResponse,
    ParkingLocationCreate, ParkingLocationUpdate, ParkingActiveStatusUpdate,
    ParkingSlotCreate, SlotStatusUpdate,
)
from backend.services.location_service import get_area_coordinates, calculate_distance_km, get_available_areas
from backend.services.auth_service import get_current_user
from backend.services.parking_service import (
    create_parking_location, update_parking_location, set_parking_active_status,
    create_slot, update_slot_status, get_all_active_sessions,
)

router = APIRouter(prefix="/api/parking", tags=["Parking Facilities"])
slots_router = APIRouter(prefix="/api/slots", tags=["Parking Management"])
sessions_router = APIRouter(prefix="/api/sessions", tags=["Parking Management"])


def require_manager_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Allow management operations only for active manager or admin accounts."""
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role.lower() not in {UserRole.MANAGER.value, UserRole.ADMIN.value}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or admin role is required for this operation",
        )
    return current_user


def _location_response(loc: ParkingLocation, db: Session) -> ParkingLocationResponse:
    available_slots = db.query(func.count(ParkingSlot.slot_id)).filter(
        ParkingSlot.parking_id == loc.parking_id,
        ParkingSlot.status == SlotStatus.AVAILABLE,
    ).scalar() or 0
    return ParkingLocationResponse(
        parking_id=loc.parking_id, parking_name=loc.parking_name, area=loc.area,
        address=loc.address, latitude=float(loc.latitude) if loc.latitude is not None else None,
        longitude=float(loc.longitude) if loc.longitude is not None else None,
        total_slots=loc.total_slots, available_slots=available_slots, parking_fee=float(loc.parking_fee),
        opening_time=str(loc.opening_time) if loc.opening_time else None,
        closing_time=str(loc.closing_time) if loc.closing_time else None,
        ev_available=loc.ev_available, accessible_available=loc.accessible_available,
        status=loc.status.value if hasattr(loc.status, "value") else str(loc.status),
    )


def _session_response(session: ParkingSession) -> SessionResponse:
    return SessionResponse(
        session_id=session.session_id, booking_id=session.booking_id, user_id=session.user_id,
        parking_id=session.parking_id,
        parking_name=session.parking.parking_name if session.parking else None,
        slot_id=session.slot_id, slot_number=session.slot.slot_number if session.slot else None,
        check_in=session.check_in, check_out=session.check_out,
        status=session.status.value if hasattr(session.status, "value") else str(session.status),
    )


@router.get("/areas", response_model=List[str])
def list_supported_areas():
    """Return the list of standard named areas with coordinate mappings."""
    return get_available_areas()


@router.get("", response_model=List[ParkingLocationResponse])
def search_parking_locations(
    area: Optional[str] = Query(None, description="Search by area name (e.g., Guindy, Tambaram, T Nagar)"),
    ev_only: Optional[bool] = Query(None, description="Filter for EV charging availability"),
    accessible_only: Optional[bool] = Query(None, description="Filter for accessible parking"),
    sort_by: Optional[str] = Query(None, description="Sort results: 'fee_asc' (cheapest first), 'fee_desc' (most expensive first), 'nearest' (default when area given)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve active parking facilities. If an area name is provided,
    filters/sorts by geographic proximity and calculates distance in km.
    Supports optional sort_by: 'fee_asc', 'fee_desc', or default (nearest/name).
    """
    query = db.query(ParkingLocation).filter(ParkingLocation.status == ParkingLocationStatus.ACTIVE)

    if ev_only:
        query = query.filter(ParkingLocation.ev_available.is_(True))
    if accessible_only:
        query = query.filter(ParkingLocation.accessible_available.is_(True))

    locations = query.all()

    # Obtain center coordinates of selected area if specified
    area_coords = get_area_coordinates(area) if area else None

    # Calculate available slots count for each location
    results = []
    for loc in locations:
        available_slots_count = db.query(func.count(ParkingSlot.slot_id)).filter(
            ParkingSlot.parking_id == loc.parking_id,
            ParkingSlot.status == SlotStatus.AVAILABLE
        ).scalar() or 0

        # Calculate distance
        distance_km = None
        if area_coords and loc.latitude is not None and loc.longitude is not None:
            distance_km = calculate_distance_km(
                area_coords[0], area_coords[1],
                float(loc.latitude), float(loc.longitude)
            )

        # If user searched for a specific area name and it's not a coordinate match,
        # prioritize matches where area name directly matches
        matches_area_name = area.strip().lower() in loc.area.lower() if area else True

        loc_dict = {
            "parking_id": loc.parking_id,
            "parking_name": loc.parking_name,
            "area": loc.area,
            "address": loc.address,
            "latitude": float(loc.latitude) if loc.latitude is not None else None,
            "longitude": float(loc.longitude) if loc.longitude is not None else None,
            "total_slots": loc.total_slots,
            "available_slots": available_slots_count,
            "parking_fee": float(loc.parking_fee),
            "opening_time": str(loc.opening_time) if loc.opening_time else None,
            "closing_time": str(loc.closing_time) if loc.closing_time else None,
            "ev_available": loc.ev_available,
            "accessible_available": loc.accessible_available,
            "status": loc.status.value if hasattr(loc.status, "value") else str(loc.status),
            "distance_km": distance_km
        }

        # If area search filter is applied, include matching area or nearby locations
        if area:
            if matches_area_name or (distance_km is not None and distance_km <= 15.0):
                results.append(loc_dict)
        else:
            results.append(loc_dict)

    # Sort results based on sort_by param
    if sort_by == "fee_asc":
        results.sort(key=lambda x: x["parking_fee"])
    elif sort_by == "fee_desc":
        results.sort(key=lambda x: x["parking_fee"], reverse=True)
    elif area_coords:
        # Default: nearest first when area is given
        results.sort(key=lambda x: (x["distance_km"] if x["distance_km"] is not None else 9999))
    else:
        # Default: alphabetical by name
        results.sort(key=lambda x: x["parking_name"])

    return results


@router.get("/management/all", response_model=List[ParkingLocationResponse])
def list_all_parking_locations_for_management(
    _: User = Depends(require_manager_or_admin), db: Session = Depends(get_db)
):
    """Return active and inactive facilities for the management interface."""
    locations = db.query(ParkingLocation).order_by(ParkingLocation.parking_name).all()
    return [_location_response(location, db) for location in locations]


@router.get("/{parking_id}", response_model=ParkingDetailResponse)
def get_parking_details(parking_id: int, db: Session = Depends(get_db)):
    """
    Retrieve full details of a specific parking facility, including its slots.
    """
    loc = db.query(ParkingLocation).filter(ParkingLocation.parking_id == parking_id).first()
    if not loc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parking facility with ID {parking_id} not found"
        )

    slots = db.query(ParkingSlot).filter(ParkingSlot.parking_id == parking_id).all()
    available_slots_count = sum(1 for s in slots if s.status == SlotStatus.AVAILABLE)

    slot_responses = [
        ParkingSlotResponse(
            slot_id=s.slot_id,
            parking_id=s.parking_id,
            slot_number=s.slot_number,
            slot_type=s.slot_type.value if hasattr(s.slot_type, "value") else str(s.slot_type),
            status=s.status.value if hasattr(s.status, "value") else str(s.status)
        )
        for s in slots
    ]

    return ParkingDetailResponse(
        parking_id=loc.parking_id,
        parking_name=loc.parking_name,
        area=loc.area,
        address=loc.address,
        latitude=float(loc.latitude) if loc.latitude is not None else None,
        longitude=float(loc.longitude) if loc.longitude is not None else None,
        total_slots=loc.total_slots,
        available_slots=available_slots_count,
        parking_fee=float(loc.parking_fee),
        opening_time=str(loc.opening_time) if loc.opening_time else None,
        closing_time=str(loc.closing_time) if loc.closing_time else None,
        ev_available=loc.ev_available,
        accessible_available=loc.accessible_available,
        status=loc.status.value if hasattr(loc.status, "value") else str(loc.status),
        slots=slot_responses
    )


@router.get("/{parking_id}/slots", response_model=List[ParkingSlotResponse])
def get_parking_slots(parking_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all parking slots for a specific facility.
    """
    loc = db.query(ParkingLocation).filter(ParkingLocation.parking_id == parking_id).first()
    if not loc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parking facility with ID {parking_id} not found"
        )

    slots = db.query(ParkingSlot).filter(ParkingSlot.parking_id == parking_id).all()
    return [
        ParkingSlotResponse(
            slot_id=s.slot_id,
            parking_id=s.parking_id,
            slot_number=s.slot_number,
            slot_type=s.slot_type.value if hasattr(s.slot_type, "value") else str(s.slot_type),
            status=s.status.value if hasattr(s.status, "value") else str(s.status)
        )
        for s in slots
    ]


@router.post("", response_model=ParkingLocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    location_in: ParkingLocationCreate,
    _: User = Depends(require_manager_or_admin),
    db: Session = Depends(get_db),
):
    location = create_parking_location(db, **location_in.model_dump())
    return _location_response(location, db)


@router.put("/{parking_id}", response_model=ParkingLocationResponse)
def update_location(
    parking_id: int,
    location_in: ParkingLocationUpdate,
    _: User = Depends(require_manager_or_admin),
    db: Session = Depends(get_db),
):
    location = update_parking_location(parking_id, db, **location_in.model_dump(exclude_unset=True))
    return _location_response(location, db)


@router.put("/{parking_id}/status", response_model=ParkingLocationResponse)
def update_location_status(
    parking_id: int,
    status_in: ParkingActiveStatusUpdate,
    _: User = Depends(require_manager_or_admin),
    db: Session = Depends(get_db),
):
    location = set_parking_active_status(parking_id, status_in.is_active, db)
    return _location_response(location, db)


@slots_router.post("", response_model=ParkingSlotResponse, status_code=status.HTTP_201_CREATED)
def create_parking_slot(
    slot_in: ParkingSlotCreate,
    _: User = Depends(require_manager_or_admin),
    db: Session = Depends(get_db),
):
    slot = create_slot(slot_in.parking_id, slot_in.slot_number, slot_in.slot_type, db)
    return ParkingSlotResponse(
        slot_id=slot.slot_id, parking_id=slot.parking_id, slot_number=slot.slot_number,
        slot_type=slot.slot_type.value if hasattr(slot.slot_type, "value") else str(slot.slot_type),
        status=slot.status.value if hasattr(slot.status, "value") else str(slot.status),
    )


@slots_router.put("/{slot_id}/status", response_model=ParkingSlotResponse)
def set_slot_status(
    slot_id: int,
    status_in: SlotStatusUpdate,
    current_user: User = Depends(require_manager_or_admin),
    db: Session = Depends(get_db),
):
    slot = update_slot_status(slot_id, status_in.status, current_user.role, db)
    return ParkingSlotResponse(
        slot_id=slot.slot_id, parking_id=slot.parking_id, slot_number=slot.slot_number,
        slot_type=slot.slot_type.value if hasattr(slot.slot_type, "value") else str(slot.slot_type),
        status=slot.status.value if hasattr(slot.status, "value") else str(slot.status),
    )


@sessions_router.get("/all", response_model=List[SessionResponse])
def list_all_active_sessions(
    _: User = Depends(require_manager_or_admin), db: Session = Depends(get_db)
):
    return [_session_response(session) for session in get_all_active_sessions(db)]


@sessions_router.get("/{session_id}", response_model=SessionResponse)
def get_session_detail(
    session_id: int,
    _: User = Depends(require_manager_or_admin), db: Session = Depends(get_db)
):
    session = db.query(ParkingSession).filter(ParkingSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking session not found")
    return _session_response(session)
