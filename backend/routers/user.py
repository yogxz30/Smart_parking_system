from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.database import get_db
from backend.models import (
    User, ParkingLocation, ParkingSlot, Booking, Favorite,
    ParkingLocationStatus, SlotStatus, BookingStatus
)
from backend.schemas import (
    UserResponse, UserDashboardResponse, UserDashboardStats, BookingResponse,
    FavoriteResponse, UserProfileUpdate, ChangePasswordRequest
)
from backend.services.auth_service import get_current_user, hash_password, verify_password

router = APIRouter(prefix="/api/user", tags=["User Profile & Dashboard"])


@router.get("/profile", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """
    Retrieve current logged-in user's profile details.
    """
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    profile_in: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the authenticated user's name and/or phone number.
    Only non-None provided fields are updated.
    """
    if profile_in.name is not None:
        name_stripped = profile_in.name.strip()
        if len(name_stripped) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name must be at least 2 characters long"
            )
        current_user.name = name_stripped

    if profile_in.phone is not None:
        phone_stripped = profile_in.phone.strip()
        # Basic phone validation: allow digits, spaces, +, -, ()
        import re
        if phone_stripped and not re.match(r'^[\d\s\+\-\(\)]{7,20}$', phone_stripped):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format"
            )
        current_user.phone = phone_stripped if phone_stripped else None

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    pw_in: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change the authenticated user's password.
    Validates current password, checks new vs confirm match, then updates using bcrypt.
    """
    # 1. Verify current password
    if not verify_password(pw_in.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # 2. Ensure new password and confirm match
    if pw_in.new_password != pw_in.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation do not match"
        )

    # 3. Ensure new password is different
    if pw_in.current_password == pw_in.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password"
        )

    # 4. Hash and save
    current_user.password = hash_password(pw_in.new_password)
    db.commit()

    return {"message": "Password changed successfully"}


@router.get("/dashboard", response_model=UserDashboardResponse)
def get_user_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve real-time metrics, active booking, and recent booking history
    for the authenticated user's dashboard.
    """
    # 1. Nearby / Total active parking locations count
    nearby_parking_count = db.query(func.count(ParkingLocation.parking_id)).filter(
        ParkingLocation.status == ParkingLocationStatus.ACTIVE
    ).scalar() or 0

    # 2. Total available slots across active facilities
    available_slots_count = db.query(func.count(ParkingSlot.slot_id)).join(
        ParkingLocation, ParkingSlot.parking_id == ParkingLocation.parking_id
    ).filter(
        ParkingLocation.status == ParkingLocationStatus.ACTIVE,
        ParkingSlot.status == SlotStatus.AVAILABLE
    ).scalar() or 0

    # 3. Active bookings count for current user (reserved or active)
    active_bookings_count = db.query(func.count(Booking.booking_id)).filter(
        Booking.user_id == current_user.user_id,
        Booking.status.in_([BookingStatus.RESERVED, BookingStatus.ACTIVE])
    ).scalar() or 0

    # 4. User's latest active/reserved booking
    active_booking_model = db.query(Booking).filter(
        Booking.user_id == current_user.user_id,
        Booking.status.in_([BookingStatus.RESERVED, BookingStatus.ACTIVE])
    ).order_by(desc(Booking.created_at)).first()

    active_booking_response = None
    if active_booking_model:
        active_booking_response = BookingResponse(
            booking_id=active_booking_model.booking_id,
            user_id=active_booking_model.user_id,
            parking_id=active_booking_model.parking_id,
            parking_name=active_booking_model.parking.parking_name if active_booking_model.parking else None,
            area=active_booking_model.parking.area if active_booking_model.parking else None,
            slot_id=active_booking_model.slot_id,
            slot_number=active_booking_model.slot.slot_number if active_booking_model.slot else None,
            booking_date=active_booking_model.booking_date,
            start_time=active_booking_model.start_time,
            end_time=active_booking_model.end_time,
            status=active_booking_model.status.value if hasattr(active_booking_model.status, "value") else str(active_booking_model.status),
            created_at=active_booking_model.created_at
        )

    # 5. User's recent bookings (last 5)
    recent_booking_models = db.query(Booking).filter(
        Booking.user_id == current_user.user_id
    ).order_by(desc(Booking.created_at)).limit(5).all()

    recent_bookings_response = [
        BookingResponse(
            booking_id=b.booking_id,
            user_id=b.user_id,
            parking_id=b.parking_id,
            parking_name=b.parking.parking_name if b.parking else None,
            area=b.parking.area if b.parking else None,
            slot_id=b.slot_id,
            slot_number=b.slot.slot_number if b.slot else None,
            booking_date=b.booking_date,
            start_time=b.start_time,
            end_time=b.end_time,
            status=b.status.value if hasattr(b.status, "value") else str(b.status),
            created_at=b.created_at
        )
        for b in recent_booking_models
    ]

    return UserDashboardResponse(
        user=UserResponse(
            user_id=current_user.user_id,
            name=current_user.name,
            email=current_user.email,
            phone=current_user.phone,
            role=current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role),
            status=current_user.status.value if hasattr(current_user.status, "value") else str(current_user.status),
            created_at=current_user.created_at
        ),
        stats=UserDashboardStats(
            nearby_parking_count=nearby_parking_count,
            available_slots_count=available_slots_count,
            active_bookings_count=active_bookings_count
        ),
        active_booking=active_booking_response,
        recent_bookings=recent_bookings_response
    )


# ==============================================================================
# Favorites Endpoints
# ==============================================================================

@router.get("/favorites", response_model=List[FavoriteResponse])
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all parking locations saved as favorites by the authenticated user.
    """
    favs = db.query(Favorite).filter(
        Favorite.user_id == current_user.user_id
    ).order_by(desc(Favorite.created_at)).all()

    return [
        FavoriteResponse(
            favorite_id=f.favorite_id,
            user_id=f.user_id,
            parking_id=f.parking_id,
            parking_name=f.parking.parking_name if f.parking else None,
            area=f.parking.area if f.parking else None,
            parking_fee=float(f.parking.parking_fee) if f.parking else None,
            ev_available=f.parking.ev_available if f.parking else None,
            accessible_available=f.parking.accessible_available if f.parking else None,
            created_at=f.created_at
        )
        for f in favs
    ]


@router.post("/favorites", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
    parking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a parking location to the authenticated user's favorites.
    Returns 409 if already favorited.
    """
    # Check parking exists
    parking = db.query(ParkingLocation).filter(
        ParkingLocation.parking_id == parking_id
    ).first()
    if not parking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking location not found"
        )

    # Check already favorited
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.user_id,
        Favorite.parking_id == parking_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This parking location is already in your favorites"
        )

    fav = Favorite(user_id=current_user.user_id, parking_id=parking_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)

    return FavoriteResponse(
        favorite_id=fav.favorite_id,
        user_id=fav.user_id,
        parking_id=fav.parking_id,
        parking_name=parking.parking_name,
        area=parking.area,
        parking_fee=float(parking.parking_fee),
        ev_available=parking.ev_available,
        accessible_available=parking.accessible_available,
        created_at=fav.created_at
    )


@router.delete("/favorites/{parking_id}", status_code=status.HTTP_200_OK)
def remove_favorite(
    parking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a parking location from the authenticated user's favorites.
    """
    fav = db.query(Favorite).filter(
        Favorite.user_id == current_user.user_id,
        Favorite.parking_id == parking_id
    ).first()

    if not fav:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )

    db.delete(fav)
    db.commit()

    return {"message": "Removed from favorites"}
