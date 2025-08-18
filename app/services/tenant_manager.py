from __future__ import annotations
import threading
from typing import Dict, Optional
from datetime import datetime

import neo4j
from sqlmodel import Session, select

from app.models.schemas import TenantCreate, TenantInfo
from app.core.db import engine
from app.models.db_models import TenantRow
from app.infrastructure.neo4j_docker import ensure_neo4j_for_tenant

class TenantManager:

    def __init__(self):
        self._lock = threading.RLock()
        self._drivers: Dict[str, neo4j.Driver] = {}


    def _row_to_tenant_create(self, row: TenantRow) -> TenantCreate:

        return TenantCreate(
            tenant_id=row.tenant_id,
            tenant_name=row.name,
            tenant_email=row.email,
            neo4j_uri=row.neo4j_uri,
            neo4j_user=row.neo4j_user,
            neo4j_password=row.neo4j_password,
        )

    # Update config on driver change
    def _config_tuple(self, payload: TenantCreate) -> tuple:
        return (payload.neo4j_uri, payload.neo4j_user, payload.neo4j_password)

    def register(self, payload: TenantCreate) -> TenantInfo:
        def _is_blank(s):
            return s is None or (isinstance(s, str) and not s.strip())

        with self._lock, Session(engine) as session:
            existing: Optional[TenantRow] = session.get(TenantRow, payload.tenant_id)

            # Check if Neo4j credentials exist
            needs_auto = _is_blank(getattr(payload, "neo4j_uri", None)) or \
                        _is_blank(getattr(payload, "neo4j_user", None)) or \
                        _is_blank(getattr(payload, "neo4j_password", None))

            if existing:
                old_cfg = (existing.neo4j_uri, existing.neo4j_user, existing.neo4j_password)

                if needs_auto:
                    # Si el payload trae password y quieres usarla, pásala; si no, None -> genera una segura
                    desired_pwd = None if _is_blank(getattr(payload, "neo4j_password", None)) else payload.neo4j_password

                    bolt_uri, auto_user, auto_pwd = ensure_neo4j_for_tenant(
                        payload.tenant_id,
                        existing_password=existing.neo4j_password or desired_pwd
                    )
                    existing.neo4j_uri = bolt_uri
                    existing.neo4j_user = auto_user

                    if not existing.neo4j_password:
                        existing.neo4j_password = auto_pwd
                        
                else:

                    existing.neo4j_uri = payload.neo4j_uri
                    existing.neo4j_user = payload.neo4j_user
                    existing.neo4j_password = payload.neo4j_password

                if getattr(payload, "name", None):
                    existing.name = payload.tenant_name
                if getattr(payload, "email", None):
                    existing.email = payload.tenant_email

                existing.updated_at = datetime.utcnow()
                session.add(existing)
                session.commit()

                new_cfg = (existing.neo4j_uri, existing.neo4j_user, existing.neo4j_password)
                if new_cfg != old_cfg and payload.tenant_id in self._drivers:
                    try:
                        self._drivers[payload.tenant_id].close()
                    except Exception:
                        pass
                    self._drivers.pop(payload.tenant_id, None)

            else:
                if needs_auto:
                    desired_pwd = None if _is_blank(getattr(payload, "neo4j_password", None)) else payload.neo4j_password
                    bolt_uri, auto_user, auto_pwd = ensure_neo4j_for_tenant(
                        payload.tenant_id, existing_password=desired_pwd
                    )
                    row = TenantRow(
                        tenant_id=payload.tenant_id,
                        name=getattr(payload, "name", None),
                        email=getattr(payload, "email", None),
                        neo4j_uri=bolt_uri,
                        neo4j_user=auto_user,
                        neo4j_password=desired_pwd or auto_pwd,
                    )
                else:
                    row = TenantRow(
                        tenant_id=payload.tenant_id,
                        name=getattr(payload, "name", None),
                        email=getattr(payload, "email", None),
                        neo4j_uri=payload.neo4j_uri,
                        neo4j_user=payload.neo4j_user,
                        neo4j_password=payload.neo4j_password,
                    )

                session.add(row)
                session.commit()

        return TenantInfo(tenant_id=payload.tenant_id)

    def get(self, tenant_id: str) -> Optional[TenantCreate]:
        with Session(engine) as session:
            row = session.get(TenantRow, tenant_id)
            if not row:
                return None
            return self._row_to_tenant_create(row)

    def get_driver(self, tenant_id: str) -> neo4j.Driver:
        with self._lock:
            if tenant_id in self._drivers:
                return self._drivers[tenant_id]

            with Session(engine) as session:
                row = session.get(TenantRow, tenant_id)
                if not row:
                    raise ValueError(f"Unknown tenant {tenant_id}")

                driver = neo4j.GraphDatabase.driver(
                    row.neo4j_uri, auth=(row.neo4j_user, row.neo4j_password)
                )
                self._drivers[tenant_id] = driver
                return driver

    def close_all(self):
        with self._lock:
            for d in self._drivers.values():
                try:
                    d.close()
                except Exception:
                    pass
            self._drivers.clear()

TENANTS = TenantManager()
