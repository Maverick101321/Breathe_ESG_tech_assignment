from .common import first_value, normalize_row, parse_date, parse_decimal, read_csv


CONSUMPTION_MOVEMENT_TYPES = {"261", "201", "551"}


def parse_sap_csv(file_obj) -> list[dict]:
    parsed_rows = []
    for index, raw_row in enumerate(read_csv(file_obj), start=2):
        row = normalize_row(raw_row)
        try:
            movement_type = first_value(row, ["Movement Type", "Bewegungsart"])
            if movement_type not in CONSUMPTION_MOVEMENT_TYPES:
                continue
            parsed_rows.append(
                {
                    "row_number": index,
                    "raw_data": raw_row,
                    "posting_date": parse_date(first_value(row, ["Posting Date", "Buchungsdatum"])),
                    "plant_code": first_value(row, ["Plant", "Werk"]),
                    "material_code": first_value(row, ["Material"]),
                    "movement_type": movement_type,
                    "quantity": parse_decimal(first_value(row, ["Quantity", "Menge"])),
                    "uom": first_value(row, ["Base Unit of Measure", "Basismengeneinheit"]),
                    "cost_center": first_value(row, ["Cost Center"], ""),
                    "vendor": first_value(row, ["Vendor"], ""),
                }
            )
        except Exception as exc:
            parsed_rows.append({"row_number": index, "raw_data": raw_row, "parse_error": str(exc)})
    return parsed_rows
