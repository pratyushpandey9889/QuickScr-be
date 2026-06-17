# UAT Scenarios

## UAT-001: BRD To Requirements

Given a business analyst uploads a BRD, when analysis completes, then the system displays an executive summary, As-Is process, To-Be process, functional requirements, non-functional requirements, risks, and assumptions.

Acceptance criteria:

- Functional requirements have IDs, descriptions, business rules, inputs, outputs, and priorities.
- NFRs cover security, scalability, performance, availability, maintainability, and auditability.
- All generated content includes source document context.

## UAT-002: Nagare JIT Sequence

Given a Nagare process document includes production sequence, supplier lead time, delivery windows, warehouse flow, and line feeding, when analysis completes, then the system generates sequence call-off logic, trigger rules, inventory formulas, validation logic, and KPIs.

Acceptance criteria:

- Delivery window formula is generated.
- Duplicate sequence, invalid supplier, zero quantity, invalid window, and inventory shortage validations are present.
- Sequence delivery adherence and line stop KPIs are present.

## UAT-003: SharePoint Source

Given a SharePoint source is configured, when a document is retrieved, then the system stores site, drive, item, URL, etag, and modified metadata before analysis.

Acceptance criteria:

- Changed etag triggers re-indexing.
- Restricted documents return a clear authorization status.
- Source citations point back to SharePoint document metadata.

## UAT-004: SAP Integration

Given SAP material and supplier APIs are configured, when generated call-off logic references SAP master data, then the system validates material, supplier, plant, and status before release.

Acceptance criteria:

- SAP calls include correlation IDs.
- Retry behavior is idempotent.
- SAP errors are mapped to business-readable exceptions.

