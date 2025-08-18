from fastapi import Header, HTTPException

async def get_tenant_id(x_tenant_id: str | None = Header(default=None)) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Missing X-Tenant-Id header")
    return x_tenant_id