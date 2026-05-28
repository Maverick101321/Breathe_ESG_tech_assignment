from .common import first_value, normalize_row, parse_date, parse_decimal, read_csv


FLIGHT_EXPENSE_TYPES = {"airfare", "flight", "air"}


def normalize_class(value):
    cleaned = (value or "economy").strip().lower()
    if "business" in cleaned:
        return "business"
    if "first" in cleaned:
        return "first"
    return "economy"


def optional_decimal(value):
    if value is None or str(value).strip() == "":
        return None
    return parse_decimal(value)


def parse_travel_csv(file_obj) -> list[dict]:
    parsed_rows = []
    for index, raw_row in enumerate(read_csv(file_obj), start=2):
        row = normalize_row(raw_row)
        try:
            expense_type = first_value(row, ["Expense Type", "Category"])
            base = {
                "row_number": index,
                "raw_data": raw_row,
                "employee_id": first_value(row, ["Employee ID", "Traveler ID"]),
                "travel_date": parse_date(first_value(row, ["Transaction Date", "Travel Date", "Date"])),
                "expense_type": expense_type,
                "origin": first_value(row, ["Origin", "Origin City", "From"], ""),
                "destination": first_value(row, ["Destination", "Destination City", "To"], ""),
                "origin_iata": (first_value(row, ["Origin Airport Code", "From Airport"], "") or "").upper().strip(),
                "destination_iata": (first_value(row, ["Destination Airport Code", "To Airport"], "") or "").upper().strip(),
                "travel_class": normalize_class(first_value(row, ["Travel Class", "Cabin Class", "Class"])),
                "distance": optional_decimal(first_value(row, ["Distance"])),
                "distance_unit": (first_value(row, ["Distance Unit"], "") or "").lower(),
                "amount": optional_decimal(first_value(row, ["Amount"])),
                "currency": first_value(row, ["Currency Code"], ""),
                "vendor": first_value(row, ["Vendor Name"], ""),
            }
            if (expense_type or "").strip().lower() not in FLIGHT_EXPENSE_TYPES:
                base["parse_error"] = "non_flight_row_skipped_v1"
            parsed_rows.append(base)
        except Exception as exc:
            parsed_rows.append({"row_number": index, "raw_data": raw_row, "parse_error": str(exc)})
    return parsed_rows
