# Backend Setup Guide

## Prerequisites
- Python 3.10.5
- UV package manager (pip install uv)

## Installation

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

## Running Tests

Run all tests with coverage:
```bash
pytest --cov=. --cov-report=html tests/
```

Run specific test file:
```bash
pytest tests/test_csv_validation.py -v
```

Run tests in watch mode:
```bash
pytest-watch tests/
```

## Starting the Server

Run the FastAPI server:
```bash
python app.py
```

The API will be available at `http://localhost:8000`

Swagger documentation: `http://localhost:8000/docs`

## API Endpoints

### Health Check
- **GET** `/api/health` - Check if API is running

### Validate CSV Files
- **POST** `/api/validate` - Validate node and relation CSV files
  - Parameters: `nodes_file` (multipart), `relations_file` (multipart)
  - Response: `{valid: bool, errors: string[], node_count: int, relation_count: int}`

### Load Graph
- **POST** `/api/load-graph` - Load and parse CSV files into graph structure
  - Parameters: `nodes_file` (multipart), `relations_file` (multipart)
  - Response: `{nodes: Node[], relations: Relation[], node_count: int, relation_count: int}`

## Test Data

Sample CSV files are in `tests/fixtures/`:
- `valid_nodes.csv` - Valid nodes file
- `valid_relations.csv` - Valid relations file
- `invalid_nodes_bad_uuid.csv` - Invalid UUID example
- `invalid_relations_orphaned.csv` - Orphaned relation example
