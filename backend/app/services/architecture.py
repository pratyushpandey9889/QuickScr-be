from app.domain.schemas import ArchitectureDesign


class ArchitectureService:
    def design(self, text: str) -> ArchitectureDesign:
        lower = text.lower()
        frontend = [
            "Next.js App Router with React and TypeScript",
            "Tailwind CSS design system for document analysis workbench",
            "RBAC-aware routes for analysts, architects, admins, and viewers",
            "Artifact viewers for requirements, Mermaid diagrams, SQL, APIs, and tests",
        ]
        backend = [
            "FastAPI application with service layer, repository abstraction, and dependency injection",
            "Document parser pipeline for TXT, Markdown, CSV, JSON, PDF, DOCX, and XLSX",
            "Requirement engineering service for deterministic extraction and AI-assisted extension",
            "Background worker for large ingestion, embeddings, and integration synchronization",
        ]
        database = [
            "PostgreSQL operational store for documents, analyses, requirements, audit logs, and conversations",
            "pgvector, Pinecone, or ChromaDB for retrieval augmented generation vectors",
            "Transactional outbox table for reliable SAP and SharePoint integration events",
        ]
        authentication = [
            "OAuth2 authorization code flow with Azure AD",
            "JWT bearer validation at FastAPI boundary",
            "Role-based access control for documents, generated solutions, integrations, and admin tasks",
            "Managed identity or workload identity for Azure service-to-service credentials",
        ]
        cloud = [
            "Azure Container Apps or AKS for API, frontend, worker, and scheduler",
            "Azure Database for PostgreSQL Flexible Server",
            "Azure Blob Storage for raw source documents and generated artifact packages",
            "Azure Key Vault for integration secrets",
            "Azure Monitor and Application Insights for logs, traces, metrics, and alerts",
        ]
        if "aws" in lower:
            cloud.append("AWS alternative: ECS Fargate, RDS PostgreSQL, S3, Secrets Manager, CloudWatch, and Bedrock/OpenAI gateway")
        return ArchitectureDesign(
            frontend=frontend,
            backend=backend,
            database=database,
            authentication=authentication,
            cloud=cloud,
            mermaid_context_diagram=self._context_diagram(),
            mermaid_deployment_diagram=self._deployment_diagram(),
        )

    def _context_diagram(self) -> str:
        return """flowchart LR
  Analyst[Business Analyst] --> UI[Next.js Workbench]
  Architect[Solution Architect] --> UI
  UI --> API[FastAPI API]
  API --> Parser[Document Parser]
  API --> Generator[Requirement and Artifact Generator]
  Generator --> DB[(PostgreSQL)]
  Generator --> Vector[(Vector Store)]
  API --> Auth[Azure AD]
  API --> SP[SharePoint Graph API]
  API --> SAP[SAP OData/RFC]
  API --> AI[Azure OpenAI/OpenAI]
  Worker[Background Worker] --> DB
  Worker --> Vector
  Worker --> SP
  Worker --> SAP"""

    def _deployment_diagram(self) -> str:
        return """flowchart TB
  subgraph Azure
    Frontend[Container App: Frontend]
    Backend[Container App: FastAPI]
    Worker[Container App Job: Worker]
    Postgres[(Azure PostgreSQL)]
    Blob[(Blob Storage)]
    KeyVault[Key Vault]
    Monitor[Azure Monitor]
  end
  Users[Enterprise Users] --> Frontend
  Frontend --> Backend
  Backend --> Postgres
  Backend --> Blob
  Backend --> KeyVault
  Backend --> Monitor
  Worker --> Postgres
  Worker --> Blob
  Worker --> Monitor
  Backend --> Graph[Microsoft Graph]
  Backend --> SAP[SAP Gateway]
  Backend --> OpenAI[Azure OpenAI]"""

