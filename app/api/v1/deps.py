# app/api/v1/deps.py
from __future__ import annotations
from typing import Any, Dict

import jwt
from jwt import PyJWKClient, InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=True)

def _get_jwk_client() -> PyJWKClient:
    if not settings.KEYCLOAK_JWKS_URL:
        raise RuntimeError("Keycloak no está configurado (falta KEYCLOAK_JWKS_URL).")
    return PyJWKClient(settings.KEYCLOAK_JWKS_URL)

def _decode_and_validate(token: str) -> Dict[str, Any]:
    try:
        signing_key = _get_jwk_client().get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.KEYCLOAK_AUDIENCE or settings.KEYCLOAK_CLIENT_ID,
            issuer=settings.KEYCLOAK_ISSUER,
            options={
                "require": ["exp", "iss", "aud"],
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
                "verify_aud": True,
            },
        )
        return claims
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_jwt_claims(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Dict[str, Any]:
    token = credentials.credentials
    return _decode_and_validate(token)

def get_current_tenant_id(claims: Dict[str, Any] = Depends(get_jwt_claims)) -> str:
    tenant_id = claims.get("sub")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Missing 'sub' claim in token")
    return tenant_id
