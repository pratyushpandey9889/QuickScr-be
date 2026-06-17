from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Priority(StrEnum):
    MUST = "Must"
    SHOULD = "Should"
    COULD = "Could"
    WONT = "Won't"


class AgentAccuracyLevel(StrEnum):
    FAST = "fast"
    BALANCED = "balanced"
    HIGH = "high"
    AUDIT = "audit"


class IntegrationType(StrEnum):
    SHAREPOINT = "SharePoint"
    SAP_ODATA = "SAP OData"
    SAP_RFC = "SAP RFC"
    AZURE_OPENAI = "Azure OpenAI"
    OPENAI = "OpenAI"
    PINECONE = "Pinecone"
    CHROMADB = "ChromaDB"
    POSTGRESQL = "PostgreSQL"


class ArtifactType(StrEnum):
    EXECUTIVE_SUMMARY = "executive_summary"
    REQUIREMENTS = "requirements"
    ARCHITECTURE = "architecture"
    DATABASE = "database"
    API = "api"
    UI = "ui"
    VALIDATION = "validation"
    INTEGRATION = "integration"
    TESTING = "testing"
    DEPLOYMENT = "deployment"


class Stakeholder(BaseModel):
    name: str
    responsibility: str
    system_role: str


class KPI(BaseModel):
    name: str
    formula: str
    target: str
    owner: str


class BusinessProcess(BaseModel):
    goals: list[str]
    stakeholders: list[Stakeholder]
    process_owners: list[str]
    inputs: list[str]
    outputs: list[str]
    current_workflow: list[str]
    future_workflow: list[str]
    pain_points: list[str]
    kpis: list[KPI]


class FunctionalRequirement(BaseModel):
    fr_id: str
    description: str
    business_rule: str
    input: str
    output: str
    priority: Priority = Priority.MUST


class NonFunctionalRequirement(BaseModel):
    category: str
    requirement: str
    acceptance_criteria: str


class EntityAttribute(BaseModel):
    name: str
    data_type: str
    nullable: bool = False
    description: str = ""
    constraints: list[str] = Field(default_factory=list)


class EntityModel(BaseModel):
    name: str
    description: str
    primary_key: str = "id"
    attributes: list[EntityAttribute]
    indexes: list[str] = Field(default_factory=list)


class Relationship(BaseModel):
    source_entity: str
    target_entity: str
    cardinality: str
    foreign_key: str
    description: str


class ValidationRule(BaseModel):
    rule_id: str
    entity: str
    field: str
    condition: str
    error_message: str
    severity: str = "error"


class ApiEndpointDesign(BaseModel):
    method: str
    endpoint: str
    request_schema: dict[str, Any] | None
    response_schema: dict[str, Any]
    validation_rules: list[str]
    errors: dict[str, str]


class IntegrationDesign(BaseModel):
    integration_type: IntegrationType
    purpose: str
    protocol: str
    authentication: str
    data_flow: list[str]
    retry_policy: str
    code_example: str


class NagareRuleSet(BaseModel):
    sequence_calloff_logic: list[str]
    delivery_scheduling_logic: list[str]
    production_sequencing: list[str]
    material_flow: list[str]
    supplier_flow: list[str]
    warehouse_flow: list[str]
    logistics_flow: list[str]
    algorithms: list[str]
    validation_logic: list[str]
    trigger_rules: list[str]
    inventory_rules: list[str]
    line_feeding_logic: list[str]
    formulas_and_kpis: list[KPI]


class DatabaseDesign(BaseModel):
    entities: list[EntityModel]
    relationships: list[Relationship]
    er_diagram_mermaid: str
    postgresql_sql: str
    sql_server_sql: str
    mysql_sql: str


class ArchitectureDesign(BaseModel):
    frontend: list[str]
    backend: list[str]
    database: list[str]
    authentication: list[str]
    cloud: list[str]
    mermaid_context_diagram: str
    mermaid_deployment_diagram: str


class TestCase(BaseModel):
    test_id: str
    test_type: str
    scenario: str
    expected_result: str
    automation_tool: str


class Risk(BaseModel):
    risk_id: str
    description: str
    impact: str
    mitigation: str


class AccuracyProfile(BaseModel):
    level: AgentAccuracyLevel
    label: str
    target_confidence: float = Field(ge=0, le=1)
    estimated_confidence: float = Field(ge=0, le=1)
    validation_depth: str
    citation_policy: str
    retrieval_top_k: int
    model_temperature: float = Field(ge=0, le=1)
    review_required: bool
    enabled_checks: list[str]
    escalation_rules: list[str]


class GeneratedSolution(BaseModel):
    solution_id: UUID = Field(default_factory=uuid4)
    source_name: str
    accuracy_profile: AccuracyProfile
    executive_summary: str
    process_flow_explanation: str
    as_is_process: list[str]
    to_be_process: list[str]
    business_process: BusinessProcess
    functional_requirements: list[FunctionalRequirement]
    non_functional_requirements: list[NonFunctionalRequirement]
    architecture: ArchitectureDesign
    database: DatabaseDesign
    api_design: list[ApiEndpointDesign]
    ui_design: list[str]
    validation_rules: list[ValidationRule]
    business_rules: list[str]
    integration_design: list[IntegrationDesign]
    nagare_rules: NagareRuleSet | None
    test_cases: list[TestCase]
    deployment_guide: list[str]
    risk_analysis: list[Risk]
    assumptions: list[str]


class TextAnalysisRequest(BaseModel):
    source_name: str = "manual-input"
    content: str = Field(min_length=20)
    accuracy_level: AgentAccuracyLevel = AgentAccuracyLevel.BALANCED


class ErrorResponse(BaseModel):
    detail: str
