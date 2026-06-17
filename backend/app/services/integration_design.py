from textwrap import dedent

from app.domain.schemas import IntegrationDesign, IntegrationType


class IntegrationDesignService:
    def design(self, text: str) -> list[IntegrationDesign]:
        lower = text.lower()
        integrations = [
            IntegrationDesign(
                integration_type=IntegrationType.POSTGRESQL,
                purpose="Persist documents, generated artifacts, requirements, audit logs, conversations, and operational state.",
                protocol="PostgreSQL wire protocol over TLS",
                authentication="Managed identity or rotated database credentials from Key Vault",
                data_flow=[
                    "API writes source document metadata and generated solution records",
                    "Worker writes vector chunk references and integration events",
                    "Audit events are append-only",
                ],
                retry_policy="Use transaction boundaries and idempotency keys; retry transient failures with exponential backoff.",
                code_example=self._postgres_code(),
            )
        ]
        if "sharepoint" in lower:
            integrations.append(
                IntegrationDesign(
                    integration_type=IntegrationType.SHAREPOINT,
                    purpose="Retrieve documents, perform search, and extract SharePoint metadata for traceable source control.",
                    protocol="Microsoft Graph REST API",
                    authentication="Azure AD application permission with Sites.Selected or delegated user token",
                    data_flow=[
                        "Search document library by configured path, content type, metadata, or keyword",
                        "Download file content through Graph driveItem content endpoint",
                        "Persist SharePoint site, drive, item, etag, webUrl, and modified timestamp",
                        "Queue changed files for re-indexing when etag changes",
                    ],
                    retry_policy="Retry 429 and 5xx responses using Retry-After header and exponential backoff.",
                    code_example=self._sharepoint_code(),
                )
            )
        if "sap" in lower:
            integrations.extend(
                [
                    IntegrationDesign(
                        integration_type=IntegrationType.SAP_ODATA,
                        purpose="Read SAP master data and transactional status through SAP Gateway services.",
                        protocol="OData v2/v4 over HTTPS",
                        authentication="OAuth2 client credentials or SAP technical user with principal propagation where available",
                        data_flow=[
                            "Read material, supplier, plant, purchase order, delivery, and production sequence data",
                            "Validate generated payloads against SAP business object keys",
                            "Persist SAP response status and correlation IDs for reconciliation",
                        ],
                        retry_policy="Retry idempotent GET operations; for writes use idempotency keys and SAP document status checks.",
                        code_example=self._sap_odata_code(),
                    ),
                    IntegrationDesign(
                        integration_type=IntegrationType.SAP_RFC,
                        purpose="Call legacy BAPIs or RFC-enabled function modules when OData service coverage is unavailable.",
                        protocol="SAP RFC through gateway connector service",
                        authentication="SAP SNC or technical destination managed in secure connector runtime",
                        data_flow=[
                            "Normalize internal command into RFC input parameters",
                            "Call connector service from backend",
                            "Map SAP RETURN table messages into domain exceptions",
                        ],
                        retry_policy="Retry only RFCs classified as read-only or idempotent; otherwise reconcile before retry.",
                        code_example=self._sap_rfc_code(),
                    ),
                ]
            )
        if any(keyword in lower for keyword in ["agent", "embedding", "openai", "question", "chat"]):
            integrations.extend(
                [
                    IntegrationDesign(
                        integration_type=IntegrationType.AZURE_OPENAI,
                        purpose="Create source-grounded answers and generated implementation details.",
                        protocol="Azure OpenAI REST API",
                        authentication="Azure AD managed identity or Azure OpenAI API key in Key Vault",
                        data_flow=[
                            "Chunk source documents and create embeddings",
                            "Retrieve relevant chunks for user question",
                            "Generate answer with citations and conversation memory",
                        ],
                        retry_policy="Retry transient rate limits with exponential backoff and request budgeting.",
                        code_example=self._azure_openai_code(),
                    ),
                    IntegrationDesign(
                        integration_type=IntegrationType.PINECONE,
                        purpose="Store vector embeddings for retrieval augmented generation at scale.",
                        protocol="Pinecone HTTPS API",
                        authentication="Pinecone API key from Key Vault",
                        data_flow=[
                            "Upsert chunk vectors with source document metadata",
                            "Query vectors by embedding and tenant filter",
                            "Return source citations for answer grounding",
                        ],
                        retry_policy="Retry upserts and queries on 429 or 5xx with exponential backoff.",
                        code_example=self._pinecone_code(),
                    ),
                ]
            )
        return integrations

    def _postgres_code(self) -> str:
        return dedent(
            """
            from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

            engine = create_async_engine(settings.database_url, pool_pre_ping=True)
            SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

            async with SessionLocal() as session:
                async with session.begin():
                    session.add(model)
            """
        ).strip()

    def _sharepoint_code(self) -> str:
        return dedent(
            """
            import httpx

            async def download_sharepoint_item(token: str, site_id: str, drive_id: str, item_id: str) -> bytes:
                url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{item_id}/content"
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
                    response.raise_for_status()
                    return response.content
            """
        ).strip()

    def _sap_odata_code(self) -> str:
        return dedent(
            """
            import httpx

            async def read_sap_material(base_url: str, token: str, material_number: str) -> dict:
                url = f"{base_url}/sap/opu/odata/sap/API_PRODUCT_SRV/A_Product('{material_number}')"
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
                    response.raise_for_status()
                    return response.json()
            """
        ).strip()

    def _sap_rfc_code(self) -> str:
        return dedent(
            """
            import httpx

            async def call_rfc_connector(connector_url: str, payload: dict) -> dict:
                async with httpx.AsyncClient(timeout=45) as client:
                    response = await client.post(f"{connector_url}/rfc", json=payload)
                    response.raise_for_status()
                    result = response.json()
                if any(message.get("TYPE") in {"A", "E"} for message in result.get("RETURN", [])):
                    raise ValueError(f"SAP RFC failed: {result['RETURN']}")
                return result
            """
        ).strip()

    def _azure_openai_code(self) -> str:
        return dedent(
            """
            from openai import AsyncAzureOpenAI

            client = AsyncAzureOpenAI(
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version="2024-06-01",
            )
            response = await client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "system", "content": "Answer with citations."}, {"role": "user", "content": question}],
            )
            """
        ).strip()

    def _pinecone_code(self) -> str:
        return dedent(
            """
            from pinecone import Pinecone

            pc = Pinecone(api_key=settings.pinecone_api_key)
            index = pc.Index(settings.pinecone_index)
            index.upsert(vectors=[{"id": chunk_id, "values": embedding, "metadata": metadata}])
            matches = index.query(vector=query_embedding, top_k=5, include_metadata=True)
            """
        ).strip()

