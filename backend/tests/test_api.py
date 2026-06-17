from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_allows_localhost_and_loopback_frontend_origins() -> None:
    client = TestClient(create_app())

    for origin in ("http://localhost:3000", "http://127.0.0.1:3000"):
        response = client.options(
            "/api/v1/analysis/document",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
            },
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin


def test_text_analysis_endpoint() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/analysis/text",
        json={
            "source_name": "sample.txt",
            "content": "SAP SharePoint Nagare sequence delivery process with supplier call-offs and AI agent citations.",
            "accuracy_level": "high",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_name"] == "sample.txt"
    assert payload["accuracy_profile"]["level"] == "high"
    assert payload["accuracy_profile"]["review_required"] is True
    assert payload["nagare_rules"] is not None
    assert len(payload["api_design"]) > 0


def test_document_upload_get_and_list_endpoints() -> None:
    client = TestClient(create_app())

    upload = client.post(
        "/api/v1/analysis/document",
        data={"accuracy_level": "audit"},
        files={"file": ("sample.txt", b"SharePoint SAP Nagare sequence delivery process with supplier call-offs.", "text/plain")},
    )
    assert upload.status_code == 200
    upload_payload = upload.json()
    solution_id = upload_payload["solution_id"]
    assert upload_payload["accuracy_profile"]["level"] == "audit"

    fetched = client.get(f"/api/v1/analysis/{solution_id}")
    listed = client.get("/api/v1/analysis")

    assert fetched.status_code == 200
    assert listed.status_code == 200
    assert any(item["solution_id"] == solution_id for item in listed.json())


def test_missing_solution_returns_404() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/analysis/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
