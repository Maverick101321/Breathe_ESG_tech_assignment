# DECISIONS.md — Ambiguity Resolution & Design Choices

Every ambiguity encountered during design is documented here with the choice made, the reasoning, and what I would ask the PM if I could.

---

## 1. SAP Export Format: Flat CSV over IDoc or OData

**Ambiguity:** SAP exposes data in multiple ways — IDoc (structured EDI segments), OData (REST-like API), BAPI (function calls), or flat file exports.

**Choice:** Flat CSV export from SAP transaction MB51 (material document list) or ME2M (purchase orders by material).

**Why:**
- IDoc parsing requires a running SAP middleware (PI/PO or BTP) and segment schema knowledge. This is a multi-week integration project, not a 4-day prototype.
- OData requires direct network access to the client's SAP system and credentials — not realistic for a new onboarding scenario.
- In practice, the sustainability lead or finance team runs a report in SAP and exports it as a delimited file. This is the actual handoff that happens at 90% of enterprise clients.
- The complexity we care about (inconsistent units, plant codes, date formats, German headers in some configs) is fully present in flat CSV exports.

**What I'd ask the PM:**
- Does the client have an SAP integration team willing to set up an OData service, or is this a "we get what the sustainability lead emails us" situation?
- What SAP modules are licensed — MM (materials management) only, or also FI (financials) and CO (controlling)?

---

## 2. Utility Data: Portal CSV over PDF or API

**Ambiguity:** Electricity data could come as PDF bills, portal CSV exports, or a utility API (e.g. Green Button).

**Choice:** Portal CSV export — the facilities team logs into the utility portal and downloads interval or billing data as CSV.

**Why:**
- PDF bills require OCR. OCR on utility bills is notoriously fragile — layout varies by utility, multi-page bills lose context across pages, and tables don't parse cleanly. High maintenance, low reliability.
- Green Button API exists but is US-specific and requires OAuth setup with each utility. Indian utilities (relevant given the client context) rarely expose APIs.
- Portal CSV is what facilities teams actually produce. It contains billing period, meter ID, consumption in kWh, and tariff code — everything we need.
- The real complexity (billing periods not aligning to calendar months, multiple meters per site, reactive power charges we ignore) is present in CSVs and is what we handle.

**What I'd ask the PM:**
- How many meters does this client have? If it's 500+ meters across sites, a portal CSV per meter per month is unscalable and we'd need to revisit.
- Is the client Indian, EU, or US-based? Green Button becomes viable for US clients.

---

## 3. Corporate Travel: Concur CSV Export over API

**Ambiguity:** Concur exposes a REST API. Why not use it directly?

**Choice:** Concur standard report export as CSV, uploaded by the travel manager.

**Why:**
- Concur API access requires enterprise OAuth provisioning, a registered app in the Concur App Center, and client IT involvement. This is a weeks-long process, not something a new client hands over on day one.
- Concur's own documentation recommends the "Extract" report job for bulk data pulls — which produces a flat file.
- The travel manager already runs monthly travel reports for expense reconciliation. Asking them to export and upload that same report is zero additional work for them.
- This is how real Scope 3 Category 6 data flows into ESG platforms today.

**What I'd ask the PM:**
- Is Navan an option? Navan has better API ergonomics and built-in carbon tracking. If the client uses Navan, we could build a proper API pull.
- Does the client have Concur's "Intelligence" module? If yes, we can schedule automated extracts.

---

## 4. Multi-tenancy: Row-level Isolation over Schema-per-tenant

**Ambiguity:** Multi-tenancy can be implemented as separate databases, separate schemas (PostgreSQL), or row-level isolation with a `tenant_id` column.

**Choice:** Row-level isolation with `tenant_id` on every table, enforced at the ORM layer via a custom QuerySet manager.

**Why:**
- Separate databases: operationally heavy. Migrations must run N times. Connection pooling becomes complex. Overkill for a prototype.
- Schema-per-tenant: better isolation than row-level but still requires schema switching per request. Django ORM support is non-native (requires `django-tenants` or similar).
- Row-level: simple, works natively with Django ORM, easy to reason about. Risk is a missing filter leaking cross-tenant data — mitigated by a base `TenantScopedQuerySet` that always filters by `tenant_id`, used as the default manager on every model.

**What I'd ask the PM:**
- Are there regulatory requirements (GDPR, SOC2) that mandate stronger isolation? If yes, schema-per-tenant is the right call for production.

---

## 5. Scope Classification: Fixed by Source Type

**Ambiguity:** Some procurement data (SAP) could be Scope 1 or Scope 3 depending on whether the fuel is burned on-site or purchased for resale.

**Choice:** Source type determines Scope at ingestion time, with the ability for an analyst to override before approval.

- SAP fuel/procurement → **Scope 1** (direct combustion, stationary or mobile)
- Utility electricity → **Scope 2** (purchased energy, location-based method)
- Corporate travel → **Scope 3, Category 6** (business travel)

**Why:** For a prototype, a fixed mapping is correct and defensible. The analyst override mechanism handles edge cases (e.g. a procurement row that is actually a third-party logistics purchase = Scope 3 Category 4).

**What I'd ask the PM:**
- Does the client report Scope 2 using location-based or market-based method? Market-based requires supplier emission factors (RECs, PPAs) which we don't have.

---

## 6. Emission Factors: Stored per Row at Ingestion Time

**Ambiguity:** Emission factors change year to year (DEFRA publishes annually). Should we store the factor or recompute from a live table?

**Choice:** Store the emission factor value and source on each `NormalizedEntry` row at ingestion time. Never recompute retroactively.

**Why:** Auditors require that the value signed off in year N reflects the factors available in year N. If DEFRA updates factors in 2025, a 2024 submission should not change. Storing per-row makes this unambiguous.

**What I'd ask the PM:**
- Which emission factor database should we default to — DEFRA, EPA, IPCC AR6, or GHG Protocol? Different auditors prefer different sources.

---

## 7. Distance Estimation for Flights

**Ambiguity:** Concur exports often include origin/destination airport codes but not distance.

**Choice:** Compute great-circle distance from IATA airport codes using a static airport coordinate dataset, then apply a 1.1 routing uplift factor (standard industry practice) and a radiative forcing multiplier of 1.9 for high-altitude emissions (per DEFRA 2023 guidance).

**Why:** Distance is required to compute flight emissions. Great-circle + uplift is the industry standard where actual routing data is unavailable. We log that this is an estimate in the `description` field of the `NormalizedEntry`.

---

## 8. What We Ignored

**SAP:**
- Accounts Payable data (vendor invoices) — relevant for Scope 3 Category 1 but requires supplier emission intensity data we don't have
- German column headers — we normalize expected headers on upload; if a file has unrecognized headers, it fails with a clear error message
- Multi-currency procurement — all spend stored in original currency, no FX conversion

**Utility:**
- Reactive power / demand charges — stored in raw_data but not used in emission calculation
- Time-of-use tariff structures — we use total consumption per billing period, not interval-level data
- Multiple meters per site aggregation — handled by site name grouping but not validated

**Travel:**
- Hotel emissions — Scope 3 Category 6 includes hotels but emission factors require hotel-specific data (star rating, location) we rarely get from Concur exports. Excluded.
- Ground transport (taxis, car rentals) — excluded from emission calculation in v1; stored in raw_data for future use
