from __future__ import annotations
import os
from pathlib import Path
from secrets import token_urlsafe
from typing import Optional, Tuple, Dict

import docker
from docker.errors import NotFound, APIError, DockerException

from app.core.config import settings

def _client() -> docker.DockerClient:
    try:
        client = docker.from_env()
        client.ping()
        return client
    except DockerException as e:
        raise RuntimeError(f"No se puede conectar con Docker: {e}")

def _ensure_network(client: docker.DockerClient, name: str) -> None:
    try:
        client.networks.get(name)
    except NotFound:
        client.networks.create(name, driver="bridge")

def _tenant_dirs(tenant_id: str) -> Dict[str, Path]:
    base = settings.DB_DIR / "neo4j" / tenant_id
    data = base / "data"
    logs = base / "logs"
    plugins = base / "plugins"
    for d in (data, logs, plugins):
        d.mkdir(parents=True, exist_ok=True)
    return {"base": base, "data": data, "logs": logs, "plugins": plugins}

def _container_name(tenant_id: str) -> str:
    return f"engrammer-neo4j-{tenant_id}".replace("_", "-").lower()

def _port_mapping_for(container) -> Tuple[int, int]:
    container.reload()
    ports = container.attrs["NetworkSettings"]["Ports"]
    bolt = int(ports["7687/tcp"][0]["HostPort"])
    http = int(ports["7474/tcp"][0]["HostPort"])
    return bolt, http

def _env_vars(password: str) -> Dict[str, str]:
    env = {
        "NEO4J_AUTH": f"neo4j/{password}"
    }
    if settings.NEO4J_WITH_APOC:
        env.update({
            "NEO4J_PLUGINS": '["apoc"]',
            "NEO4J_dbms_security_procedures_unrestricted": "apoc.*"
            })
    return env

def _volume_binds(dirs: Dict[str, Path]) -> Dict[str, dict]:
    return {
        dirs["data"].as_posix(): {"bind": "/data", "mode": "rw"},
        dirs["logs"].as_posix(): {"bind": "/logs", "mode": "rw"},
        dirs["plugins"].as_posix(): {"bind": "/plugins", "mode": "rw"},
    }

def ensure_neo4j_for_tenant(tenant_id: str, existing_password: Optional[str]) -> Tuple[str, str, str]:

    client = _client()
    _ensure_network(client, settings.DOCKER_NETWORK)

    dirs = _tenant_dirs(tenant_id)
    name = _container_name(tenant_id)


    container = None
    try:
        container = client.containers.get(name)
        if container.status != "running":
            container.start()
    except NotFound:
        pass

    if container is None:

        password = existing_password or "123456789"

        ports = {"7687/tcp": None, "7474/tcp": None}

        container = client.containers.run(
            image=settings.NEO4J_IMAGE,
            name=name,
            detach=True,
            environment=_env_vars(password),
            ports=ports,
            volumes=_volume_binds(dirs),
            network=settings.DOCKER_NETWORK,
            restart_policy={"Name": "unless-stopped"},
        )
    else:
        password = existing_password or "unknown"

    bolt_port, http_port = _port_mapping_for(container)
    bolt_uri = f"bolt://localhost:{bolt_port}"

    return bolt_uri, "neo4j", password
