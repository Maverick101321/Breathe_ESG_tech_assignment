from decimal import Decimal
from math import asin, cos, radians, sin, sqrt


AIRPORT_COORDS = {
    "BOM": (19.0896, 72.8656),
    "DEL": (28.5562, 77.1000),
    "BLR": (13.1986, 77.7066),
    "MAA": (12.9941, 80.1709),
    "HYD": (17.2313, 78.4298),
    "CCU": (22.6520, 88.4463),
    "LHR": (51.4700, -0.4543),
    "CDG": (49.0097, 2.5479),
    "DXB": (25.2532, 55.3657),
    "SIN": (1.3644, 103.9915),
    "JFK": (40.6413, -73.7781),
    "ORD": (41.9742, -87.9073),
    "LAX": (33.9425, -118.4081),
    "NRT": (35.7720, 140.3929),
    "SYD": (-33.9399, 151.1753),
    "AMS": (52.3105, 4.7683),
    "FRA": (50.0379, 8.5622),
    "DOH": (25.2731, 51.6081),
    "HKG": (22.3080, 113.9185),
    "ICN": (37.4602, 126.4407),
}

CABIN_FACTORS = {
    "economy": Decimal("0.255"),
    "business": Decimal("0.617"),
    "first": Decimal("0.870"),
}

RFI_MULTIPLIER = Decimal("1.9")
ROUTING_UPLIFT = Decimal("1.1")


def haversine_km(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius_km = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return Decimal(str(2 * radius_km * asin(sqrt(a))))


def normalize_travel_row(parsed_row: dict, tenant_id) -> dict:
    origin_iata = parsed_row.get("origin_iata")
    destination_iata = parsed_row.get("destination_iata")
    distance = parsed_row.get("distance")
    if distance is None:
        if origin_iata not in AIRPORT_COORDS or destination_iata not in AIRPORT_COORDS:
            return {"error": "unknown_airport_code"}
        distance_km = haversine_km(AIRPORT_COORDS[origin_iata], AIRPORT_COORDS[destination_iata])
    else:
        distance_km = distance
        if (parsed_row.get("distance_unit") or "").lower() == "miles":
            distance_km *= Decimal("1.60934")

    distance_km = distance_km * ROUTING_UPLIFT
    travel_class = parsed_row.get("travel_class")
    if travel_class not in CABIN_FACTORS:
        travel_class = "economy"
    factor = CABIN_FACTORS[travel_class]
    return {
        "scope": "scope_3",
        "category": f"flight_{travel_class}",
        "activity_date": parsed_row["travel_date"],
        "description": f"Flight {origin_iata}\u2192{destination_iata} ({travel_class})",
        "original_value": parsed_row.get("distance") or distance_km,
        "original_unit": parsed_row.get("distance_unit") or "km",
        "normalized_value": distance_km,
        "normalized_unit": "km",
        "co2e_kg": distance_km * factor * RFI_MULTIPLIER,
        "emission_factor": factor,
        "emission_factor_source": "DEFRA_2023_RFI",
        "source_location": f"{origin_iata} \u2192 {destination_iata}",
    }
