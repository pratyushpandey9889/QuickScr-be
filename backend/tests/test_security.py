import anyio
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, SecurityScopes
from jose import jwt

from app.core.config import get_settings
from app.core.security import Principal, Role, get_current_principal


def test_principal_permissions_union_roles() -> None:
    principal = Principal(
        subject="1",
        email="architect@example.com",
        roles=(Role.ARCHITECT, Role.VIEWER),
    )

    assert "documents:write" in principal.permissions
    assert "solutions:read" in principal.permissions


def test_local_environment_allows_admin_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "local")
    get_settings.cache_clear()

    principal = anyio.run(get_current_principal, SecurityScopes(scopes=["documents:write"]), None)

    assert principal.subject == "local-user"
    assert Role.ADMIN in principal.roles


def test_non_local_environment_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "prod")
    get_settings.cache_clear()

    with pytest.raises(HTTPException) as exc:
        anyio.run(get_current_principal, SecurityScopes(scopes=[]), None)

    assert exc.value.status_code == 401


def test_rejects_missing_permissions(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "prod")
    monkeypatch.delenv("JWT_AUDIENCE", raising=False)
    monkeypatch.delenv("JWT_ISSUER", raising=False)
    get_settings.cache_clear()
    token = jwt.encode({"sub": "viewer", "roles": ["viewer"], "email": "viewer@example.com"}, "secret")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc:
        anyio.run(get_current_principal, SecurityScopes(scopes=["documents:write"]), credentials)

    assert exc.value.status_code == 403

