---
name: testing-and-coverage
description: Use when writing, maintaining, or executing automated tests, managing CSV test fixtures, enforcing Test-Driven Development (TDD), and auditing code coverage thresholds (>85% backend, >80% frontend).
---

# Testing & Coverage Skill

## 1. Overview & Purpose
This skill operationalizes the complete Test Strategy defined in Section 7 of [BRD.md](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/BRD.md).

It provides standardized commands, test structure guidelines, edge-case fixture patterns, and coverage requirements for both the Python/FastAPI backend and the Angular frontend.

---

## 2. Test-Driven Development (TDD) Workflow

Every new feature or bug fix must follow the Red-Green-Refactor cycle:
1. **Red:** Write a failing test in the appropriate test suite capturing the requirement or bug condition.
2. **Green:** Write the minimal implementation code to make the test pass.
3. **Refactor:** Clean up code, optimize performance, and verify all tests remain passing.
4. **Coverage Check:** Confirm code coverage meets or exceeds project thresholds.

---

## 3. Backend Test Suite (`backend/tests/`)

### 3.1 Test Files & Responsibilities
- `test_models.py`: Validates Pydantic `Node`, `Relation`, and `Graph` model instantiation, UUID v4 format rejection, empty name rejection, and JSON property handling.
- `test_csv_validation.py`: Tests `CSVValidator` against missing headers, invalid UUIDs, orphaned relations, self-relations, duplicate IDs, and invalid JSON.
- `test_graph_parser.py`: Tests `GraphParser.build_graph()` to ensure correct graph assembly, node connectivity, isolated nodes, and memory efficiency.
- `test_api.py`: Integration tests for `/api/health`, `/api/validate`, and `/api/load-graph` endpoints using Starlette/FastAPI `TestClient`.

### 3.2 Backend Test Commands
```bash
# Run all backend tests
pytest backend/tests/ -v

# Run with verbose tracebacks
pytest backend/tests/ -v --tb=short

# Run with coverage report
pytest --cov=backend --cov-report=term-missing backend/tests/

# Generate HTML coverage report
pytest --cov=backend --cov-report=html:coverage/backend backend/tests/
```

**Target:** Minimum **85% backend code coverage**.

---

## 4. Frontend Test Suite (`frontend/src/app/`)

### 4.1 Test Files & Responsibilities
- `file-upload.component.spec.ts`: Tests file input selection, CSV format validation, button states, and error list rendering.
- `graph.service.spec.ts`: Tests HTTP calls to `/api/validate` and `/api/load-graph` using `HttpTestingController`, error handling, and RxJS state emissions.
- `graph-viewer.component.spec.ts`: Tests D3 SVG rendering, node/link counts, pan/zoom hooks, and component cleanup.
- `detail-panel.component.spec.ts`: Tests detail panel visibility, formatted property output, and close/dismiss button actions.

### 4.2 Frontend Test Commands
```bash
cd frontend

# Run unit tests once in headless Chrome
npm test -- --watch=false --browsers=ChromeHeadless

# Run with code coverage report
npm test -- --watch=false --browsers=ChromeHeadless --code-coverage
```

**Target:** Minimum **80% frontend code coverage**.

---

## 5. Test Fixtures Reference (`backend/tests/fixtures/`)

| Fixture File | Purpose | Expected Outcome |
| :--- | :--- | :--- |
| `valid_nodes.csv` | Standard nodes with properties | Passes validation, returns node count |
| `valid_relations.csv` | Standard relations connecting valid nodes | Passes validation, returns relation count |
| `invalid_nodes_bad_uuid.csv` | Node with malformed UUID string | Fails with `Row 2: Invalid UUID format` |
| `invalid_nodes_missing_header.csv`| Missing mandatory `properties` header | Fails with `Missing required columns` |
| `invalid_relations_orphaned.csv` | Edge connecting non-existent node UUID | Fails with `source_uuid not found in nodes` |

### Adding New Test Fixtures
When adding edge cases (e.g. empty CSVs, UTF-8 emojis, circular graphs, 1000+ node performance test):
1. Place the CSV in `backend/tests/fixtures/<descriptive_name>.csv`.
2. Add corresponding test methods in `test_csv_validation.py` or `test_graph_parser.py`.
3. Document expected error text or parse outcome.
