# API Design

## Core Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | Service health check |
| POST | `/api/v1/analysis/text` | Analyze pasted or API-submitted text |
| POST | `/api/v1/analysis/document` | Analyze uploaded TXT, Markdown, CSV, JSON, PDF, DOCX, or XLSX |
| GET | `/api/v1/analysis/{solution_id}` | Retrieve one generated solution |
| GET | `/api/v1/analysis` | List generated solutions in the current repository |

## Validation Rules

- Text analysis requires at least 20 characters.
- Document uploads require a supported extension and extractable text.
- `accuracy_level` accepts `fast`, `balanced`, `high`, or `audit`; omitted requests default to `balanced`.
- Protected APIs require `documents:write` or `solutions:read` permissions.
- Every generated entity API must validate required fields, UUID path parameters, referential integrity, and audited deletes.

## Accuracy Profile

Text requests include `accuracy_level` in JSON. Document requests include `accuracy_level` as multipart form data. Responses include:

| Field | Meaning |
| --- | --- |
| `level` | Selected accuracy level |
| `target_confidence` | Target confidence for the selected mode |
| `estimated_confidence` | Heuristic confidence estimate based on source completeness signals |
| `validation_depth` | Validation scope applied by the agent |
| `citation_policy` | Citation requirement for generated claims |
| `retrieval_top_k` | Retrieval depth for AI-agent context search |
| `model_temperature` | Recommended generation temperature |
| `review_required` | Whether human review is required before production export |
| `enabled_checks` | Active quality gates |
| `escalation_rules` | Conditions that require reviewer attention |

## Error Handling

| Status | Meaning |
| --- | --- |
| 400 | Invalid request, unsupported file type, or empty extracted document |
| 401 | Missing or invalid bearer token |
| 403 | Authenticated principal lacks required permission |
| 404 | Generated solution or resource not found |
| 409 | Resource conflict or delete blocked by dependencies |
| 422 | Schema validation error |
| 500 | Unhandled service failure, logged with correlation ID |
