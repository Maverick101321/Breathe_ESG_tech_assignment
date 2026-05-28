import hashlib

from django.db import transaction

from ingestion.models import IngestionBatch, NormalizedEntry, RawRow
from ingestion.normalizers.sap_normalizer import normalize_sap_row
from ingestion.normalizers.travel_normalizer import normalize_travel_row
from ingestion.normalizers.utility_normalizer import normalize_utility_row
from ingestion.parsers.sap_parser import parse_sap_csv
from ingestion.parsers.travel_parser import parse_travel_csv
from ingestion.parsers.utility_parser import parse_utility_csv
from review.models import AuditLog, ReviewStatus


PARSERS = {
    IngestionBatch.SOURCE_SAP: parse_sap_csv,
    IngestionBatch.SOURCE_UTILITY: parse_utility_csv,
    IngestionBatch.SOURCE_TRAVEL: parse_travel_csv,
}

NORMALIZERS = {
    IngestionBatch.SOURCE_SAP: normalize_sap_row,
    IngestionBatch.SOURCE_UTILITY: normalize_utility_row,
    IngestionBatch.SOURCE_TRAVEL: normalize_travel_row,
}


def calculate_file_hash(file_obj):
    file_obj.seek(0)
    digest = hashlib.sha256()
    while True:
        chunk = file_obj.read(1024 * 1024)
        if not chunk:
            break
        if isinstance(chunk, str):
            chunk = chunk.encode("utf-8")
        digest.update(chunk)
    file_obj.seek(0)
    return digest.hexdigest()


def serialize_for_json(value):
    if isinstance(value, dict):
        return {key: serialize_for_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serialize_for_json(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value) if value.__class__.__name__ == "Decimal" else value


@transaction.atomic
def ingest_file(*, tenant, user, file_obj, source_type, filename=None, allow_duplicate=False):
    if source_type not in PARSERS:
        raise ValueError("Unsupported source_type")

    file_hash = calculate_file_hash(file_obj)
    if not allow_duplicate and IngestionBatch.objects.filter(tenant=tenant, file_hash=file_hash).exists():
        raise ValueError("Duplicate file for this tenant")

    batch = IngestionBatch.objects.create(
        tenant=tenant,
        uploaded_by=user,
        source_type=source_type,
        filename=filename or getattr(file_obj, "name", "upload.csv"),
        file_hash=file_hash,
        status=IngestionBatch.STATUS_PROCESSING,
    )

    parser = PARSERS[source_type]
    normalizer = NORMALIZERS[source_type]
    parsed_rows = parser(file_obj)
    error_count = 0

    for index, parsed_row in enumerate(parsed_rows, start=1):
        parse_error = parsed_row.get("parse_error")
        raw_row = RawRow.objects.create(
            tenant=tenant,
            batch=batch,
            row_number=parsed_row.get("row_number", index),
            raw_data=serialize_for_json(parsed_row.get("raw_data", parsed_row)),
            parse_error=parse_error,
        )
        if parse_error:
            error_count += 1
            continue

        normalized = normalizer(parsed_row, tenant.id)
        if normalized.get("error"):
            raw_row.parse_error = normalized["error"]
            raw_row.save(update_fields=["parse_error"])
            error_count += 1
            continue

        entry = NormalizedEntry.objects.create(
            tenant=tenant,
            raw_row=raw_row,
            batch=batch,
            **normalized,
        )
        ReviewStatus.objects.create(tenant=tenant, entry=entry, status="pending")
        AuditLog.objects.create(
            tenant=tenant,
            actor=user,
            action="uploaded",
            target_type="NormalizedEntry",
            target_id=entry.id,
            before_state=None,
            after_state=serialize_for_json(normalized),
            notes=f"Uploaded via {source_type}",
        )

    batch.row_count = len(parsed_rows)
    batch.error_count = error_count
    batch.status = IngestionBatch.STATUS_FAILED if error_count == len(parsed_rows) and parsed_rows else IngestionBatch.STATUS_COMPLETE
    batch.save(update_fields=["row_count", "error_count", "status"])
    return batch
