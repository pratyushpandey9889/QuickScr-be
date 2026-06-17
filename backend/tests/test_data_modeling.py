from app.services.data_modeling import DataModelingService
from app.services.requirement_engineering import RequirementEngineeringService


def test_database_design_contains_sql_for_supported_dialects() -> None:
    text = "SAP supplier material delivery sequence call-off for Nagare JIT."
    requirements = RequirementEngineeringService().create_functional_requirements(text)

    design = DataModelingService().design_database(text, requirements)

    assert "CREATE TABLE source_document" in design.postgresql_sql
    assert "CREATE TABLE sequence_calloff" in design.postgresql_sql
    assert "uniqueidentifier" in design.sql_server_sql
    assert "char(36)" in design.mysql_sql


def test_validation_rules_are_generated_for_required_fields() -> None:
    design = DataModelingService().design_database("generic approval workflow", [])

    rules = DataModelingService().validation_rules(design.entities)

    assert rules
    assert any(rule.entity == "source_document" and rule.field == "source_name" for rule in rules)

