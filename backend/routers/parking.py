from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models import ParkingLocation, ParkingSlot, ParkingLocationStatus, SlotStatus
from backend.schemas import ParkingLocationResponse, ParkingDetailResponse, ParkingSlotResponse
from backend.services.location_service import get_area_coordinates, calculate_distance_km, get_available_areas

router = APIRouter(prefix="/api/parking", tags=["Parking Facilities"])


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
