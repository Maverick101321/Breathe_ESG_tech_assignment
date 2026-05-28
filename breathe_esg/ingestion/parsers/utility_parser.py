from decimal import Decimal

from .common import first_value, normalize_row, parse_date, parse_decimal, read_csv


def parse_utility_csv(file_obj) -> list[dict]:
    parsed_rows = []
    for index, raw_row in enumerate(read_csv(file_obj), start=2):
        row = normalize_row(raw_row)
        try:
            consumption = parse_decimal(first_value(row, ["Units Consumed", "Consumption", "kWh"]))
            uom = first_value(row, ["Unit", "UOM"], "kWh")
            if uom and uom.strip().lower() == "mwh":
                consumption *= Decimal("1000")
                uom = "kWh"
            parsed_rows.append(
                {
                    "row_number": index,
                    "raw_data": raw_row,
                    "meter_id": first_value(row, ["Consumer Number", "Meter ID", "Account Number"]),
                    "period_start": parse_date(first_value(row, ["Billing Period From", "Period Start"])),
                    "period_end": parse_date(first_value(row, ["Billing Period To", "Period End"])),
                    "consumption_kwh": consumption,
                    "site_name": first_value(row, ["Site Name", "Location"], ""),
                    "tariff_code": first_value(row, ["Tariff Category", "Tariff Code"], ""),
                }
            )
        except Exception as exc:
            parsed_rows.append({"row_number": index, "raw_data": raw_row, "parse_error": str(exc)})
    return parsed_rows
