from fastapi import APIRouter, HTTPException
from app.models.schemas import TenantCreate, TenantInfo
from app.services.tenant_manager import TENANTS

router = APIRouter()

@router.post("/users/register", response_model=TenantInfo)
def register_tenant(payload: TenantCreate):
    if not payload.tenant_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    return TENANTS.register(payload)
