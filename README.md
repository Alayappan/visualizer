# Graph Visualization Web App

A web application for visualizing node and relationship data from CSV files. Built with Python/FastAPI backend and Angular frontend with D3.js graph visualization.

## Quick Start

### Prerequisites
- Python 3.10.5
- Node.js 20.9.0
- Angular CLI 11.1.4
- UV (Python package manager)

### Backend Setup

1. Navigate to backend:
```bash
cd backend
```

2. Create virtual environment:
```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

4. Run tests:
```bash
pytest --cov=. --cov-report=html tests/
```

5. Start the server:
```bash
python app.py
```

Server runs on `http://localhost:8000`
Swagger docs: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to frontend root:
```bash
cd visualizer
```

2. Install dependencies:
```bash
npm install
```

3. Run tests:
```bash
npm test -- --code-coverage
```

4. Start development server:
```bash
npm start
```

App runs on `http://localhost:4200`

## Project Structure

```
visualizer/
├── backend/                          # Python FastAPI backend
│   ├── app.py                       # FastAPI application
│   ├── requirements.txt             # Python dependencies
│   ├── models/                      # Data models (Node, Relation)
│   ├── validators/                  # CSV validation logic
│   ├── routes/                      # API endpoints
│   ├── tests/                       # Backend unit tests
│   │   └── fixtures/               # Test CSV files
│   └── README.md                   # Backend setup guide
│
├── frontend/                        # Angular application
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/         # Angular components
│   │   │   ├── services/           # API services
│   │   │   ├── models/             # TypeScript interfaces
│   │   │   └── app.component.ts    # Main component
│   │   └── index.html              # HTML entry point
│   ├── package.json               # NPM dependencies
│   ├── angular.json               # Angular configuration
│   └── README.md                  # Frontend setup guide
│
├── BRD.md                          # Business Requirements Document
└── README.md                       # This file
```

## Features

### CSV File Upload & Validation
- Upload two CSV files: nodes and relations
- Validate CSV structure and data integrity
- UUID v4 format validation
- JSON properties parsing
- Detailed error reporting

### Graph Visualization
- Interactive D3.js graph rendering
- Pan and zoom functionality
- Click nodes to view details
- Click relations to view relationship info
- Auto-layout force simulation

### Node Details Display
```
Name: Server-001
UUID: 550e8400-e29b-41d4-a716-446655440000
Properties:
  • cpu: 80%
  • memory: 16GB
```

### Relation Details Display
```
Type: depends_on
From: Server-001
To: Database
UUID: 550e8400-e29b-41d4-a716-446655440003
Properties:
  • strength: high
  • latency: 50ms
```

## CSV File Formats

### Nodes CSV
```csv
name,uuid,properties
Server-001,550e8400-e29b-41d4-a716-446655440000,"{""cpu"":""80%""}"
Server-002,550e8400-e29b-41d4-a716-446655440001,
Database,550e8400-e29b-41d4-a716-446655440002,
```

**Columns:**
- `name` (required): Node display name
- `uuid` (required): UUID v4 identifier
- `properties` (optional): JSON string with node properties

### Relations CSV
```csv
source_uuid,target_uuid,relationship_name,relationship_uuid,properties
550e8400-e29b-41d4-a716-446655440000,550e8400-e29b-41d4-a716-446655440002,depends_on,550e8400-e29b-41d4-a716-446655440003,"{""strength"":""high""}"
```

**Columns:**
- `source_uuid` (required): UUID of source node
- `target_uuid` (required): UUID of target node
- `relationship_name` (required): Type of relationship
- `relationship_uuid` (required): UUID for the relationship
- `properties` (optional): JSON string with relation properties

## API Endpoints

### Health Check
**GET** `/api/health`
- Response: `{"status": "ok"}`

### Validate Files
**POST** `/api/validate`
- Parameters: `nodes_file`, `relations_file` (multipart)
- Response: 
```json
{
  "valid": true,
  "errors": [],
  "node_count": 3,
  "relation_count": 2
}
```

### Load Graph
**POST** `/api/load-graph`
- Parameters: `nodes_file`, `relations_file` (multipart)
- Response:
```json
{
  "nodes": [
    {"name": "...", "uuid": "...", "properties": {...}}
  ],
  "relations": [...],
  "node_count": 3,
  "relation_count": 2
}
```

## Validation Rules

### Node CSV
- All rows must have `name` and `uuid`
- UUIDs must be valid UUID v4 format
- Names cannot be empty
- `properties` (if present) must be valid JSON
- No duplicate UUIDs

### Relations CSV
- All rows must have `source_uuid`, `target_uuid`, `relationship_name`, `relationship_uuid`
- All UUIDs must be valid UUID v4 format
- `source_uuid` and `target_uuid` must exist in nodes
- No duplicate `relationship_uuid`
- `properties` (if present) must be valid JSON

## Testing

### Backend Tests
Run all backend tests with coverage:
```bash
cd backend
pytest --cov=. --cov-report=html tests/
```

Tests include:
- Data model validation
- CSV schema validation
- UUID format validation
- JSON parsing
- API endpoint testing
- Full workflow integration tests

### Frontend Tests
Run all frontend tests with coverage:
```bash
npm test -- --code-coverage
```

Tests include:
- Service layer tests
- Component unit tests
- HTTP request mocking
- Event handling tests

## Development Workflow

1. **Make changes** to backend or frontend
2. **Run tests** to ensure everything works
3. **Test with sample data** from `backend/tests/fixtures/`
4. **Commit** when tests pass

## Sample Data

Sample CSV files are provided in `backend/tests/fixtures/`:
- `valid_nodes.csv` - Valid nodes file
- `valid_relations.csv` - Valid relations file
- `invalid_nodes_bad_uuid.csv` - Invalid UUID example
- `invalid_relations_orphaned.csv` - Orphaned relation example

## Production Deployment

### Backend (Python)
```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production server (gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Frontend (Angular)
```bash
# Build production bundle
ng build --prod

# Serve with static server
npx serve -s dist/graph-visualizer -l 3000
```

## Troubleshooting

### Backend Issues
- **ModuleNotFoundError**: Ensure all dependencies installed with `pip install -r requirements.txt`
- **Port 8000 in use**: Change port in `app.py` or kill existing process
- **CORS errors**: CORS is enabled for all origins in development

### Frontend Issues
- **Port 4200 in use**: Use `ng serve --port 4300`
- **D3.js not loading**: Run `npm install d3`
- **API not found**: Ensure backend is running on `http://localhost:8000`

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Browser (Angular)                            │
│                                                                 │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │ File Upload     │  │ Graph Viewer │  │ Detail Panel       │ │
│  │ Component       │  │ (D3.js)      │  │ (Node/Relation)    │ │
│  └────────┬────────┘  └──────┬───────┘  └─────────┬──────────┘ │
│           │                  │                    │             │
│           └──────────────┬───┴────────────────────┘             │
│                          │                                      │
│                  ┌───────▼──────────┐                           │
│                  │  Graph Service   │                           │
│                  │  (HTTP/RxJS)     │                           │
│                  └────────┬─────────┘                           │
└───────────────────────────┼─────────────────────────────────────┘
                            │ HTTP Requests
┌───────────────────────────▼─────────────────────────────────────┐
│              FastAPI Backend (Python)                            │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ Routes       │  │ Validators   │  │ Graph Parser          │ │
│  │ (/validate)  │  │ (CSV schema) │  │ (Nodes/Relations)     │ │
│  │ (/load-graph)│  │              │  │                       │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
│                          │                    │                 │
│                          └────────┬───────────┘                 │
│                                   │                             │
│                          ┌────────▼────────┐                    │
│                          │  Data Models    │                    │
│                          │  (Node, Relation)                    │
│                          └─────────────────┘                    │
└──────────────────────────────────────────────────────────────────┘
```

## License

This project is provided as-is for educational and internal use.

## Support

For issues or questions, refer to:
- Backend: `backend/README.md`
- Frontend: `frontend/README.md`
- BRD: `BRD.md` (detailed requirements and specifications)



