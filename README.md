# Engrammer Project

Engrammer is a multi-tenant API built on **FastAPI** and **Neo4j GraphRAG** pipelines to help manage and query user memories.

## 🚀 Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## 🔑 Authentication & User Management

User management is handled via **Keycloak**.  
The Keycloak admin console can be found at:

👉 [http://193.146.75.247:8080/admin/engrammer/console](http://193.146.75.247:8080/admin/engrammer/console)

⚠️ Access requires a grant. To request access, please contact: **sftobias@ifca.unican.es**

## 📡 API Endpoints

A **DEV version** of the API is available at:

👉 [http://193.146.75.247:8000/docs#](http://193.146.75.247:8000/docs#)

⚠️ This is still a project in progress, so errors, bugs, and downtimes may occur.

## 🧩 Example Usage

### Register a tenant
```bash
curl -X POST http://localhost:8000/v1/users/register  -H 'Content-Type: application/json'  -d '{
  "tenant_id": "example_tenant",
  "neo4j_uri": "",
  "neo4j_user": "",
  "neo4j_password": ""
 }'
```

### List pipelines
```bash
curl http://localhost:8000/v1/pipelines
```

### Invoke pipeline (chat turn)
To call this endpoint you must provide a **Bearer token** in the Authorization header (do not pass `tenant_id` directly).

```bash
curl -X POST http://localhost:8000/v1/pipelines/invoke  -H "Authorization: Bearer <ACCESS_TOKEN>"  -H "Content-Type: application/json"  -d '{
  "pipeline_id": "pipeline_guardar",
  "session_id": "conv-a",
  "user_message": "Fui a un concierto ayer con Ana."
 }'
```

### End conversation
Same rule applies: use **Bearer token** instead of `tenant_id`.

```bash
curl -X POST http://localhost:8000/v1/pipelines/end  -H "Authorization: Bearer <ACCESS_TOKEN>"  -H "Content-Type: application/json"  -d '{
  "pipeline_id": "memory",
  "session_id": "conv-a"
 }'
```

## ⚠️ Notes

- This repository is under **active development**. Expect frequent changes.
- For bug reports or contributions, please open a GitHub issue or pull request.
