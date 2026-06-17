from dataclasses import dataclass
from enum import StrEnum

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from jose import JWTError, jwt

from app.core.config import get_settings


class Role(StrEnum):
    ADMIN = "admin"
    ARCHITECT = "architect"
    ANALYST = "analyst"
    VIEWER = "viewer"


ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.ADMIN: {"documents:read", "documents:write", "solutions:read", "solutions:write", "admin"},
    Role.ARCHITECT: {"documents:read", "documents:write", "solutions:read", "solutions:write"},
    Role.ANALYST: {"documents:read", "documents:write", "solutions:read"},
    Role.VIEWER: {"documents:read", "solutions:read"},
}


@dataclass(frozen=True)
class Principal:
    subject: str
    email: str
    roles: tuple[Role, ...]

    @property
    def permissions(self) -> set[str]:
        permissions: set[str] = set()
        for role in self.roles:
            permissions.update(ROLE_PERMISSIONS[role])
        return permissions


bearer = HTTPBearer(auto_error=False)


async def get_current_principal(
    security_scopes: SecurityScopes,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> Principal:
    settings = get_settings()
    if settings.app_env == "local" and credentials is None:
        return Principal(
            subject="local-user",
            email="local@quickscribe.dev",
            roles=(Role.ADMIN,),
        )

    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    try:
        claims = jwt.get_unverified_claims(credentials.credentials)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid bearer token") from exc

    if settings.jwt_audience and claims.get("aud") != settings.jwt_audience:
        raise HTTPException(status_code=401, detail="Invalid token audience")
    if settings.jwt_issuer and claims.get("iss") != settings.jwt_issuer:
        raise HTTPException(status_code=401, detail="Invalid token issuer")

    raw_roles = claims.get("roles") or claims.get("groups") or ["viewer"]
    roles = tuple(Role(role) for role in raw_roles if role in Role._value2member_map_)
    principal = Principal(
        subject=str(claims.get("sub", "")),
        email=str(claims.get("preferred_username", claims.get("email", ""))),
        roles=roles or (Role.VIEWER,),
    )

    missing_scopes = [scope for scope in security_scopes.scopes if scope not in principal.permissions]
    if missing_scopes:
        raise HTTPException(status_code=403, detail=f"Missing permissions: {', '.join(missing_scopes)}")
    return principal


def require_permissions(*permissions: str):
    async def dependency(
        principal: Principal = Security(get_current_principal, scopes=list(permissions)),
    ) -> Principal:
        return principal

    return dependency
