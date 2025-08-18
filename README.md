# GraphRAG Pipelines API (Multi-tenant)

Expose pipelines as REST endpoints with multi-tenant isolation.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Register a tenant

```bash
curl -X POST http://localhost:8000/v1/users/register \
 -H 'Content-Type: application/json' \
 -d '{
  "tenant_id": "",
  "neo4j_uri": "",
  "neo4j_user": "",
  "neo4j_password": ""
 }'
```

## List pipelines

```bash
curl http://localhost:8000/v1/pipelines
```

## Invoke pipeline (chat turn)

```bash
curl -X POST http://localhost:8000/v1/pipelines/invoke \
 -H 'Content-Type: application/json' \
 -d '{
  "tenant_id": "user123",
  "pipeline_id": "pipeline_guardar",
  "session_id": "conv-a",
  "user_message": "Fui a un concierto ayer con Ana.",
  "messages": [{"role":"user","content":"Fui a un concierto ayer con Ana."}],
 }'
```

```bash
curl -X POST http://localhost:8000/v1/pipelines/invoke \
 -H 'Content-Type: application/json' \
 -d '{
  "tenant_id": "user123",
  "pipeline_id": "pipeline_guardar",
  "user_message": "Fui a un concierto ayer con Ana."
 }'
```

## End conversation (force finalize & store)

```bash
curl -X POST http://localhost:8000/v1/pipelines/end \
 -H 'Content-Type: application/json' \
 -d '{
  "tenant_id": "user123",
  "pipeline_id": "memory",
  "session_id": "conv-a"
 }'
```