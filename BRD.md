# Business Requirements Document - Graph Visualization Web App

## 1. Executive Summary

A web application for visualizing node and relationship data from CSV files. The application validates CSV inputs, parses node and relation data, and renders an interactive graph where users can click on nodes/relations to view detailed information.

**Technology Stack:**
- Backend: Python 3.10.5 (using UV package manager)
- Frontend: Angular (CLI 11.1.4, Node 20.9.0)
- Architecture: Single-page application with REST API backend

---

## 2. High-Level Requirements

### 2.1 Core Features
1. **CSV File Upload** - Accept two separate CSV files (nodes and relations)
2. **CSV Validation** - Validate structure and mandatory fields
3. **Graph Rendering** - Display nodes and relationships as interactive graph
4. **Interactive UI** - Click on nodes/relations to view details
5. **Single Page** - All interactions on one page with dynamic content switching

### 2.2 User Flow
```
1. User visits app → File upload interface
2. Upload node CSV + relation CSV
3. Backend validates files
4. If valid → Hide file upload, load graph
5. If invalid → Show error messages
6. User clicks nodes/relations to view details
```

---

## 3. Detailed Functional Requirements

### 3.1 Phase 1: Backend CSV Validation & API Setup

#### 3.1.1 Node CSV Schema
**File:** nodes.csv

| Column | Type | Mandatory | Description | Example |
|--------|------|-----------|-------------|---------|
| name | string | Yes | Node display name | "Server-001" |
| uuid | string (UUID v4) | Yes | Unique node identifier | "550e8400-e29b-41d4-a716-446655440000" |
| properties | JSON string | No | Additional node attributes | "{\"cpu\": \"80%\", \"memory\": \"16GB\"}" |

**Validation Rules:**
- UUID must be valid UUID v4 format
- Name must be non-empty string
- If properties present, must be valid JSON
- No duplicate UUIDs within file
- Minimum 1 node required

#### 3.1.2 Relation CSV Schema
**File:** relations.csv

| Column | Type | Mandatory | Description | Example |
|--------|------|-----------|-------------|---------|
| source_uuid | string (UUID v4) | Yes | UUID of source node | "550e8400-e29b-41d4-a716-446655440000" |
| target_uuid | string (UUID v4) | Yes | UUID of target node | "550e8400-e29b-41d4-a716-446655440001" |
| relationship_name | string | Yes | Type of relationship | "depends_on" |
| relationship_uuid | string (UUID v4) | Yes | Unique relation identifier | "550e8400-e29b-41d4-a716-446655440002" |
| properties | JSON string | No | Relationship attributes | "{\"strength\": \"high\", \"latency\": \"50ms\"}" |

**Validation Rules:**
- All UUID fields must be valid UUID v4 format
- relationship_name must be non-empty string
- source_uuid and target_uuid must exist in nodes.csv
- If properties present, must be valid JSON
- No duplicate relationship_uuid within file

#### 3.1.3 API Endpoints

**POST /api/validate**
- Input: Two CSV files (multipart form-data)
- Output: `{ "valid": bool, "errors": [string], "node_count": int, "relation_count": int }`
- Status: 200 (valid) or 400 (invalid)

**POST /api/load-graph**
- Input: Two CSV files (multipart form-data)
- Output: `{ "nodes": [Node], "relations": [Relation] }`
- Status: 200 or 400 with error messages
- Action: Parse and return graph data structure

**GET /api/health**
- Output: `{ "status": "ok" }`
- Status: 200

#### 3.1.4 Data Models (Backend)

```python
class Node:
    uuid: str
    name: str
    properties: dict (optional)

class Relation:
    uuid: str
    source_uuid: str
    target_uuid: str
    relationship_name: str
    properties: dict (optional)
```

---

### 3.2 Phase 2: Frontend File Upload & Validation Display

#### 3.2.1 Upload Component
**Location:** File upload section at page top

**Features:**
- Two file input fields (labeled "Nodes CSV" and "Relations CSV")
- "Validate" button
- File validation feedback (success/error messages)
- Auto-format detection (CSV extension check)

**User Actions:**
1. Select nodes.csv
2. Select relations.csv
3. Click "Validate"
4. Display results: ✓ Valid or ✗ Errors with details

#### 3.2.2 Error Display
- Show validation errors in clear list format
- Highlight which field failed (e.g., "Row 5: Invalid UUID format")
- Provide retry button without page reload

#### 3.2.3 Success Flow
- Show summary: "X nodes loaded, Y relations loaded"
- Show "Load Graph" button
- Disable file inputs

---

### 3.3 Phase 3: Graph Rendering (Interactive Visualization)

#### 3.3.1 Graph Display Container
**Library:** D3.js or Vis.js (recommended for interactive features)

**Visual Elements:**
- **Nodes:** Circles with node name in center
- **Relations:** Lines/arrows connecting nodes with relationship_name label
- **Colors:** Different colors for different relationship types (optional enhancement)
- **Size:** Node size can vary by property or be uniform

#### 3.3.2 Interactivity
- **Hover:** Highlight node and connected relations
- **Click Node:** Display node details panel
- **Click Relation:** Display relation details panel
- **Drag:** Allow panning/zooming of graph
- **Reset:** Button to reset view/zoom

#### 3.3.3 Detail Panel (Triggered by Click)

**For Node:**
```
┌─────────────────────────┐
│ Node Details            │
├─────────────────────────┤
│ Name: Server-001        │
│ UUID: 550e8400-...      │
│ Properties:             │
│   • cpu: 80%            │
│   • memory: 16GB        │
│                         │
│ [Close]                 │
└─────────────────────────┘
```

**For Relation:**
```
┌─────────────────────────┐
│ Relationship Details    │
├─────────────────────────┤
│ Type: depends_on        │
│ From: Server-001        │
│ To: Server-002          │
│ UUID: 550e8400-...      │
│ Properties:             │
│   • strength: high      │
│   • latency: 50ms       │
│                         │
│ [Close]                 │
└─────────────────────────┘
```

#### 3.3.4 UI State Management
- File upload section: Visible initially
- File upload section: Hidden after successful load
- Graph display: Hidden initially, shown after load
- Detail panel: Overlay/sidebar, closeable
- "New Upload" button: Available in graph view to restart

---

### 3.4 Phase 4: Error Handling & Edge Cases

#### 3.4.1 CSV Parsing Errors
- Missing mandatory fields → Show which row/field
- Invalid data types → Show expected vs. received
- Orphaned relations → Relations referencing non-existent nodes
- Duplicate UUIDs → Show duplicate values

#### 3.4.2 Network/API Errors
- Backend unavailable → Show error message with retry
- File too large → Size validation client-side
- Timeout → Show timeout error with retry option

#### 3.4.3 Empty/Invalid Data
- Empty CSV files → Reject with message
- No nodes → Cannot create graph
- No relations → Allow graph with isolated nodes (optional)

---

## 4. Technical Requirements

### 4.1 Backend Stack (Python)
- **Framework:** FastAPI or Flask
- **Package Manager:** UV (pip replacement)
- **Python Version:** 3.10.5
- **CORS:** Enable for Angular frontend
- **CSV Parsing:** pandas library
- **UUID Validation:** uuid library
- **JSON:** Built-in json library

### 4.2 Frontend Stack (Angular)
- **Angular CLI:** 11.1.4
- **Node:** 20.9.0
- **Graph Library:** D3.js v6+ or Vis.js
- **HTTP Client:** Angular HttpClientModule
- **Reactive Forms:** For file upload handling
- **CSS:** Bootstrap or Angular Material (optional)

### 4.3 File Structure
```
visualizer/
├── backend/
│   ├── app.py (or main.py)
│   ├── requirements.txt
│   ├── validators/
│   │   ├── csv_validator.py
│   │   └── schema_validator.py
│   ├── models/
│   │   ├── node.py
│   │   └── relation.py
│   ├── routes/
│   │   └── graph_routes.py
│   └── tests/
│       ├── test_csv_validation.py
│       ├── test_node_csv.py
│       └── test_relation_csv.py
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── components/
│       │   │   ├── file-upload/
│       │   │   ├── graph-viewer/
│       │   │   └── detail-panel/
│       │   ├── services/
│       │   │   └── graph.service.ts
│       │   └── app.component.ts
│       └── assets/
└── README.md
```

---

## 5. Incremental Implementation Plan

### Phase 1: Backend Foundation with Unit Tests (Week 1)
- [ ] Setup Python project with UV
- [ ] Create data models (Node, Relation)
- [ ] **Write unit tests for data models** (test_models.py)
- [ ] Implement CSV validation logic
- [ ] **Write unit tests for validators** (test_csv_validation.py, test_node_csv.py, test_relation_csv.py)
- [ ] Create FastAPI/Flask app with basic endpoints
- [ ] **Write unit tests for endpoints** (test_api_basic.py)
- [ ] Achieve >80% code coverage
- **Deliverable:** Working backend with comprehensive unit tests, validation API tested

**Unit Tests Required:**
- Data model instantiation and validation
- CSV schema validation (all error cases)
- UUID format validation
- JSON properties parsing
- Mandatory vs optional field handling
- Edge cases (empty values, special characters)

### Phase 2: Backend Graph Loading with Unit Tests (Week 1)
- [ ] Implement graph data loading endpoint
- [ ] Parse and structure CSV data
- [ ] **Write unit tests for graph parsing** (test_graph_parser.py)
- [ ] Return graph in JSON format
- [ ] Add comprehensive error handling
- [ ] **Write unit tests for error scenarios** (test_error_handling.py)
- [ ] **Write integration tests** (test_integration.py) for full workflow
- [ ] Achieve >85% code coverage
- **Deliverable:** Full backend with unit/integration tests, all edge cases covered

**Unit Tests Required:**
- Graph parsing from valid CSVs
- Orphaned relation detection
- Duplicate UUID handling
- Large dataset parsing
- Malformed JSON in properties
- Missing/null values handling
- File encoding issues

### Phase 3: Frontend Setup with Unit Tests (Week 2)
- [ ] Create Angular components structure
- [ ] Build file upload component
- [ ] **Write unit tests for file-upload component** (file-upload.component.spec.ts)
- [ ] Implement file selection and validation UI
- [ ] Connect to backend validation API
- [ ] **Write unit tests for API integration** (graph.service.spec.ts)
- [ ] Display validation results/errors
- [ ] **Mock backend API for testing** (test utilities)
- [ ] Achieve >80% code coverage
- **Deliverable:** File upload interface with unit tests, API service tested

**Unit Tests Required:**
- File input handling
- File validation (type, size)
- HTTP service calls (with mocks)
- Error message display
- Success state management
- Component lifecycle handling
- Input field binding

### Phase 4: Graph Visualization with Unit Tests (Week 2)
- [ ] Setup graph rendering library (D3.js/Vis.js)
- [ ] Create graph-viewer component
- [ ] Implement graph rendering from API data
- [ ] **Write unit tests for graph-viewer component** (graph-viewer.component.spec.ts)
- [ ] Add pan/zoom functionality
- [ ] **Write unit tests for graph interactions** (graph-interactions.spec.ts)
- [ ] Test with sample data
- [ ] Achieve >75% code coverage
- **Deliverable:** Interactive graph display with unit tests

**Unit Tests Required:**
- Graph rendering from data
- Node/relation positioning
- Pan/zoom functionality
- Graph data transformation
- DOM manipulation verification
- Memory management (no memory leaks)
- Responsive layout handling

### Phase 5: Detail Panels & Interactivity with Unit Tests (Week 2)
- [ ] Create detail-panel component
- [ ] Implement click handlers for nodes/relations
- [ ] **Write unit tests for detail-panel component** (detail-panel.component.spec.ts)
- [ ] Display formatted detail information
- [ ] **Write unit tests for data formatting** (data-formatter.spec.ts)
- [ ] Add close/dismiss functionality
- [ ] **Write unit tests for panel interactions** (panel-interactions.spec.ts)
- [ ] Style and polish UI
- [ ] Achieve >80% code coverage
- **Deliverable:** Full interactive graph with comprehensive unit tests

**Unit Tests Required:**
- Panel open/close state
- Click event handling
- Data formatting for display
- Property rendering
- Empty/null property handling
- Panel positioning
- Event propagation prevention

### Phase 6: End-to-End Testing & Polish (Week 3)
- [ ] **Write end-to-end tests** (e2e test suite)
- [ ] Full workflow: upload → validate → render → interact
- [ ] Test error scenarios (invalid CSVs, network errors)
- [ ] Cross-browser compatibility testing
- [ ] Performance testing (load time, memory usage)
- [ ] **Ensure all unit tests pass with >80% coverage across codebase**
- [ ] UI/UX refinements based on testing
- [ ] Documentation and setup guide
- **Deliverable:** Production-ready application with full test coverage

**E2E Tests Required:**
- Complete user workflows
- Error recovery paths
- Large dataset handling
- Browser compatibility
- Performance benchmarks
- Accessibility compliance

---

## 6. Data Flow Diagram

```
┌─────────────────┐
│  User Browser   │
│   (Angular)     │
└────────┬────────┘
         │
         │ 1. Upload nodes.csv + relations.csv
         ▼
┌─────────────────────────────┐
│  POST /api/load-graph       │
│  (FastAPI/Flask Backend)    │
│                             │
│  ┌───────────────────────┐  │
│  │ CSV Validator         │  │
│  │ - Parse CSV           │  │
│  │ - Validate Schema     │  │
│  │ - Check UUIDs         │  │
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │ Graph Builder         │  │
│  │ - Create Node objects │  │
│  │ - Create Relation obj │  │
│  │ - Return JSON         │  │
│  └───────────────────────┘  │
└────────┬────────────────────┘
         │
         │ 2. Return {nodes, relations}
         ▼
┌─────────────────────┐
│ Angular Service     │
│ - Store graph data  │
│ - Emit to component │
└────────┬────────────┘
         │
         │ 3. Pass to graph-viewer
         ▼
┌─────────────────────────┐
│ Graph Component         │
│ - Render with D3.js     │
│ - Show nodes/relations  │
│ - Handle click events   │
└────────┬────────────────┘
         │
         │ 4. Display details on click
         ▼
┌─────────────────────┐
│ Detail Panel        │
│ - Node/Relation     │
│ - Properties        │
│ - Formatted output  │
└─────────────────────┘
```

---

## 7. Test Strategy

### 7.1 Testing Approach
- **Test-Driven Development (TDD):** Write tests before implementing features
- **Continuous Testing:** Run tests after each code change
- **Coverage Target:** Minimum 80% code coverage across all phases
- **Test Levels:** Unit → Integration → End-to-End

### 7.2 Backend Unit Tests (Python)

**Test Framework:** pytest with pytest-cov for coverage

**test_models.py:**
```python
- test_node_creation_valid()
- test_node_creation_invalid_uuid()
- test_node_properties_parsing()
- test_node_missing_name()
- test_relation_creation_valid()
- test_relation_creation_invalid_uuid()
- test_relation_properties_parsing()
```

**test_csv_validation.py:**
```python
- test_validate_node_csv_valid()
- test_validate_relation_csv_valid()
- test_validate_node_csv_missing_header()
- test_validate_node_csv_missing_mandatory_field()
- test_validate_node_csv_invalid_uuid_format()
- test_validate_node_csv_duplicate_uuid()
- test_validate_node_csv_invalid_json_properties()
- test_validate_node_csv_empty_file()
- test_validate_relation_csv_orphaned_uuid()
- test_validate_relation_csv_self_relation()
```

**test_node_csv.py:**
```python
- test_parse_valid_node_csv()
- test_parse_node_with_simple_properties()
- test_parse_node_with_complex_properties()
- test_parse_node_without_properties()
- test_parse_node_with_special_characters_in_name()
- test_parse_node_with_whitespace_handling()
- test_parse_multiple_nodes()
```

**test_relation_csv.py:**
```python
- test_parse_valid_relation_csv()
- test_parse_relation_with_properties()
- test_parse_relation_without_properties()
- test_parse_relation_with_special_characters()
- test_validate_relation_source_exists()
- test_validate_relation_target_exists()
- test_parse_multiple_relations()
```

**test_graph_parser.py:**
```python
- test_build_graph_structure()
- test_graph_contains_all_nodes()
- test_graph_contains_all_relations()
- test_graph_node_connectivity()
- test_graph_with_isolated_nodes()
- test_graph_with_large_dataset()
- test_graph_memory_efficiency()
```

**test_error_handling.py:**
```python
- test_file_not_found_error()
- test_file_read_permission_error()
- test_csv_decode_error()
- test_malformed_csv_error()
- test_invalid_json_error()
- test_uuid_validation_error_handling()
- test_api_error_response_format()
```

**test_api_basic.py:**
```python
- test_health_endpoint()
- test_validate_endpoint_valid()
- test_validate_endpoint_invalid()
- test_validate_endpoint_missing_files()
- test_validate_endpoint_file_type_check()
```

**test_integration.py:**
```python
- test_full_workflow_valid_files()
- test_full_workflow_invalid_node_csv()
- test_full_workflow_invalid_relation_csv()
- test_load_graph_endpoint_success()
- test_load_graph_endpoint_error()
- test_concurrent_requests()
```

**Execution:**
```bash
pytest --cov=app --cov-report=html tests/
```

### 7.3 Frontend Unit Tests (Angular)

**Test Framework:** Jasmine with Karma runner

**file-upload.component.spec.ts:**
```typescript
- it('should create file upload component')
- it('should accept node CSV file')
- it('should accept relation CSV file')
- it('should reject non-CSV files')
- it('should validate file size')
- it('should display error for missing file')
- it('should enable validate button only when both files selected')
- it('should call graph service on validate')
- it('should display validation response')
- it('should disable file inputs after success')
```

**graph.service.spec.ts:**
```typescript
- it('should create service')
- it('should call POST /api/validate')
- it('should call POST /api/load-graph')
- it('should handle HTTP errors')
- it('should timeout on slow responses')
- it('should cache graph data')
- it('should emit graph update events')
```

**graph-viewer.component.spec.ts:**
```typescript
- it('should create graph component')
- it('should render nodes from data')
- it('should render relations between nodes')
- it('should handle empty graph')
- it('should update graph on data change')
- it('should handle large datasets')
- it('should not leak memory on destroy')
- it('should render node labels correctly')
- it('should render relation labels correctly')
```

**graph-interactions.spec.ts:**
```typescript
- it('should detect node click')
- it('should detect relation click')
- it('should trigger detail panel on click')
- it('should implement pan functionality')
- it('should implement zoom functionality')
- it('should reset view')
- it('should highlight connected nodes on hover')
```

**detail-panel.component.spec.ts:**
```typescript
- it('should create detail panel')
- it('should display node details')
- it('should display relation details')
- it('should format properties correctly')
- it('should handle missing properties')
- it('should close on dismiss')
- it('should prevent event propagation')
- it('should render multiple properties')
```

**data-formatter.spec.ts:**
```typescript
- it('should format node data')
- it('should format relation data')
- it('should handle null/undefined values')
- it('should escape special characters')
- it('should format JSON objects')
- it('should handle large property values')
```

**Execution:**
```bash
ng test --watch=true --code-coverage
```

### 7.4 Integration Tests

**Backend Integration:**
```python
# Full CSV upload and parsing workflow
test_upload_node_and_relation_csv_together()
test_validate_then_load_workflow()
```

**Frontend Integration:**
```typescript
# Full component workflow
test_upload_and_graph_display_workflow()
test_click_node_show_detail_workflow()
```

### 7.5 End-to-End Tests

**Test Framework:** Cypress or Protractor

**e2e/workflows.e2e.ts:**
```typescript
describe('Complete User Workflows', () => {
  - Upload valid files and view graph
  - Upload invalid files and see errors
  - Click nodes and view details
  - Pan/zoom graph
  - Upload new files after viewing graph
  - Handle network errors gracefully
});
```

### 7.6 Sample Test Data Files

Create in `tests/fixtures/`:

**valid_nodes.csv:**
```csv
name,uuid,properties
Node-A,550e8400-e29b-41d4-a716-446655440000,"{""type"":""server""}"
Node-B,550e8400-e29b-41d4-a716-446655440001,
```

**valid_relations.csv:**
```csv
source_uuid,target_uuid,relationship_name,relationship_uuid,properties
550e8400-e29b-41d4-a716-446655440000,550e8400-e29b-41d4-a716-446655440001,connects,550e8400-e29b-41d4-a716-446655440002,
```

**invalid_nodes_missing_field.csv:**
```csv
name,uuid
Node-A,550e8400-e29b-41d4-a716-446655440000
```

**invalid_nodes_bad_uuid.csv:**
```csv
name,uuid,properties
Node-A,not-a-uuid,
```

**invalid_relations_orphaned.csv:**
```csv
source_uuid,target_uuid,relationship_name,relationship_uuid,properties
550e8400-e29b-41d4-a716-446655440099,550e8400-e29b-41d4-a716-446655440001,connects,550e8400-e29b-41d4-a716-446655440002,
```

### 7.7 Coverage Requirements by Phase

| Phase | Minimum Coverage | Files to Test |
|-------|-----------------|---------------|
| Phase 1 | 85% | models, validators, api routes |
| Phase 2 | 85% | graph parser, error handling, integration |
| Phase 3 | 80% | upload component, api service |
| Phase 4 | 75% | graph-viewer component, interactions |
| Phase 5 | 80% | detail-panel, data formatting |
| Phase 6 | 80% | Full suite + E2E |

### 7.8 CI/CD Integration

**Pre-commit hooks:** Run unit tests before commit
**Build pipeline:** Fail build if coverage drops below threshold
**Continuous testing:** Run full test suite on every push

### 7.9 Test Execution Commands

**Backend:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_csv_validation.py -v

# Run with verbose output
pytest -v --tb=short
```

**Frontend:**
```bash
# Run tests in watch mode
ng test

# Run with coverage
ng test --code-coverage

# Run E2E tests
ng e2e
```

---

## 8. Acceptance Criteria

### Feature: File Upload & Validation
- [ ] User can select and upload two CSV files
- [ ] System validates both files against schema
- [ ] User receives clear validation feedback (errors or success)
- [ ] File upload interface is disabled after successful load

### Feature: Graph Display
- [ ] Nodes are rendered as circles with names visible
- [ ] Relations are rendered as connecting lines with labels
- [ ] Graph is centered and visible in viewport
- [ ] User can pan and zoom the graph

### Feature: Interactive Details
- [ ] Clicking a node shows node details panel
- [ ] Clicking a relation shows relation details panel
- [ ] Details include all relevant fields and properties
- [ ] User can close detail panels
- [ ] Detail panels do not obstruct graph view

### Feature: Error Handling
- [ ] Invalid CSV formats show specific error messages
- [ ] Network errors are caught and displayed
- [ ] User can retry operations without page refresh
- [ ] No unhandled exceptions crash the application

### Feature: Performance
- [ ] Graph loads within 3 seconds for 1000 nodes
- [ ] UI remains responsive during interactions
- [ ] No memory leaks on file reload

---

## 9. Success Metrics

- Application successfully loads and displays graphs
- All validation rules properly enforced
- User can interact with graph intuitively
- < 5% error rate in production
- Average load time < 2 seconds for typical datasets

---

## 10. Future Enhancements (Out of Scope - Phase 2)

- Export graph as image/SVG
- Graph layout optimization algorithms
- Search/filter nodes by properties
- Relationship type color coding
- Graph statistics panel (node count, relation count)
- Batch operations on nodes/relations
- Undo/redo for interactions
- Multiple graph views (list, tree, graph)

---

## Appendix: Sample Data

### Sample nodes.csv
```csv
name,uuid,properties
Server-001,550e8400-e29b-41d4-a716-446655440000,"{""cpu"":""80%"",""memory"":""16GB""}"
Server-002,550e8400-e29b-41d4-a716-446655440001,"{""cpu"":""45%"",""memory"":""8GB""}"
Database,550e8400-e29b-41d4-a716-446655440002,
```

### Sample relations.csv
```csv
source_uuid,target_uuid,relationship_name,relationship_uuid,properties
550e8400-e29b-41d4-a716-446655440000,550e8400-e29b-41d4-a716-446655440002,depends_on,550e8400-e29b-41d4-a716-446655440003,"{""strength"":""high""}"
550e8400-e29b-41d4-a716-446655440001,550e8400-e29b-41d4-a716-446655440002,queries,550e8400-e29b-41d4-a716-446655440004,
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-06-06  
**Status:** Ready for Development
