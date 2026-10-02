# Visualizer Project - Agent Guidelines & Master Architecture

Welcome to the **Neo4j Graph Visualizer** project. This document serves as the master instruction guide, architecture overview, and agent coordination manual for all AI agents and developers working on this codebase.

This project is built strictly in accordance with the Business Requirements Document ([BRD.md](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/BRD.md)).

---

## 1. Executive Summary & Architecture Overview

The Graph Visualizer is a single-page web application designed to validate, parse, and visualize node and relationship graph datasets from CSV files (`nodes.csv` and `relations.csv`).

### Core Technology Stack
- **Backend:** Python 3.10.5, FastAPI, pandas, Pydantic v2, uvicorn, pytest, pytest-cov.
- **Frontend:** Angular (CLI 11.1.4 / Angular 20, Node 20.9.0), TypeScript 5.8, RxJS 7, D3.js v7, Jasmine, Karma.
- **Data Model:** Property Graph model aligned with Neo4j conventions (UUID v4 identifiers, typed relationships, JSON properties).

### System Data Flow
```
User (Browser)
   │
   ├─► 1. Uploads nodes.csv + relations.csv
   │      │
   │      ▼
   ├─► 2. POST /api/validate ──► CSVValidator (schema, UUIDs, orphan detection)
   │      │
   │      ▼
   ├─► 3. POST /api/load-graph ──► GraphParser ──► JSON {nodes, relations}
   │      │
   │      ▼
   ├─► 4. GraphService (RxJS state store)
   │      │
   │      ├─► GraphViewerComponent (D3 force-directed interactive SVG)
   │      │
   │      └─► DetailPanelComponent (Node / Relation property drawer)
```

---

## 2. Agent Roles & Specializations

All engineering tasks on this project are assigned to specialized agent personas defined in [`.agents/agents/`](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/.agents/agents/):

| Agent Persona | Role File | Primary Domain | Key Skills |
| :--- | :--- | :--- | :--- |
| **Backend Agent** | [`.agents/agents/backend-agent.md`](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/.agents/agents/backend-agent.md) | Python/FastAPI backend, CSV validators, models, REST API | `backend-api`, `csv-validation`, `testing-and-coverage` |
| **Frontend Agent** | [`.agents/agents/frontend-agent.md`](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/.agents/agents/frontend-agent.md) | Angular SPA, D3.js graph visualization, RxJS state, detail panels | `frontend-workflow`, `graph-visualization`, `testing-and-coverage` |
| **Graph Data Agent** | [`.agents/agents/graph-data-agent.md`](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/.agents/agents/graph-data-agent.md) | Property graph modeling, Neo4j schema compatibility, data integrity | `neo4j-modeling`, `csv-validation`, `graph-visualization` |
| **QA & Test Agent** | [`.agents/agents/qa-test-agent.md`](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/.agents/agents/qa-test-agent.md) | TDD enforcement, pytest & Karma suites, test fixtures, coverage | `testing-and-coverage`, `csv-validation`, `backend-api` |
| **Orchestrator Agent**| [`.agents/agents/orchestrator-agent.md`](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/.agents/agents/orchestrator-agent.md) | Full-stack delivery, BRD milestone verification, contract sync | All skills |

---

## 3. Registered Workspace Skills

Skills are modular operational runbooks located under [`.agents/skills/`](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/.agents/skills/):

- [**csv-validation**](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/.agents/skills/csv-validation/SKILL.md): Comprehensive schema validation rules for `nodes.csv` and `relations.csv`, UUID v4 checks, JSON parsing, duplicate prevention, and orphaned relation detection.
- [**graph-visualization**](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/.agents/skills/graph-visualization/SKILL.md): D3.js force simulation, zoom, drag, node/arrow styling, selection events, and cleanup lifecycle.
- [**backend-api**](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/.agents/skills/backend-api/SKILL.md): FastAPI application endpoints, multipart form-data handling, error response contracts, and uvicorn server execution.
- [**frontend-workflow**](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/.agents/skills/frontend-workflow/SKILL.md): Angular component interactions, state machine flow (upload -> validate -> render -> reset), and RxJS service patterns.
- [**testing-and-coverage**](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/.agents/skills/testing-and-coverage/SKILL.md): Test-Driven Development (TDD) guide, pytest coverage (>85%), Jasmine/Karma coverage (>80%), and edge-case test fixtures.
- [**neo4j-modeling**](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/.agents/skills/neo4j-modeling/SKILL.md): Mapping CSV node/relationship structures to Neo4j Property Graph standards and Cypher query conventions.

---

## 4. Key Engineering Standards & Constraints

### 4.1 Backend Standards (`backend/`)
1. **Thin Routes:** Keep `backend/routes/__init__.py` minimal; delegate business logic, validation, and parsing to `backend/validators/` and `backend/models/`.
2. **Explicit Validation:** Never ingest CSVs without schema validation. Return descriptive, row-specific error messages (`Row 5: Invalid UUID format: ...`).
3. **UUID Integrity:** All node UUIDs, relation UUIDs, source UUIDs, and target UUIDs must conform to UUID v4.
4. **No Orphaned Relations:** Every `source_uuid` and `target_uuid` in `relations.csv` must resolve to an existing `uuid` in `nodes.csv`.
5. **Coverage Requirement:** Minimum **85% code coverage** across `models/`, `validators/`, and `routes/`.

### 4.2 Frontend Standards (`frontend/`)
1. **Single Source of State:** All graph and selection state belongs in `GraphService` (`frontend/src/app/services/graph.service.ts`). Components must not store parallel copies of graph data.
2. **Deterministic UI State:** The UI transitions cleanly between:
   - `Initial / Upload`: Inputs visible, graph hidden.
   - `Validating / Validated`: Feedback displayed with error or success counts.
   - `Graph View`: Upload section hidden, D3 SVG rendered, Reset button available.
   - `Detail Open`: Overlay/sidebar open for selected node or relation.
3. **D3 Lifecycle Hygiene:** Stop D3 force simulations and remove existing SVG DOM elements before re-rendering or on component destruction (`ngOnDestroy`) to prevent memory leaks.
4. **Accessibility & Error UX:** Preserve validation error lists so users can fix their files without full page reload.
5. **Coverage Requirement:** Minimum **80% code coverage** for components and services.

---

## 5. Development & Testing Commands

### Backend Commands (from `backend/` or workspace root)
```bash
# Activate virtual environment / UV
source backend/.venv/bin/activate  # or use uv run

# Run backend development server
uvicorn backend.app:app --reload --port 8000

# Run all backend unit & integration tests
pytest backend/tests/ -v

# Run backend tests with coverage report
pytest --cov=backend --cov-report=term-missing backend/tests/
```

### Frontend Commands (from `frontend/`)
```bash
cd frontend

# Install dependencies
npm install

# Run frontend development server
npm start  # or ng serve

# Run unit tests headless
npm test -- --watch=false --browsers=ChromeHeadless

# Build production bundle
npm run build
```

---

## 6. Verification Against BRD Acceptance Criteria

Before signing off on any feature or change, verify:
- [ ] Two CSV files can be selected and validated independently.
- [ ] Validation feedback explicitly points out row numbers and column names for any failure.
- [ ] Nodes render as labeled circles; relations render as directional labeled links.
- [ ] Panning, zooming, and dragging work smoothly without console errors.
- [ ] Clicking any node or relation opens the detail panel showing all properties and metadata.
- [ ] Detail panel closes cleanly without disrupting graph state.
- [ ] "New Upload" resets the application back to the upload state.
- [ ] Tests pass with >= 85% coverage on backend and >= 80% coverage on frontend.
