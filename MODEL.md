# MODEL.md — Data Model & Design Rationale

## Overview

This document describes the data model for the Breathe ESG ingestion and review platform. The model is designed around four non-negotiable requirements: multi-tenancy, Scope 1/2/3 classification, source-of-truth tracking, and a complete audit trail. Every design decision below is explained in terms of the problem it solves.

---

## Core Design Principles

**Immutability of raw data.** Whatever comes in from a client file is never mutated. The `RawRow` table stores the original record exactly as parsed. All normalization happens in a separate table. If our normalization logic was wrong, we can re-derive `NormalizedEntry` from `RawRow` without asking the client for the file again.

**Source-of-truth traceability.** Every normalized entry knows which batch it came from, which file, which tenant uploaded it, and when. If an analyst edits a value, the original is preserved and the edit is logged.

**Approval as a state machine.** Rows move through: `pending → flagged → approved / rejected`. Once approved, the row is locked — no further edits. This matches what auditors require.

**Unit normalization at write time.** Raw values (gallons, kWh, miles, MJ) are converted to a canonical unit (kWh for energy, kg CO₂e for emissions) when the `NormalizedEntry` is created. The original value and unit are always stored alongside.

---

## Entity Relationship Summary

```
Tenant
  └── IngestionBatch (one per file upload)
        └── RawRow (one per CSV row, immutable)
              └── NormalizedEntry (one per RawRow, mutable pre-approval)
                    └── ReviewStatus (current state)
                    └── AuditLog (all state transitions)
```

---

## Table Definitions

### 1. `Tenant`

Represents a client company onboarded to the platform.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `name` | VARCHAR(255) | Company name |
| `slug` | VARCHAR(100) | URL-safe identifier |
| `created_at` | TIMESTAMPTZ | |
| `is_active` | BOOLEAN | Soft-disable without deleting |

**Why UUID PK?** Sequential integer IDs leak row counts across tenants. UUIDs are safe to expose in URLs and APIs.

**Multi-tenancy approach:** Row-level isolation. Every table below carries a `tenant_id` FK. No shared schemas, no separate databases (overkill for a prototype). All Django querysets are filtered by `tenant_id` at the view layer; a middleware injects the tenant from the authenticated user's session.

---

### 2. `User`

Extends Django's `AbstractUser`. Scoped to a tenant.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `tenant_id` | FK → Tenant | |
| `email` | VARCHAR | Login identifier |
| `role` | ENUM | `analyst`, `admin` |
| `created_at` | TIMESTAMPTZ | |

**Roles:** `admin` can upload and manage; `analyst` can review, approve, flag, reject. Kept simple — no RBAC complexity for a prototype.

---

### 3. `IngestionBatch`

One record per file upload. Groups all rows from a single upload event.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `tenant_id` | FK → Tenant | |
| `uploaded_by` | FK → User | |
| `source_type` | ENUM | `sap_fuel_procurement`, `utility_electricity`, `corporate_travel` |
| `filename` | VARCHAR(255) | Original filename as uploaded |
| `file_hash` | VARCHAR(64) | SHA-256 of raw file — detect duplicate uploads |
| `uploaded_at` | TIMESTAMPTZ | |
| `row_count` | INTEGER | Total rows parsed |
| `error_count` | INTEGER | Rows that failed parsing |
| `status` | ENUM | `processing`, `complete`, `failed` |

**Why file_hash?** Prevents the same file being uploaded twice — common mistake by facilities teams re-sending last month's export.

**source_type enum** drives which parser runs and which Scope category is assigned.

---

### 4. `RawRow`

Immutable. Stores one parsed row from the source CSV exactly as it appeared, serialized to JSON. Never updated after creation.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `tenant_id` | FK → Tenant | |
| `batch_id` | FK → IngestionBatch | |
| `row_number` | INTEGER | Line number in source file |
| `raw_data` | JSONB | Full original row as key-value pairs |
| `parse_error` | TEXT | Null if parsed OK; error message if not |
| `created_at` | TIMESTAMPTZ | |

**Why JSONB?** Each source has a different shape. SAP CSVs have plant codes and German headers; Concur exports have merchant names and cost centers. Storing raw_data as JSONB means we don't need a separate schema per source type, and we can always inspect what we received.

**parse_error rows** still get a `RawRow` record — this is how we surface "what failed" in the analyst dashboard.

---

### 5. `NormalizedEntry`

The cleaned, unit-normalized, Scope-classified version of a `RawRow`. This is what analysts review and what goes to auditors.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `tenant_id` | FK → Tenant | |
| `raw_row_id` | FK → RawRow | One-to-one |
| `batch_id` | FK → IngestionBatch | Denormalized for query convenience |
| `scope` | ENUM | `scope_1`, `scope_2`, `scope_3` |
| `category` | VARCHAR(100) | e.g. `fuel_diesel`, `electricity_grid`, `flight_long_haul` |
| `activity_date` | DATE | When the activity occurred (not upload date) |
| `description` | TEXT | Human-readable summary of the activity |
| `original_value` | DECIMAL(18,6) | Raw quantity from source |
| `original_unit` | VARCHAR(50) | e.g. `litres`, `kWh`, `miles`, `USD` |
| `normalized_value` | DECIMAL(18,6) | Converted to canonical unit |
| `normalized_unit` | VARCHAR(50) | `kWh` for energy; `kg_co2e` for emissions |
| `co2e_kg` | DECIMAL(18,6) | Final emission in kg CO₂e |
| `emission_factor` | DECIMAL(18,8) | Factor used for conversion |
| `emission_factor_source` | VARCHAR(255) | e.g. `IPCC_2021`, `EPA_2023`, `DEFRA_2024` |
| `source_location` | VARCHAR(255) | Plant code / meter ID / airport pair |
| `is_edited` | BOOLEAN | True if analyst modified any value post-ingestion |
| `edited_by` | FK → User | Null if unedited |
| `edited_at` | TIMESTAMPTZ | |
| `created_at` | TIMESTAMPTZ | |

**Scope assignment logic:**
- `sap_fuel_procurement` → Scope 1 (direct combustion of fuel owned/controlled by company)
- `utility_electricity` → Scope 2 (purchased electricity)
- `corporate_travel` → Scope 3 (Category 6: business travel)

**co2e_kg** is computed at ingestion time using the stored `emission_factor`. If the factor is updated later, the old calculation is preserved (auditors need the value-at-time-of-approval, not a retroactively recalculated one).

**Why store both original and normalized?** Auditors want to see source values. Analysts catch errors ("this says 50,000 gallons but it should be 500") more easily when they see the original unit.

---

### 6. `ReviewStatus`

Current review state of a `NormalizedEntry`. Separated from `NormalizedEntry` to keep the status machine clean and queryable.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `tenant_id` | FK → Tenant | |
| `entry_id` | FK → NormalizedEntry | One-to-one |
| `status` | ENUM | `pending`, `flagged`, `approved`, `rejected` |
| `reviewed_by` | FK → User | Null if pending |
| `reviewed_at` | TIMESTAMPTZ | |
| `flag_reason` | TEXT | Required when status = `flagged` |
| `rejection_reason` | TEXT | Required when status = `rejected` |
| `is_locked` | BOOLEAN | True once approved — blocks further edits |

**State transitions:**
```
pending → flagged    (analyst marks suspicious)
pending → approved   (analyst signs off)
pending → rejected   (analyst discards)
flagged → approved   (resolved)
flagged → rejected   (resolved as invalid)
approved → [locked]  (no further transitions)
```

Once `is_locked = true`, any attempt to edit the linked `NormalizedEntry` returns a 403.

---

### 7. `AuditLog`

Append-only. Every status change, edit, or upload event is recorded here. Never deleted.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `tenant_id` | FK → Tenant | |
| `actor_id` | FK → User | Who did it |
| `action` | ENUM | `uploaded`, `parsed`, `edited`, `flagged`, `approved`, `rejected`, `locked` |
| `target_type` | VARCHAR(50) | `IngestionBatch`, `NormalizedEntry`, etc. |
| `target_id` | UUID | ID of the affected object |
| `before_state` | JSONB | Snapshot before change (null for uploads) |
| `after_state` | JSONB | Snapshot after change |
| `timestamp` | TIMESTAMPTZ | |
| `notes` | TEXT | Optional analyst comment |

**Why JSONB snapshots?** If an analyst edits a `co2e_kg` value and later an auditor asks "what did it say before?", we have the answer. This is not a soft delete — it is a full before/after record.

---

## Source-Specific Field Notes

### SAP Fuel & Procurement
`raw_data` will contain: plant code, material number, quantity, unit of measure (UOM), document date, vendor, cost center. The normalization layer maps plant codes to locations via a lookup, converts UOM (L, GAL, m³) to litres, and applies the appropriate fuel emission factor by material type (diesel, petrol, LPG).

### Utility Electricity
`raw_data` will contain: meter ID, billing period start, billing period end, consumption (kWh), tariff code, site name. Billing periods frequently don't align to calendar months — `activity_date` is set to the billing period start date. The `source_location` field stores the meter ID.

### Corporate Travel
`raw_data` will contain: traveler ID (anonymized), trip date, origin, destination, travel class, transport mode (flight/hotel/ground), distance (if provided) or airport codes (if not). When only airport codes are given, distance is estimated using great-circle calculation with a standard 1.1 uplift factor for actual routing. Emission factors differ by cabin class (economy vs business) per DEFRA guidance.

---

## Indexes

```sql
-- All queries are tenant-scoped first
CREATE INDEX idx_normalized_tenant ON normalized_entry(tenant_id);
CREATE INDEX idx_normalized_batch ON normalized_entry(batch_id);
CREATE INDEX idx_review_status ON review_status(entry_id, status);
CREATE INDEX idx_audit_target ON audit_log(target_type, target_id);
CREATE INDEX idx_rawrow_batch ON raw_row(batch_id);
```

---

## What This Model Does Not Handle (intentionally)

1. **Emission factor versioning** — factors are stored per-row at ingestion time. A separate `EmissionFactor` table with version history is the right long-term solution but out of scope.
2. **Supplier-level Scope 3 (Categories 1–5)** — procurement data from SAP could support this but requires supplier emission intensity data we don't have.
3. **Multi-currency normalization** — travel spend is stored in original currency. FX conversion for spend-based emission estimates is not implemented.

These are documented in TRADEOFFS.md.
