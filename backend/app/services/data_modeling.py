import re

from app.domain.schemas import (
    DatabaseDesign,
    EntityAttribute,
    EntityModel,
    FunctionalRequirement,
    Relationship,
    ValidationRule,
)


class DataModelingService:
    base_entities = [
        EntityModel(
            name="source_document",
            description="Document submitted or retrieved for analysis",
            attributes=[
                EntityAttribute(name="id", data_type="uuid", constraints=["primary key"]),
                EntityAttribute(name="source_name", data_type="varchar(255)"),
                EntityAttribute(name="source_type", data_type="varchar(50)"),
                EntityAttribute(name="content_hash", data_type="varchar(128)"),
                EntityAttribute(name="created_by", data_type="varchar(255)"),
                EntityAttribute(name="created_at", data_type="timestamp"),
            ],
            indexes=["idx_source_document_content_hash", "idx_source_document_created_at"],
        ),
        EntityModel(
            name="generated_solution",
            description="Complete generated implementation package for one source document",
            attributes=[
                EntityAttribute(name="id", data_type="uuid", constraints=["primary key"]),
                EntityAttribute(name="source_document_id", data_type="uuid", constraints=["foreign key"]),
                EntityAttribute(name="executive_summary", data_type="text"),
                EntityAttribute(name="status", data_type="varchar(50)"),
                EntityAttribute(name="created_at", data_type="timestamp"),
                EntityAttribute(name="updated_at", data_type="timestamp"),
            ],
            indexes=["idx_generated_solution_source_document_id", "idx_generated_solution_status"],
        ),
        EntityModel(
            name="requirement",
            description="Functional or non-functional requirement generated from source content",
            attributes=[
                EntityAttribute(name="id", data_type="uuid", constraints=["primary key"]),
                EntityAttribute(name="generated_solution_id", data_type="uuid", constraints=["foreign key"]),
                EntityAttribute(name="requirement_code", data_type="varchar(50)"),
                EntityAttribute(name="requirement_type", data_type="varchar(50)"),
                EntityAttribute(name="description", data_type="text"),
                EntityAttribute(name="priority", data_type="varchar(20)"),
                EntityAttribute(name="business_rule", data_type="text", nullable=True),
                EntityAttribute(name="created_at", data_type="timestamp"),
            ],
            indexes=["idx_requirement_solution_id", "idx_requirement_code"],
        ),
        EntityModel(
            name="audit_log",
            description="Immutable audit event for user actions, generated decisions, and integration calls",
            attributes=[
                EntityAttribute(name="id", data_type="uuid", constraints=["primary key"]),
                EntityAttribute(name="actor", data_type="varchar(255)"),
                EntityAttribute(name="action", data_type="varchar(100)"),
                EntityAttribute(name="resource_type", data_type="varchar(100)"),
                EntityAttribute(name="resource_id", data_type="uuid", nullable=True),
                EntityAttribute(name="metadata", data_type="jsonb"),
                EntityAttribute(name="created_at", data_type="timestamp"),
            ],
            indexes=["idx_audit_log_actor", "idx_audit_log_created_at"],
        ),
    ]

    def design_database(self, text: str, requirements: list[FunctionalRequirement]) -> DatabaseDesign:
        entities = [entity.model_copy(deep=True) for entity in self.base_entities]
        entities.extend(self._domain_entities(text))
        relationships = self._relationships(entities)
        return DatabaseDesign(
            entities=entities,
            relationships=relationships,
            er_diagram_mermaid=self._to_mermaid(entities, relationships),
            postgresql_sql=self._to_sql("postgresql", entities, relationships),
            sql_server_sql=self._to_sql("sqlserver", entities, relationships),
            mysql_sql=self._to_sql("mysql", entities, relationships),
        )

    def validation_rules(self, entities: list[EntityModel]) -> list[ValidationRule]:
        rules: list[ValidationRule] = []
        counter = 1
        for entity in entities:
            for attribute in entity.attributes:
                if not attribute.nullable and "primary key" not in attribute.constraints:
                    rules.append(
                        ValidationRule(
                            rule_id=f"VR-{counter:03d}",
                            entity=entity.name,
                            field=attribute.name,
                            condition="value is not null and not empty",
                            error_message=f"{entity.name}.{attribute.name} is required",
                        )
                    )
                    counter += 1
        return rules

    def _domain_entities(self, text: str) -> list[EntityModel]:
        lower = text.lower()
        entities: list[EntityModel] = []
        if any(keyword in lower for keyword in ["sap", "material", "supplier", "delivery", "sequence", "jit", "nagare"]):
            entities.extend(
                [
                    EntityModel(
                        name="material",
                        description="Material or part used in production or delivery sequence",
                        attributes=[
                            EntityAttribute(name="id", data_type="uuid", constraints=["primary key"]),
                            EntityAttribute(name="material_number", data_type="varchar(80)"),
                            EntityAttribute(name="description", data_type="varchar(255)"),
                            EntityAttribute(name="uom", data_type="varchar(20)"),
                            EntityAttribute(name="sap_plant", data_type="varchar(20)"),
                            EntityAttribute(name="created_at", data_type="timestamp"),
                        ],
                        indexes=["idx_material_number", "idx_material_sap_plant"],
                    ),
                    EntityModel(
                        name="supplier",
                        description="Supplier responsible for sequenced delivery",
                        attributes=[
                            EntityAttribute(name="id", data_type="uuid", constraints=["primary key"]),
                            EntityAttribute(name="supplier_code", data_type="varchar(80)"),
                            EntityAttribute(name="name", data_type="varchar(255)"),
                            EntityAttribute(name="lead_time_minutes", data_type="integer"),
                            EntityAttribute(name="created_at", data_type="timestamp"),
                        ],
                        indexes=["idx_supplier_code"],
                    ),
                    EntityModel(
                        name="sequence_calloff",
                        description="JIT or Nagare call-off generated from production sequence demand",
                        attributes=[
                            EntityAttribute(name="id", data_type="uuid", constraints=["primary key"]),
                            EntityAttribute(name="material_id", data_type="uuid", constraints=["foreign key"]),
                            EntityAttribute(name="supplier_id", data_type="uuid", constraints=["foreign key"]),
                            EntityAttribute(name="sequence_number", data_type="integer"),
                            EntityAttribute(name="required_quantity", data_type="numeric(18,3)"),
                            EntityAttribute(name="required_at", data_type="timestamp"),
                            EntityAttribute(name="delivery_window_start", data_type="timestamp"),
                            EntityAttribute(name="delivery_window_end", data_type="timestamp"),
                            EntityAttribute(name="status", data_type="varchar(50)"),
                            EntityAttribute(name="created_at", data_type="timestamp"),
                        ],
                        indexes=["idx_calloff_sequence", "idx_calloff_required_at", "idx_calloff_status"],
                    ),
                ]
            )
        if "sharepoint" in lower:
            entities.append(
                EntityModel(
                    name="sharepoint_source",
                    description="SharePoint document location and retrieval metadata",
                    attributes=[
                        EntityAttribute(name="id", data_type="uuid", constraints=["primary key"]),
                        EntityAttribute(name="source_document_id", data_type="uuid", constraints=["foreign key"]),
                        EntityAttribute(name="site_id", data_type="varchar(255)"),
                        EntityAttribute(name="drive_id", data_type="varchar(255)"),
                        EntityAttribute(name="item_id", data_type="varchar(255)"),
                        EntityAttribute(name="web_url", data_type="text"),
                        EntityAttribute(name="etag", data_type="varchar(255)"),
                        EntityAttribute(name="created_at", data_type="timestamp"),
                    ],
                    indexes=["idx_sharepoint_item", "idx_sharepoint_source_document_id"],
                )
            )
        if "conversation" in lower or "agent" in lower or "embedding" in lower:
            entities.extend(
                [
                    EntityModel(
                        name="document_chunk",
                        description="Chunked source content used for retrieval augmented generation",
                        attributes=[
                            EntityAttribute(name="id", data_type="uuid", constraints=["primary key"]),
                            EntityAttribute(name="source_document_id", data_type="uuid", constraints=["foreign key"]),
                            EntityAttribute(name="chunk_index", data_type="integer"),
                            EntityAttribute(name="content", data_type="text"),
                            EntityAttribute(name="embedding_provider", data_type="varchar(80)"),
                            EntityAttribute(name="vector_id", data_type="varchar(255)"),
                            EntityAttribute(name="created_at", data_type="timestamp"),
                        ],
                        indexes=["idx_document_chunk_source", "idx_document_chunk_vector_id"],
                    ),
                    EntityModel(
                        name="conversation_turn",
                        description="AI agent conversation history with source-grounded answers",
                        attributes=[
                            EntityAttribute(name="id", data_type="uuid", constraints=["primary key"]),
                            EntityAttribute(name="session_id", data_type="uuid"),
                            EntityAttribute(name="role", data_type="varchar(30)"),
                            EntityAttribute(name="content", data_type="text"),
                            EntityAttribute(name="citations", data_type="jsonb"),
                            EntityAttribute(name="created_at", data_type="timestamp"),
                        ],
                        indexes=["idx_conversation_turn_session", "idx_conversation_turn_created_at"],
                    ),
                ]
            )
        return self._dedupe(entities)

    def _relationships(self, entities: list[EntityModel]) -> list[Relationship]:
        entity_names = {entity.name for entity in entities}
        relationships = [
            Relationship(
                source_entity="generated_solution",
                target_entity="source_document",
                cardinality="many-to-one",
                foreign_key="source_document_id",
                description="Each generated solution belongs to one source document.",
            ),
            Relationship(
                source_entity="requirement",
                target_entity="generated_solution",
                cardinality="many-to-one",
                foreign_key="generated_solution_id",
                description="Each requirement belongs to one generated solution.",
            ),
        ]
        optional = [
            ("sequence_calloff", "material", "material_id"),
            ("sequence_calloff", "supplier", "supplier_id"),
            ("sharepoint_source", "source_document", "source_document_id"),
            ("document_chunk", "source_document", "source_document_id"),
        ]
        for source, target, foreign_key in optional:
            if source in entity_names and target in entity_names:
                relationships.append(
                    Relationship(
                        source_entity=source,
                        target_entity=target,
                        cardinality="many-to-one",
                        foreign_key=foreign_key,
                        description=f"{source} references {target}.",
                    )
                )
        return relationships

    def _to_mermaid(self, entities: list[EntityModel], relationships: list[Relationship]) -> str:
        lines = ["erDiagram"]
        for relationship in relationships:
            lines.append(f"  {relationship.target_entity} ||--o{{ {relationship.source_entity} : \"has\"")
        for entity in entities:
            lines.append(f"  {entity.name} {{")
            for attribute in entity.attributes:
                mermaid_type = re.sub(r"[^A-Za-z0-9_]", "_", attribute.data_type)
                key = " PK" if "primary key" in attribute.constraints else ""
                key = " FK" if "foreign key" in attribute.constraints else key
                lines.append(f"    {mermaid_type} {attribute.name}{key}")
            lines.append("  }")
        return "\n".join(lines)

    def _to_sql(self, dialect: str, entities: list[EntityModel], relationships: list[Relationship]) -> str:
        statements: list[str] = []
        for entity in entities:
            column_lines = []
            for attribute in entity.attributes:
                column_lines.append(self._column_sql(dialect, attribute))
            for relationship in relationships:
                if relationship.source_entity == entity.name:
                    column_lines.append(
                        f"  CONSTRAINT fk_{entity.name}_{relationship.target_entity} "
                        f"FOREIGN KEY ({relationship.foreign_key}) REFERENCES {relationship.target_entity}(id)"
                    )
            statements.append(f"CREATE TABLE {entity.name} (\n" + ",\n".join(column_lines) + "\n);")
            for index in entity.indexes:
                indexed_column = self._infer_index_column(index, entity)
                statements.append(f"CREATE INDEX {index} ON {entity.name} ({indexed_column});")
        return "\n\n".join(statements)

    def _column_sql(self, dialect: str, attribute: EntityAttribute) -> str:
        sql_type = self._map_type(dialect, attribute.data_type)
        constraints: list[str] = []
        if "primary key" in attribute.constraints:
            constraints.append("PRIMARY KEY")
        if not attribute.nullable and "primary key" not in attribute.constraints:
            constraints.append("NOT NULL")
        return f"  {attribute.name} {sql_type} {' '.join(constraints)}".rstrip()

    def _map_type(self, dialect: str, data_type: str) -> str:
        if dialect == "postgresql":
            return data_type
        if dialect == "sqlserver":
            mapping = {"uuid": "uniqueidentifier", "jsonb": "nvarchar(max)", "text": "nvarchar(max)", "timestamp": "datetime2"}
            return mapping.get(data_type, data_type.replace("varchar", "nvarchar"))
        if dialect == "mysql":
            mapping = {"uuid": "char(36)", "jsonb": "json", "timestamp": "datetime"}
            return mapping.get(data_type, data_type)
        return data_type

    def _infer_index_column(self, index: str, entity: EntityModel) -> str:
        for attribute in entity.attributes:
            if attribute.name in index:
                return attribute.name
        return entity.attributes[0].name

    def _dedupe(self, entities: list[EntityModel]) -> list[EntityModel]:
        seen: set[str] = set()
        deduped: list[EntityModel] = []
        for entity in entities:
            if entity.name not in seen:
                deduped.append(entity)
                seen.add(entity.name)
        return deduped

