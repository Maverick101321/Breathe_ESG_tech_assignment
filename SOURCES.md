# SOURCES.md — Source Research & Sample Data Rationale

For each of the three sources: what real-world format was researched, what we learned, what the sample data looks like and why, and what would break in a real deployment.

---

## 1. SAP — Fuel & Procurement Data

### Real-world format researched

SAP exposes procurement and materials data through several mechanisms. We researched:

- **IDoc (Intermediate Document):** SAP's native EDI format. Segment-based, fixed-width fields, hierarchical structure. Used primarily for system-to-system integration (SAP to SAP, or SAP to logistics partners). Requires a configured port (WE20/WE21) and partner profiles. Not a human-accessible export.
- **OData services:** SAP Gateway exposes OData endpoints (e.g. `API_MATERIAL_DOCUMENT_SRV` for goods movements). Requires a developer key, SAP Gateway license, and client IT involvement to whitelist and authorize.
- **Flat file export from transaction MB51:** MB51 is the Material Document List — it lists all goods movements (goods receipts, goods issues, transfers) filtered by plant, material, movement type, and date range. The sustainability lead can run this report and export it via the SAP GUI list export to a tab-delimited or CSV file.
- **ME2M / ME2L:** Purchase order reports by material or vendor. Similar export capability.

### What we learned

MB51 exports are the realistic handoff format for fuel and energy procurement. A typical export contains:

- `Posting Date` — in SAP default format (DD.MM.YYYY in German locale, MM/DD/YYYY in US locale)
- `Material` — SAP material number (e.g. `RAW-DIESEL-001`), not a human-readable name
- `Plant` — 4-character plant code (e.g. `1000`, `IN01`) — meaningless without a plant master lookup
- `Movement Type` — numeric code (e.g. `101` = goods receipt, `201` = goods issue to cost center)
- `Quantity` — numeric value
- `Base Unit of Measure` — SAP UOM codes: `L` (litres), `GAL` (US gallons), `KG`, `M3`
- `Storage Location`, `Cost Center`, `Vendor` — additional context fields

German column headers appear when SAP system language is DE: `Buchungsdatum`, `Werk`, `Menge`, `Basismengeneinheit`.

Movement type determines direction: goods issue (201, 261) = consumption = relevant for emissions. Goods receipt (101) = procurement, only relevant if tracking purchased fuel inventory.

### Sample data rationale

Our sample CSV uses:
- Posting dates in DD.MM.YYYY (German locale — the harder case, shows we know this exists)
- Plant codes `IN01`, `IN02` (India plants — realistic for an Indian enterprise client)
- Material numbers with a human-readable suffix (`DIESEL-HSD`, `PETROL-MS`, `LPG-BULK`)
- Movement type 261 (goods issue to production order) — direct fuel consumption
- UOM mix: litres and kg (LPG is sold by weight in India)
- One row with an unrecognized UOM (`MT` instead of `TO` for metric ton) — tests our error handling

### What would break in real deployment

- **Plant code lookup:** Our normalization maps `IN01` → "Mumbai Plant" using a hardcoded dict. A real client has 50–200 plant codes, some of which change after acquisitions. Needs a client-managed lookup table.
- **Material number mapping:** We map material numbers to fuel types via a prefix convention. Real SAP material masters have no naming convention — `1000045` could be diesel or office supplies. Needs a material-to-fuel-type mapping table, maintained by the client.
- **Movement type logic:** We only process type 261. A real deployment needs a configurable movement type filter — different clients configure their SAP differently.
- **Multi-company-code exports:** Large enterprises run multiple company codes in one SAP system. MB51 can export across company codes, producing rows that belong to different legal entities (relevant for consolidated vs entity-level reporting).

---

## 2. Utility Data — Electricity

### Real-world format researched

We researched three modes of utility data access:

- **PDF bills:** Physical or emailed PDF invoices from the utility. Contain all billing data but require OCR. Layout varies per utility, per billing period, and after utility system upgrades. High maintenance.
- **Portal CSV export:** Utilities (Tata Power, MSEDCL, BESCOM in India; PG&E, ConEd in the US) provide customer portals where interval data or billing summaries can be downloaded as CSV. Common for commercial/industrial accounts.
- **Green Button API:** US standard for utility data sharing. OAuth-based. Not available in India or most of Asia.
- **EDI 810 (invoice) / EDI 867 (meter reads):** Used by large US enterprises with third-party bill management vendors. Converted to CSV by the vendor.

### What we learned

For Indian enterprise clients, portal CSV is the only realistic option. A typical MSEDCL or Tata Power commercial portal CSV contains:

- `Consumer Number` — meter/account identifier
- `Billing Month` — often written as `APR-2024` or `04/2024`
- `Billing Period From` / `To` — actual read dates, which don't align to calendar months
- `Units Consumed (kWh)` — total consumption for the period
- `Sanctioned Load (kW)` — contracted demand
- `Maximum Demand (kVA)` — peak demand recorded
- `Tariff Category` — commercial, industrial HT, industrial LT, etc.
- `Amount (INR)` — total bill amount

Key complexity: billing periods. A meter read on March 28 and April 29 produces a "March" bill that actually covers 32 days spanning two months. Naive calendar-month aggregation double-counts or misses consumption. We store `billing_period_start` and `billing_period_end` and attribute consumption to the start date.

### Sample data rationale

Our sample CSV uses:
- Three meters across two sites (`SITE-MUM-01`, `SITE-BLR-01`) — realistic for a multi-site client
- Billing periods that don't align to calendar months (e.g. Mar 28 – Apr 27) — tests our date handling
- One row with consumption in `MWh` instead of `kWh` — tests unit normalization
- One row with a missing `Units Consumed` field and a non-zero amount — surfaces as a parse error in the dashboard (common when a bill is estimated, not metered)
- Tariff codes `LT-III` and `HT-II` — left as-is in raw_data, not used in v1 calculation

### What would break in real deployment

- **Multi-meter aggregation:** A large client with 200 meters across 30 sites produces 200 CSVs per month (one per meter or one per account). We handle a single CSV upload — bulk upload and site-level aggregation is not implemented.
- **Estimated vs actual reads:** Utilities estimate consumption when a meter is inaccessible. The estimated value is later corrected in the next bill as a "true-up" adjustment. Our model doesn't handle adjustments to previously approved rows.
- **Reactive power and power factor penalties:** Appear as line items in the bill. Not relevant to kWh consumption or emissions but inflate the total units consumed figure in some export formats.
- **Rooftop solar / net metering:** A client with solar panels has bidirectional meter reads (import and export). Export reduces Scope 2 but our model only handles import.

---

## 3. Corporate Travel — Flights & Ground Transport

### Real-world format researched

We researched Concur and Navan as the two dominant enterprise travel platforms.

**Concur:** SAP Concur is the enterprise standard for large organizations. Data access options:
- **Standard List Report export:** Travel managers run a report in Concur Intelligence or standard reporting and export as CSV/Excel. Most common.
- **Concur Extract (Data Extract Job):** Scheduled flat file export to SFTP. Requires Concur Professional/Premium and IT setup.
- **Concur Travel API (v4):** REST API for trip itineraries. Requires app registration in Concur App Center and enterprise OAuth. Available but gated.

**Navan:** More modern API-first platform. Exposes trip data via REST with better ergonomics. Has built-in carbon tracking. Growing adoption among tech companies but not yet dominant in traditional enterprises.

A typical Concur travel report CSV export contains:
- `Report Name` / `Report ID` — expense report identifier
- `Employee ID` / `Employee Name` — traveler (we anonymize to Employee ID only)
- `Transaction Date` — date of travel or booking
- `Expense Type` — `Airfare`, `Hotel`, `Car Rental`, `Ground Transport`
- `Vendor Name` — airline, hotel chain, car rental company
- `Origin City` / `Destination City` — for flights
- `Origin Airport Code` / `Destination Airport Code` — IATA codes (e.g. `BOM`, `DEL`, `LHR`)
- `Distance` — sometimes present (miles or km), often absent
- `Amount` — spend in original currency
- `Currency Code`
- `Travel Class` — `Economy`, `Business`, `First`

### What we learned

Distance is the key gap. Concur exports frequently omit distance — only origin and destination airport codes are given. The industry standard for filling this gap:

1. Look up coordinates for origin and destination from an IATA airport database
2. Calculate great-circle distance (Haversine formula)
3. Apply a 1.1 routing uplift factor (real routes are longer than straight lines)
4. Apply a radiative forcing index (RFI) multiplier of 1.9 for flights (per DEFRA 2023) to account for non-CO₂ warming effects at altitude

Cabin class matters significantly: business class carries 2–3x the emission factor of economy per km (seat count allocation method per DEFRA).

### Sample data rationale

Our sample CSV uses:
- IATA airport code pairs without distance (`BOM→DEL`, `DEL→LHR`, `BOM→SIN`) — tests our distance estimation
- One row with distance pre-populated in miles — tests unit conversion (miles → km)
- Mix of economy and business class — tests cabin class factor differentiation
- Hotel rows with no distance field — hotels use spend-based emission factors (excluded from v1 calculation, stored in raw_data)
- Ground transport rows (taxi, car rental) — stored but not calculated in v1
- One row with an unrecognized airport code (`XXX`) — surfaces as a flagged row in the dashboard

### What would break in real deployment

- **Hotel emission calculation:** Excluded in v1. Requires spend-based factors by country and star rating (per DEFRA Category 6 guidance). Without this, Scope 3 Category 6 is understated.
- **Ground transport:** Car rental emissions require vehicle class and distance or fuel consumed. Taxi spend-based factors vary by country. Both excluded.
- **Anonymization:** We store `Employee ID` only. A real deployment needs to confirm whether employee-level data can be stored per the client's data protection policy (GDPR Article 88 for EU clients).
- **Multi-leg itineraries:** A trip BOM→DXB→LHR appears as two rows in Concur. Our normalization treats them independently, which is correct, but a future feature would group by trip ID for analyst readability.
- **Frequent flyer upgrades:** A ticket purchased as economy but flown as business (upgrade) may be logged as economy in Concur. Emission factor applied is wrong. No reliable way to detect this from export data.
