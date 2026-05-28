# TRADEOFFS.md — Deliberate Omissions

Three things we chose not to build, and why.

---

## 1. Real-time SAP / Concur API Integration

**What it would be:** A scheduled job that pulls data directly from SAP via OData or Concur via REST API, eliminating the manual upload step entirely.

**Why we didn't build it:**
- SAP OData access requires the client's IT team to expose an endpoint, set up an API user with appropriate authorizations, and whitelist our server — a multi-week process that blocks day-one onboarding.
- Concur API requires app registration in the Concur App Center and enterprise OAuth provisioning. Not available on day one of a new client relationship.
- Building a polling/webhook integration before we've validated the data model would mean rebuilding the integration every time the model changes.

**The right tradeoff:** Manual CSV upload works for every client immediately, requires zero IT involvement from the client, and lets us validate the normalization logic before investing in API plumbing. Once the data model is stable and a client is fully onboarded, the API integration is a drop-in replacement for the upload step — the normalization and review pipeline is identical.

**What we'd build next:** A `DataConnector` model that encapsulates credentials and pull schedules per source per tenant, with the CSV upload as a fallback.

---

## 2. Emission Factor Versioning & Management UI

**What it would be:** A database-backed `EmissionFactor` table with version history, an admin UI to update factors when DEFRA/EPA publish new values, and a bulk recalculation job to recompute `co2e_kg` for unapproved rows when factors change.

**Why we didn't build it:**
- Emission factors are currently hardcoded per source category in the normalization layer. This is wrong for production but entirely sufficient for a prototype where sample data uses one factor set.
- A versioned factor table introduces a foreign key from `NormalizedEntry` to `EmissionFactor` version, which complicates the audit trail (the approved value must reflect the factor at approval time, not the current factor).
- The UI for factor management (upload new DEFRA spreadsheet, diff against previous version, trigger recalculation) is a non-trivial feature that would consume 1–2 days of the 4-day timeline.

**The right tradeoff:** For a prototype being evaluated on data model quality and decision judgment, shipping with hardcoded factors and documenting the gap is more honest than shipping a half-finished factor management UI. The `emission_factor` and `emission_factor_source` columns on `NormalizedEntry` are the scaffolding for the proper solution.

**What we'd build next:** `EmissionFactor(id, category, value, unit, source, valid_from, valid_to)` with a FK from `NormalizedEntry`. Recalculation job scoped to unapproved rows only.

---

## 3. Market-based Scope 2 Reporting

**What it would be:** Support for the GHG Protocol's market-based method for Scope 2 — using supplier-specific emission factors from Energy Attribute Certificates (EACs), Renewable Energy Certificates (RECs), or Power Purchase Agreements (PPAs) instead of the grid average factor.

**Why we didn't build it:**
- Market-based reporting requires the client to provide certificate data (REC serial numbers, PPA contract terms, residual mix factors by country) that is not present in a standard utility portal CSV export.
- Most large enterprises report both location-based and market-based Scope 2. Supporting both doubles the calculation surface area and introduces a certificate tracking sub-system.
- Without knowing whether this client has RECs or PPAs, building the market-based path would produce zero output — we'd have built infrastructure with no data to run through it.

**The right tradeoff:** We implement location-based Scope 2 only, document the gap clearly, and store the meter ID and tariff code in `raw_data` so the market-based calculation can be retrofitted once the client provides certificate data.

**What we'd build next:** A `EnergyAttribute Certificate` model, a second `co2e_kg_market` column on `NormalizedEntry`, and a reconciliation view that shows the delta between location-based and market-based figures.
