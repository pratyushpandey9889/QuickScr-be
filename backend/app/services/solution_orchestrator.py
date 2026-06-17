from app.domain.schemas import AgentAccuracyLevel, GeneratedSolution, Risk, TestCase
from app.services.accuracy import AccuracyService
from app.services.ai_agent_blueprint import AiAgentBlueprintService
from app.services.api_designer import ApiDesignerService
from app.services.architecture import ArchitectureService
from app.services.data_modeling import DataModelingService
from app.services.integration_design import IntegrationDesignService
from app.services.nagare import NagareService
from app.services.requirement_engineering import RequirementEngineeringService


class SolutionOrchestrator:
    def __init__(
        self,
        requirement_service: RequirementEngineeringService | None = None,
        architecture_service: ArchitectureService | None = None,
        data_service: DataModelingService | None = None,
        api_service: ApiDesignerService | None = None,
        integration_service: IntegrationDesignService | None = None,
        nagare_service: NagareService | None = None,
        ai_agent_blueprint_service: AiAgentBlueprintService | None = None,
        accuracy_service: AccuracyService | None = None,
    ) -> None:
        self.requirement_service = requirement_service or RequirementEngineeringService()
        self.architecture_service = architecture_service or ArchitectureService()
        self.data_service = data_service or DataModelingService()
        self.api_service = api_service or ApiDesignerService()
        self.integration_service = integration_service or IntegrationDesignService()
        self.nagare_service = nagare_service or NagareService()
        self.ai_agent_blueprint_service = ai_agent_blueprint_service or AiAgentBlueprintService()
        self.accuracy_service = accuracy_service or AccuracyService()

    def generate(
        self,
        source_name: str,
        text: str,
        accuracy_level: AgentAccuracyLevel = AgentAccuracyLevel.BALANCED,
    ) -> GeneratedSolution:
        accuracy_profile = self.accuracy_service.create_profile(accuracy_level, text)
        business_process = self.requirement_service.build_business_process(text)
        functional_requirements = self.requirement_service.create_functional_requirements(text)
        non_functional_requirements = self.requirement_service.create_non_functional_requirements()
        database = self.data_service.design_database(text, functional_requirements)
        nagare_rules = self.nagare_service.design_rules() if self.nagare_service.applies(text) else None
        ui_design = [
            "Document intake panel with upload, SharePoint source selector, and analysis status",
            "Executive summary and As-Is/To-Be comparison view",
            "Requirement catalog with priority, business rule, owner, and approval status",
            "Architecture tab with Mermaid diagrams and deployment topology",
            "Database tab with ER diagram and SQL dialect selector",
            "API tab with REST endpoint matrix, schemas, errors, and Swagger link",
            "Nagare tab for sequence call-off, delivery windows, inventory projection, and exception queue",
            "Integration tab for SAP, SharePoint, vector store, and AI agent configuration",
            "Testing tab with unit, integration, API, Playwright, and UAT scenarios",
            "Accuracy profile panel with confidence estimate, validation depth, citation policy, and review gates",
            "Audit timeline with source document, generated decisions, reviewer actions, and exports",
        ]
        business_rules = [
            "Every generated artifact must include source name and timestamp for traceability.",
            "Requirements cannot move to approved status until a process owner and architect have reviewed them.",
            "External integration calls must be idempotent, authenticated, encrypted, logged, and retry-safe.",
            "Generated SQL must include primary keys, foreign keys, indexes, and audit fields.",
            "AI answers must cite source documents when answering process or requirement questions.",
            f"Agent accuracy level '{accuracy_profile.label}' must apply {accuracy_profile.validation_depth}.",
        ]
        if accuracy_profile.review_required:
            business_rules.append("Generated artifacts require reviewer approval before production export.")
        if nagare_rules:
            business_rules.extend(nagare_rules.validation_logic)
        integration_design = self.integration_service.design(text)
        if any(keyword in text.lower() for keyword in ["agent", "embedding", "openai", "question", "chat"]):
            ui_design.extend(self.ai_agent_blueprint_service.implementation_notes())

        return GeneratedSolution(
            source_name=source_name,
            accuracy_profile=accuracy_profile,
            executive_summary=self.requirement_service.create_executive_summary(text, source_name),
            process_flow_explanation=self.requirement_service.explain_process_flow(business_process),
            as_is_process=business_process.current_workflow,
            to_be_process=business_process.future_workflow,
            business_process=business_process,
            functional_requirements=functional_requirements,
            non_functional_requirements=non_functional_requirements,
            architecture=self.architecture_service.design(text),
            database=database,
            api_design=self.api_service.design_for_entities(database.entities),
            ui_design=ui_design,
            validation_rules=self.data_service.validation_rules(database.entities),
            business_rules=business_rules,
            integration_design=integration_design,
            nagare_rules=nagare_rules,
            test_cases=self._test_cases(
                nagare_enabled=nagare_rules is not None,
                accuracy_level=accuracy_level,
            ),
            deployment_guide=self._deployment_guide(),
            risk_analysis=self._risks(text, accuracy_level),
            assumptions=self._assumptions(text, accuracy_level),
        )

    def _test_cases(self, nagare_enabled: bool, accuracy_level: AgentAccuracyLevel) -> list[TestCase]:
        tests = [
            TestCase(
                test_id="UT-001",
                test_type="Unit",
                scenario="Requirement extractor generates baseline FR and NFR catalogs from document text.",
                expected_result="Structured requirements are returned with stable IDs and priorities.",
                automation_tool="Pytest",
            ),
            TestCase(
                test_id="IT-001",
                test_type="Integration",
                scenario="Uploaded document is parsed, analyzed, saved, and retrievable by solution ID.",
                expected_result="API returns 200 and persisted generated solution matches source metadata.",
                automation_tool="Pytest + HTTPX",
            ),
            TestCase(
                test_id="API-001",
                test_type="API",
                scenario="Protected API rejects requests without valid JWT outside local environment.",
                expected_result="API returns 401 or 403 based on authentication and RBAC status.",
                automation_tool="Pytest",
            ),
            TestCase(
                test_id="E2E-001",
                test_type="Playwright",
                scenario="Analyst uploads a BRD and reviews generated requirements, database, and API tabs.",
                expected_result="Workbench renders generated artifacts without layout overlap or client errors.",
                automation_tool="Playwright",
            ),
            TestCase(
                test_id="UAT-001",
                test_type="UAT",
                scenario="Process owner approves generated To-Be process and requirement catalog.",
                expected_result="Approval is recorded in audit log and artifacts are exportable.",
                automation_tool="Manual UAT script",
            ),
        ]
        if nagare_enabled:
            tests.append(
                TestCase(
                    test_id="UAT-002",
                    test_type="UAT",
                    scenario="Planner validates a sequence call-off with supplier lead time, delivery window, and inventory projection.",
                    expected_result="System flags late, duplicate, or stockout-risk call-offs before release.",
                    automation_tool="Manual UAT script + Pytest fixtures",
                )
            )
        if accuracy_level in {AgentAccuracyLevel.HIGH, AgentAccuracyLevel.AUDIT}:
            tests.append(
                TestCase(
                    test_id="UAT-003",
                    test_type="UAT",
                    scenario="Reviewer validates that generated Must requirements and critical business rules have source evidence.",
                    expected_result="System highlights uncited or low-confidence artifacts and blocks approval where required.",
                    automation_tool="Manual UAT script + Pytest fixtures",
                )
            )
        if accuracy_level == AgentAccuracyLevel.AUDIT:
            tests.append(
                TestCase(
                    test_id="UAT-004",
                    test_type="UAT",
                    scenario="Audit-grade export is attempted before process owner and architect approvals.",
                    expected_result="Export is blocked until mandatory review gates are complete.",
                    automation_tool="Manual UAT script",
                )
            )
        return tests

    def _deployment_guide(self) -> list[str]:
        return [
            "Provision PostgreSQL, storage, Key Vault, container registry, and monitoring resources.",
            "Configure Azure AD application registration, API audience, redirect URIs, and RBAC roles.",
            "Build and push backend, frontend, worker, and migration container images.",
            "Run database migrations and seed admin role assignments.",
            "Deploy API and worker with managed identity, secrets from Key Vault, health probes, and autoscaling.",
            "Deploy frontend with API base URL and Azure AD client configuration.",
            "Configure SharePoint Sites.Selected permission and SAP network connectivity if required.",
            "Enable Application Insights dashboards, log retention, alert rules, and backup policies.",
        ]

    def _risks(self, text: str, accuracy_level: AgentAccuracyLevel) -> list[Risk]:
        risks = [
            Risk(
                risk_id="R-001",
                description="Source documents may be incomplete or ambiguous.",
                impact="Generated requirements may require human review before implementation.",
                mitigation="Mark assumptions, require owner approval, and capture source citations.",
            ),
            Risk(
                risk_id="R-002",
                description="SAP service coverage may vary across landscapes.",
                impact="Some operations may require RFC or custom wrapper services instead of OData.",
                mitigation="Run SAP discovery workshop and maintain adapter boundary per integration type.",
            ),
            Risk(
                risk_id="R-003",
                description="AI-generated content may include unsupported inference.",
                impact="Incorrect decisions could be accepted without validation.",
                mitigation="Require citations, deterministic validations, and approval workflow.",
            ),
        ]
        if "sharepoint" in text.lower():
            risks.append(
                Risk(
                    risk_id="R-004",
                    description="SharePoint permissions and document lifecycle policies may block retrieval.",
                    impact="Source ingestion may miss restricted or archived files.",
                    mitigation="Use Sites.Selected, metadata audit, and retryable ingestion status tracking.",
                )
            )
        if accuracy_level == AgentAccuracyLevel.FAST:
            risks.append(
                Risk(
                    risk_id="R-005",
                    description="Fast Draft accuracy level performs lighter cross-artifact validation.",
                    impact="Generated artifacts may need deeper review before development or production decisions.",
                    mitigation="Use High Accuracy or Audit Grade before regulated approval, SAP write-back, or production export.",
                )
            )
        if accuracy_level == AgentAccuracyLevel.AUDIT:
            risks.append(
                Risk(
                    risk_id="R-006",
                    description="Audit Grade can block export when source evidence or reviewer approvals are missing.",
                    impact="Delivery may wait for process owner or architect review.",
                    mitigation="Plan review SLA and maintain complete source document citations.",
                )
            )
        return risks

    def _assumptions(self, text: str, accuracy_level: AgentAccuracyLevel) -> list[str]:
        assumptions = [
            "The submitted document is the authoritative source for first-pass requirement generation.",
            "Generated artifacts require business and architecture review before production release.",
            "PostgreSQL is the primary operational database.",
            "Azure AD is the preferred identity provider.",
            "Azure is the preferred cloud platform, with AWS patterns available as an alternative.",
        ]
        lower = text.lower()
        if "sap" in lower:
            assumptions.append("SAP systems expose required master and transaction data through OData or an approved RFC connector.")
        if "sharepoint" in lower:
            assumptions.append("The application can be granted Microsoft Graph permission to read selected SharePoint sites.")
        if "nagare" in lower or "jit" in lower or "sequence" in lower:
            assumptions.append("Production sequence, BOM, supplier lead time, and inventory data are available with reliable timestamps.")
        if accuracy_level in {AgentAccuracyLevel.HIGH, AgentAccuracyLevel.AUDIT}:
            assumptions.append("Source citations and reviewer decisions are available for every critical generated requirement.")
        if accuracy_level == AgentAccuracyLevel.AUDIT:
            assumptions.append("Audit-grade exports are allowed only after process owner and solution architect approvals.")
        return assumptions
