from decimal import Decimal


EMISSION_FACTOR = Decimal("0.82")
FACTOR_SOURCE = "CEA_2023_INDIA_GRID"


def normalize_utility_row(parsed_row: dict, tenant_id) -> dict:
    consumption_kwh = parsed_row["consumption_kwh"]
    meter_id = parsed_row["meter_id"]
    period_start = parsed_row["period_start"]
    period_end = parsed_row["period_end"]
    return {
        "scope": "scope_2",
        "category": "electricity_grid",
        "activity_date": period_start,
        "description": f"Grid electricity at meter {meter_id} ({period_start} to {period_end})",
        "original_value": consumption_kwh,
        "original_unit": "kWh",
        "normalized_value": consumption_kwh,
        "normalized_unit": "kWh",
        "co2e_kg": consumption_kwh * EMISSION_FACTOR,
        "emission_factor": EMISSION_FACTOR,
        "emission_factor_source": FACTOR_SOURCE,
        "source_location": meter_id,
    }
