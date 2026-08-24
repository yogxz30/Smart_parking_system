import math
from typing import Dict, Tuple, Optional, List


# Standard landmark center coordinates for major Chennai areas
CHENNAI_AREAS: Dict[str, Tuple[float, float]] = {
    "Guindy": (13.0067000, 80.2026000),
    "Tambaram": (12.9249000, 80.1180000),
    "T Nagar": (13.0418000, 80.2341000),
    "Anna Nagar": (13.0850000, 80.2101000),
    "Velachery": (12.9815000, 80.2180000),
    "Adyar": (13.0012000, 80.2565000),
    "Mylapore": (13.0368000, 80.2676000),
    "Nungambakkam": (13.0569000, 80.2425000),
    "Egmore": (13.0732000, 80.2609000),
    "Porur": (13.0382000, 80.1565000),
    "Chromepet": (12.9516000, 80.1462000),
    "OMR - Thoraipakkam": (12.9372000, 80.2333000),
    "OMR - Sholinganallur": (12.9010000, 80.2279000)
}


def get_available_areas() -> List[str]:
    """Return the list of all supported named areas."""
    return list(CHENNAI_AREAS.keys())


def get_area_coordinates(area_name: str) -> Optional[Tuple[float, float]]:
    """
    Lookup latitude and longitude for a given area name.
    Supports case-insensitive matching.
    """
    if not area_name:
        return None
        
    cleaned_name = area_name.strip().lower()
    for name, coords in CHENNAI_AREAS.items():
        if name.lower() == cleaned_name:
            return coords
            
    # Partial substring match fallback
    for name, coords in CHENNAI_AREAS.items():
        if cleaned_name in name.lower() or name.lower() in cleaned_name:
            return coords
            
    return None


def calculate_distance_km(
    lat1: Optional[float], 
    lon1: Optional[float], 
    lat2: Optional[float], 
    lon2: Optional[float]
) -> Optional[float]:
    """
    Calculate the great-circle distance between two geographic coordinates
    using the standard Haversine formula. Returns distance in kilometers (km).
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return None

    # Earth radius in kilometers
    R = 6371.0

    # Convert degrees to radians
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    delta_phi = math.radians(float(lat2) - float(lat1))
    delta_lambda = math.radians(float(lon2) - float(lon1))

    # Haversine formula
    a = (
        math.sin(delta_phi / 2.0) ** 2 +
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    distance = R * c

    return round(distance, 2)
