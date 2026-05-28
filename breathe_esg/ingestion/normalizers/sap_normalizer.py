from decimal import Decimal


PLANT_LOCATIONS = {
    "IN01": "Mumbai Plant",
    "IN02": "Bangalore Plant",
    "IN03": "Chennai Plant",
    "DE01": "Frankfurt Plant",
    "US01": "Houston Plant",
}

MATERIAL_FUEL_MAP = {
    "DIESEL": {"fuel_type": "diesel", "factor": Decimal("2.68"), "factor_source": "DEFRA_2023"},
    "HSD": {"fuel_type": "diesel", "factor": Decimal("2.68"), "factor_source": "DEFRA_2023"},
    "PETROL": {"fuel_type": "petrol", "factor": Decimal("2.31"), "factor_source": "DEFRA_2023"},
    "MS": {"fuel_type": "petrol", "factor": Decimal("2.31"), "factor_source": "DEFRA_2023"},
    "LPG": {"fuel_type": "lpg", "factor": Decimal("1.56"), "factor_source": "DEFRA_2023"},
    "CNG": {"fuel_type": "cng", "factor": Decimal("2.04"), "factor_source": "DEFRA_2023"},
}

UOM_TO_LITRES = {
    "L": Decimal("1.0"),
    "LTR": Decimal("1.0"),
    "GAL": Decimal("3.785"),
    "GALON": Decimal("3.785"),
    "M3": Decimal("1000.0"),
    "KG": None,
}


def normalize_sap_row(parsed_row: dict, tenant_id) -> dict:
    material_code = (parsed_row.get("material_code") or "").upper()
    fuel = next((value for key, value in MATERIAL_FUEL_MAP.items() if key in material_code), None)
    if not fuel:
        return {"error": "unknown_material_fuel_type"}

    uom = (parsed_row.get("uom") or "").upper()
    if uom not in UOM_TO_LITRES:
        return {"error": f"unsupported_uom:{uom}"}

    quantity = parsed_row["quantity"]
    if uom == "KG":
        normalized_value = quantity / Decimal("0.54")
    else:
        normalized_value = quantity * UOM_TO_LITRES[uom]

    source_location = PLANT_LOCATIONS.get(parsed_row["plant_code"], parsed_row["plant_code"])
    fuel_type = fuel["fuel_type"]
    co2e_kg = normalized_value * fuel["factor"]
    return {
        "scope": "scope_1",
        "category": f"fuel_{fuel_type}",
        "activity_date": parsed_row["posting_date"],
        "description": f"{fuel_type.title()} consumption at {source_location}",
        "original_value": quantity,
        "original_unit": parsed_row["uom"],
        "normalized_value": normalized_value,
        "normalized_unit": "litres",
        "co2e_kg": co2e_kg,
        "emission_factor": fuel["factor"],
        "emission_factor_source": fuel["factor_source"],
        "source_location": source_location,
    }
