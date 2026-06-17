import re
from collections import Counter

from app.domain.schemas import (
    BusinessProcess,
    FunctionalRequirement,
    KPI,
    NonFunctionalRequirement,
    Priority,
    Stakeholder,
)


class RequirementEngineeringService:
    process_keywords = {
        "approval": "Approval Workflow",
        "inventory": "Inventory Control",
        "delivery": "Delivery Execution",
        "sequence": "Production Sequencing",
        "supplier": "Supplier Collaboration",
        "warehouse": "Warehouse Operations",
        "sap": "SAP Integration",
        "sharepoint": "Document Governance",
        "invoice": "Finance Processing",
        "quality": "Quality Management",
    }

    def create_executive_summary(self, text: str, source_name: str) -> str:
        topics = self._rank_topics(text)
        topic_text = ", ".join(topics[:5]) if topics else "business process automation"
        return (
            f"{source_name} has been analyzed as an enterprise process transformation candidate. "
            f"The target solution focuses on {topic_text}, structured requirement extraction, "
            "auditable workflow execution, secure integrations, and automated generation of "
            "database, API, UI, validation, testing, and deployment artifacts."
        )

    def build_business_process(self, text: str) -> BusinessProcess:
        lower = text.lower()
        goals = self._extract_goals(lower)
        inputs = self._extract_inputs(lower)
        outputs = self._extract_outputs(lower)
        current_workflow = self._extract_workflow(text, fallback="Receive request and process manually")
        future_workflow = [
            "Ingest source documents from upload, SharePoint, or SAP-linked repositories",
            "Classify process domain, entities, validations, integrations, and KPIs",
            "Generate solution architecture, APIs, database design, UI backlog, tests, and deployment plan",
            "Route generated artifacts for owner review and controlled approval",
            "Persist audit trail, source citations, generated decisions, and implementation status",
        ]
        pain_points = self._extract_pain_points(lower)
        return BusinessProcess(
            goals=goals,
            stakeholders=self._extract_stakeholders(lower),
            process_owners=self._extract_process_owners(lower),
            inputs=inputs,
            outputs=outputs,
            current_workflow=current_workflow,
            future_workflow=future_workflow,
            pain_points=pain_points,
            kpis=self._default_kpis(lower),
        )

    def create_functional_requirements(self, text: str) -> list[FunctionalRequirement]:
        lower = text.lower()
        requirements = [
            FunctionalRequirement(
                fr_id="FR-001",
                description="Ingest business documents from file upload and supported enterprise repositories.",
                business_rule="Only authorized users may submit source documents for analysis.",
                input="BRD, SOP, flowchart text, SAP process document, SharePoint document, CSV, XLSX, PDF, or DOCX",
                output="Normalized document text with source metadata",
                priority=Priority.MUST,
            ),
            FunctionalRequirement(
                fr_id="FR-002",
                description="Extract business process goals, stakeholders, inputs, outputs, workflow steps, pain points, and KPIs.",
                business_rule="Every generated artifact must preserve traceability to the source document name.",
                input="Normalized document text",
                output="Structured business process model",
                priority=Priority.MUST,
            ),
            FunctionalRequirement(
                fr_id="FR-003",
                description="Generate functional and non-functional requirements with priorities and acceptance context.",
                business_rule="Requirements must be uniquely identified and categorized before implementation planning.",
                input="Business process model and extracted statements",
                output="FR and NFR catalog",
                priority=Priority.MUST,
            ),
            FunctionalRequirement(
                fr_id="FR-004",
                description="Generate entity model, ER diagram, SQL scripts, API contracts, validation rules, and tests.",
                business_rule="Generated schemas must include audit fields and tenant-safe identifiers.",
                input="Requirements and entity candidates",
                output="Implementation artifacts",
                priority=Priority.MUST,
            ),
        ]

        conditional_requirements = [
            (
                "sharepoint",
                FunctionalRequirement(
                    fr_id="FR-005",
                    description="Retrieve, search, and extract metadata from SharePoint document libraries.",
                    business_rule="SharePoint access must use Azure AD delegated or application permissions.",
                    input="Site ID, drive ID, folder path, document metadata",
                    output="Indexed source document content with citations",
                    priority=Priority.SHOULD,
                ),
            ),
            (
                "sap",
                FunctionalRequirement(
                    fr_id="FR-006",
                    description="Integrate with SAP OData or RFC services for master data, transaction status, and process events.",
                    business_rule="SAP calls must be idempotent, logged, retried, and reconciled against source keys.",
                    input="SAP client, service endpoint, business object keys",
                    output="Validated SAP payloads and integration status",
                    priority=Priority.SHOULD,
                ),
            ),
            (
                "sequence",
                FunctionalRequirement(
                    fr_id="FR-007",
                    description="Calculate Nagare sequence call-offs, delivery windows, line feeding instructions, and exception alerts.",
                    business_rule="Sequence changes must preserve FIFO within the same production slot unless planner override is approved.",
                    input="Production sequence, takt time, supplier lead time, inventory position",
                    output="Delivery call-off, material staging plan, exception list",
                    priority=Priority.MUST,
                ),
            ),
        ]
        for keyword, requirement in conditional_requirements:
            if keyword in lower:
                requirements.append(requirement)
        return requirements

    def create_non_functional_requirements(self) -> list[NonFunctionalRequirement]:
        return [
            NonFunctionalRequirement(
                category="Security",
                requirement="Use OAuth2 with Azure AD, JWT validation, RBAC, encrypted transport, and least-privilege integration credentials.",
                acceptance_criteria="All protected APIs reject unauthenticated requests and enforce role permissions.",
            ),
            NonFunctionalRequirement(
                category="Scalability",
                requirement="Separate ingestion, analysis, API, and vector indexing workloads for horizontal scaling.",
                acceptance_criteria="The platform can process large document batches through asynchronous workers without blocking API requests.",
            ),
            NonFunctionalRequirement(
                category="Performance",
                requirement="Return synchronous text analysis in under 5 seconds for documents under 50 KB and queue larger jobs.",
                acceptance_criteria="P95 API latency is measured and alerting is configured for threshold breaches.",
            ),
            NonFunctionalRequirement(
                category="Availability",
                requirement="Deploy stateless services across multiple availability zones with managed PostgreSQL backups.",
                acceptance_criteria="RPO is 15 minutes or less and RTO is 60 minutes or less for production.",
            ),
            NonFunctionalRequirement(
                category="Maintainability",
                requirement="Use clean architecture boundaries, typed contracts, dependency injection, and isolated integration adapters.",
                acceptance_criteria="Core services have unit tests and integrations have contract tests.",
            ),
            NonFunctionalRequirement(
                category="Auditability",
                requirement="Record source documents, generated artifacts, user actions, approvals, and integration calls.",
                acceptance_criteria="Auditors can trace each generated decision back to source document and user action.",
            ),
        ]

    def explain_process_flow(self, process: BusinessProcess) -> str:
        return (
            "The process starts with controlled document ingestion, moves through automated "
            "business understanding and requirement engineering, then produces governed "
            "implementation artifacts for architecture, data, APIs, UI, validation, integrations, "
            "testing, and deployment. The future state replaces manual interpretation with "
            "repeatable extraction, traceable decisions, review checkpoints, and secure delivery."
        )

    def _rank_topics(self, text: str) -> list[str]:
        lower = text.lower()
        hits = [label for keyword, label in self.process_keywords.items() if keyword in lower]
        if hits:
            return hits
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{3,}", lower)
        stop_words = {"process", "document", "system", "business", "user", "data", "from", "with"}
        counts = Counter(word for word in words if word not in stop_words)
        return [word.title() for word, _ in counts.most_common(5)]

    def _extract_goals(self, lower: str) -> list[str]:
        goals = ["Convert business documentation into traceable, production-ready software artifacts"]
        if "manual" in lower:
            goals.append("Reduce manual interpretation effort and handoff delays")
        if "sap" in lower:
            goals.append("Synchronize business process execution with SAP system of record data")
        if "sharepoint" in lower:
            goals.append("Use governed SharePoint content as a controlled requirements source")
        if "jit" in lower or "nagare" in lower or "sequence" in lower:
            goals.append("Improve JIT sequence accuracy and material delivery adherence")
        return goals

    def _extract_inputs(self, lower: str) -> list[str]:
        inputs = ["Business requirement documents", "SOPs", "Process flow descriptions"]
        if "excel" in lower or "xlsx" in lower:
            inputs.append("Excel workbooks")
        if "sharepoint" in lower:
            inputs.append("SharePoint documents and metadata")
        if "sap" in lower:
            inputs.append("SAP master data, process documents, OData payloads, and RFC responses")
        return inputs

    def _extract_outputs(self, lower: str) -> list[str]:
        outputs = [
            "Executive summary",
            "Requirement catalog",
            "Database schema",
            "API contracts",
            "Frontend backlog",
            "Test scenarios",
        ]
        if "nagare" in lower or "jit" in lower or "sequence" in lower:
            outputs.append("Sequence call-off and line feeding logic")
        return outputs

    def _extract_workflow(self, text: str, fallback: str) -> list[str]:
        candidates = []
        for line in text.splitlines():
            stripped = line.strip(" -\t")
            if re.match(r"^(\d+[\).]|step\s+\d+)", stripped.lower()):
                candidates.append(stripped)
        return candidates[:12] or [
            fallback,
            "Interpret requirements across business, IT, and operations teams",
            "Design solution artifacts manually",
            "Review, revise, and hand off to implementation team",
        ]

    def _extract_pain_points(self, lower: str) -> list[str]:
        pain_points = []
        if "manual" in lower:
            pain_points.append("Manual document interpretation creates inconsistency and rework")
        if "delay" in lower or "late" in lower:
            pain_points.append("Process delays affect downstream execution and delivery commitments")
        if "error" in lower or "mismatch" in lower:
            pain_points.append("Data mismatches increase exception handling effort")
        if "excel" in lower:
            pain_points.append("Spreadsheet-driven workflows limit auditability and concurrent collaboration")
        return pain_points or [
            "Requirements are spread across unstructured documents",
            "Architecture and implementation artifacts are recreated for every initiative",
            "Traceability from source requirement to delivered software is difficult to prove",
        ]

    def _extract_stakeholders(self, lower: str) -> list[Stakeholder]:
        stakeholders = [
            Stakeholder(name="Business Process Owner", responsibility="Owns process outcomes and approvals", system_role="architect"),
            Stakeholder(name="Business Analyst", responsibility="Reviews generated requirements and rules", system_role="analyst"),
            Stakeholder(name="Solution Architect", responsibility="Approves architecture and integration design", system_role="architect"),
            Stakeholder(name="Developer", responsibility="Implements generated code and tests", system_role="analyst"),
        ]
        if "supplier" in lower:
            stakeholders.append(Stakeholder(name="Supplier Coordinator", responsibility="Monitors supplier delivery adherence", system_role="viewer"))
        if "warehouse" in lower:
            stakeholders.append(Stakeholder(name="Warehouse Planner", responsibility="Executes staging and line feeding plan", system_role="analyst"))
        return stakeholders

    def _extract_process_owners(self, lower: str) -> list[str]:
        owners = ["Business Process Owner", "IT Product Owner"]
        if "sap" in lower:
            owners.append("SAP Functional Consultant")
        if "quality" in lower:
            owners.append("Quality Manager")
        if "warehouse" in lower or "inventory" in lower:
            owners.append("Warehouse Operations Lead")
        return owners

    def _default_kpis(self, lower: str) -> list[KPI]:
        kpis = [
            KPI(
                name="Requirement Extraction Cycle Time",
                formula="analysis_completed_at - document_received_at",
                target="< 1 business day",
                owner="Business Analyst",
            ),
            KPI(
                name="Generated Artifact Acceptance Rate",
                formula="accepted_artifacts / total_generated_artifacts * 100",
                target=">= 90%",
                owner="Solution Architect",
            ),
            KPI(
                name="Traceability Coverage",
                formula="requirements_with_source_reference / total_requirements * 100",
                target="100%",
                owner="Compliance Lead",
            ),
        ]
        if "delivery" in lower or "sequence" in lower or "nagare" in lower:
            kpis.append(
                KPI(
                    name="Sequence Delivery Adherence",
                    formula="on_sequence_deliveries / total_sequence_deliveries * 100",
                    target=">= 98%",
                    owner="Logistics Lead",
                )
            )
        return kpis

