import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation


DATE_FORMATS = ("%d.%m.%Y", "%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y")


def read_csv(file_obj):
    file_obj.seek(0)
    raw = file_obj.read()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8-sig")
    rows = csv.DictReader(raw.splitlines())
    return list(rows)


def normalize_row(row):
    return {str(key).strip().lower(): value for key, value in row.items()}


def first_value(row, names, default=None):
    for name in names:
        value = row.get(name.strip().lower())
        if value is not None and str(value).strip() != "":
            return str(value).strip()
    return default


def parse_date(value):
    if not value:
        raise ValueError("missing date")
    cleaned = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"invalid date: {value}")


def parse_decimal(value):
    if value is None or str(value).strip() == "":
        raise ValueError("missing decimal")
    cleaned = str(value).strip().replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError(f"invalid decimal: {value}") from exc
