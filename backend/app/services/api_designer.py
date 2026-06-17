from app.domain.schemas import ApiEndpointDesign, EntityModel


class ApiDesignerService:
    def design_for_entities(self, entities: list[EntityModel]) -> list[ApiEndpointDesign]:
        endpoints: list[ApiEndpointDesign] = []
        for entity in entities:
            resource = entity.name.replace("_", "-")
            schema = self._schema(entity)
            endpoints.extend(
                [
                    ApiEndpointDesign(
                        method="GET",
                        endpoint=f"/api/v1/{resource}",
                        request_schema=None,
                        response_schema={"type": "array", "items": schema},
                        validation_rules=["Caller must have read permission for the resource"],
                        errors={"401": "Unauthorized", "403": "Forbidden"},
                    ),
                    ApiEndpointDesign(
                        method="GET",
                        endpoint=f"/api/v1/{resource}/{{id}}",
                        request_schema=None,
                        response_schema=schema,
                        validation_rules=["id must be a valid UUID"],
                        errors={"401": "Unauthorized", "403": "Forbidden", "404": "Resource not found"},
                    ),
                    ApiEndpointDesign(
                        method="POST",
                        endpoint=f"/api/v1/{resource}",
                        request_schema=schema,
                        response_schema=schema,
                        validation_rules=self._validation_rules(entity),
                        errors={"400": "Validation failed", "401": "Unauthorized", "403": "Forbidden", "409": "Conflict"},
                    ),
                    ApiEndpointDesign(
                        method="PUT",
                        endpoint=f"/api/v1/{resource}/{{id}}",
                        request_schema=schema,
                        response_schema=schema,
                        validation_rules=["id must exist"] + self._validation_rules(entity),
                        errors={"400": "Validation failed", "401": "Unauthorized", "403": "Forbidden", "404": "Resource not found"},
                    ),
                    ApiEndpointDesign(
                        method="DELETE",
                        endpoint=f"/api/v1/{resource}/{{id}}",
                        request_schema=None,
                        response_schema={"status": "deleted", "id": "uuid"},
                        validation_rules=["id must exist", "delete must be audited"],
                        errors={"401": "Unauthorized", "403": "Forbidden", "404": "Resource not found", "409": "Delete blocked by dependencies"},
                    ),
                ]
            )
        return endpoints

    def _schema(self, entity: EntityModel) -> dict[str, object]:
        return {
            "type": "object",
            "properties": {
                attribute.name: {"type": self._json_type(attribute.data_type)}
                for attribute in entity.attributes
            },
            "required": [
                attribute.name
                for attribute in entity.attributes
                if not attribute.nullable and "primary key" not in attribute.constraints
            ],
        }

    def _json_type(self, data_type: str) -> str:
        if data_type.startswith("integer"):
            return "integer"
        if data_type.startswith("numeric"):
            return "number"
        if data_type in {"jsonb", "json"}:
            return "object"
        return "string"

    def _validation_rules(self, entity: EntityModel) -> list[str]:
        return [
            f"{attribute.name} is required"
            for attribute in entity.attributes
            if not attribute.nullable and "primary key" not in attribute.constraints
        ]

