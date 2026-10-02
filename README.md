# Neo4j Graph Visualizer Desktop Application

An interactive desktop application for validating, parsing, and visualizing node and relationship property graph datasets from CSV files. Built with **Python 3.10+**, **Tkinter / ttk**, **NetworkX**, **pandas**, and **Pydantic v2**, adhering strictly to Neo4j Property Graph standards.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture & System Flow](#architecture--system-flow)
- [Project Directory Structure](#project-directory-structure)
- [Prerequisites & Requirements](#prerequisites--requirements)
- [Quick Start](#quick-start)
- [CSV File Specifications](#csv-file-specifications)
- [Validation Rules](#validation-rules)
- [User Interface & Controls](#user-interface--controls)
  - [Keyboard Shortcuts](#keyboard-shortcuts)
  - [Mouse Controls](#mouse-controls)
- [Sample Datasets](#sample-datasets)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

The **Neo4j Graph Visualizer** provides a seamless desktop workflow for exploring and verifying graph datasets before importing them into Neo4j or graph databases. It features:
- A deterministic, fail-safe validation engine that verifies schema conformity, UUID v4 standards, JSON properties, and referential integrity (preventing orphaned relationships).
- A rich Tkinter-based canvas featuring force-directed spring layouts, pseudo-3D perspective projection, camera orbit controls, real-time node dragging with dynamic edge updates, and curved links for multi-edge/bidirectional relationships.
- An inspector drawer with structured property trees and quick clipboard actions for entity UUIDs.

---

## Key Features

### 1. Robust CSV Schema & Integrity Validation
- **Schema Enforcement:** Validates required columns (`name`, `uuid`, `properties` for nodes; `source_uuid`, `target_uuid`, `relationship_name`, `relationship_uuid`, `properties` for relations).
- **UUID v4 Integrity:** Validates that every entity and relationship identifier is a strict UUID v4.
- **Referential Integrity:** Detects orphaned relations whose `source_uuid` or `target_uuid` does not exist in the nodes dataset.
- **JSON Attribute Parsing:** Validates and parses nested JSON properties strings into structured dictionaries.
- **Duplicate Detection:** Identifies duplicate node UUIDs or relationship UUIDs within files.
- **Detailed Error Reporting:** Presents clear, row-indexed error messages (1-indexed row number, column name, and explanation) in a dedicated scrollable panel.

### 2. Interactive Graph Canvas
- **Force-Directed Layout:** Powered by NetworkX (`spring_layout`) with automatic repulsion and spring equilibrium.
- **Pseudo-3D Perspective Projection:** Full 3D camera orbit (pitch and yaw controls) with depth-sorted visual rendering.
- **Curved Directed Relationships:** Uses quadratic Bézier curves to cleanly separate parallel edges and bidirectional connections without overlapping.
- **Node Shading & Highlighting:** Spherical node shading with specular highlights, drop shadows, centered labels, and golden selection glow.
- **Real-Time Interactive Dragging:** Move nodes freely across the canvas while incident edges dynamically recalculate and redraw in real time.
- **Navigation Controls:** Mouse-wheel zoom centered on cursor, viewport panning, auto-fit to screen (`⤢ Fit Screen`), and one-click layout recalculation (`🔄 Re-layout`).

### 3. Property Inspector Drawer (Detail Panel)
- **Collapsible Sidebar:** Inspect node or relationship metadata upon click.
- **Structured Properties Tree:** Formatted `ttk.Treeview` displaying arbitrary JSON key-value attributes.
- **One-Click Clipboard Copy:** Instant copy buttons for UUIDs, source/target IDs, and names.
- **Graph Metrics:** Live status bar reporting node count, relationship count, current zoom level, and active selections.

### 4. Interactive Node & Relationship Management
- **Modal Dialogs:** Built-in dialogs (`NodeDialog`, `RelationDialog`) for creating, editing, and previewing nodes and relationships directly within the GUI.

---

## Architecture & System Flow

```
                   ┌───────────────────────────────────┐
                   │           User Actions            │
                   │  - Browse CSVs or Load Sample     │
                   │  - Click Validate                 │
                   └─────────────────┬─────────────────┘
                                     │
                                     ▼
                   ┌───────────────────────────────────┐
                   │     CSVValidator (validators/)    │
                   │  - Schema column checks           │
                   │  - UUID v4 format verification    │
                   │  - JSON properties parsing        │
                   │  - Orphaned relationship check    │
                   └─────────────────┬─────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
           [If Validation Fails]             [If Validation Passes]
                    │                                 │
                    ▼                                 ▼
       ┌─────────────────────────┐       ┌─────────────────────────┐
       │   FileSelector View     │       │ GraphParser (parser.py) │
       │  - Red error banner     │       │  - Maps DataFrames to   │
       │  - Scrollable row error │       │    Pydantic Graph model │
       │    message list         │       └────────────┬────────────┘
       └─────────────────────────┘                    │
                                                      ▼
                                         ┌─────────────────────────┐
                                         │  GraphVisualizerApp UI  │
                                         │   (Switch to Workspace) │
                                         └────────────┬────────────┘
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       │                                                             │
                       ▼                                                             ▼
          ┌─────────────────────────┐                                   ┌─────────────────────────┐
          │  GraphCanvas Component  │                                   │  DetailPanel Component  │
          │  - NetworkX layout      │◄──────── [Selection Event] ──────►│  - Entity metadata      │
          │  - 3D perspective / pan │                                   │  - JSON property tree   │
          │  - Node drag & orbit    │                                   │  - Copy UUID to clip    │
          └─────────────────────────┘                                   └─────────────────────────┘
```

---

## Project Directory Structure

```
visualizer/
├── data/
│   ├── family_nodes.csv             # Sample dataset: 8 family members with properties
│   └── family_relations.csv         # Sample dataset: 26 typed relationships
├── src/
│   ├── __init__.py
│   ├── gui/                         # Tkinter Desktop GUI modules
│   │   ├── __init__.py
│   │   ├── app.py                   # Master application window & state transitions
│   │   ├── detail_panel.py          # Property inspector drawer (metadata & treeview)
│   │   ├── dialogs.py               # Node & Relationship edit/create modal dialogs
│   │   ├── file_selector.py         # CSV selection, sample loader & validation feedback UI
│   │   ├── graph_canvas.py          # Interactive canvas, pseudo-3D orbit, zoom/pan/drag
│   │   └── theme.py                 # Modern dark-slate palette & ttk widget styling
│   ├── models/                      # Pydantic v2 data models
│   │   └── __init__.py              # Node, Relation, and Graph data models & validators
│   └── validators/                  # Validation & parsing engine
│       ├── __init__.py              # CSVValidator (schema, UUIDs, orphans, JSON)
│       └── graph_parser.py          # GraphParser (converts DataFrames to Graph instances)
├── tests/                           # Pytest test suite
│   ├── conftest.py                  # Test fixtures and headless Tkinter root setup
│   ├── fixtures/                    # CSV test fixtures (valid & invalid edge cases)
│   │   ├── invalid_nodes_bad_uuid.csv
│   │   ├── invalid_nodes_missing_header.csv
│   │   ├── invalid_relations_orphaned.csv
│   │   ├── valid_nodes.csv
│   │   └── valid_relations.csv
│   ├── test_csv_validation.py       # CSV validation & schema test suite
│   ├── test_dialogs.py              # Modal dialogs test suite
│   ├── test_family_data.py          # End-to-end test on sample family dataset
│   ├── test_graph_parser.py         # GraphParser unit tests
│   ├── test_gui.py                  # Headless GUI tests (canvas, panels, selectors)
│   └── test_models.py               # Pydantic models unit tests
├── main.py                          # Application entry point
├── pyproject.toml                   # Project metadata and configuration
├── requirements.txt                 # Runtime and testing dependencies
└── README.md                        # Documentation
```

---

## Prerequisites & Requirements

- **Python:** Version `3.10` or higher
- **Tkinter:** Included by default in official Python distributions on macOS and Windows.
  - On Ubuntu / Debian:
    ```bash
    sudo apt-get update && sudo apt-get install -y python3-tk
    ```
- **Dependencies:**
  - `pandas >= 2.1.0`
  - `pydantic >= 2.5.0`
  - `networkx >= 3.0`
  - `pytest >= 7.4.0` *(development / testing)*
  - `pytest-cov >= 4.1.0` *(coverage reporting)*

---

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd visualizer
```

### 2. Set Up Virtual Environment

**Using standard `venv`:**
```bash
python3 -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Or using `uv`:**
```bash
uv venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### 3. Launch the Application
```bash
python main.py
```

---

## CSV File Specifications

The application expects two UTF-8 CSV files: `nodes.csv` and `relations.csv`.

### Nodes CSV (`nodes.csv`)

| Column | Type | Mandatory | Description | Example |
| :--- | :--- | :---: | :--- | :--- |
| `name` | String | **Yes** | Human-readable node display label | `"Server-001"` |
| `uuid` | UUID v4 | **Yes** | Unique identifier for the node | `"550e8400-e29b-41d4-a716-446655440000"` |
| `properties` | JSON String | No | Serialized dictionary of attributes | `"{\"cpu\": \"80%\", \"memory\": \"16GB\"}"` |

**Example `nodes.csv`:**
```csv
name,uuid,properties
Server-001,550e8400-e29b-41d4-a716-446655440000,"{""cpu"": ""80%"", ""memory"": ""16GB""}"
Server-002,550e8400-e29b-41d4-a716-446655440001,"{""cpu"": ""45%"", ""memory"": ""8GB""}"
Database,550e8400-e29b-41d4-a716-446655440002,"{""engine"": ""PostgreSQL"", ""version"": 15}"
```

### Relations CSV (`relations.csv`)

| Column | Type | Mandatory | Description | Example |
| :--- | :--- | :---: | :--- | :--- |
| `source_uuid` | UUID v4 | **Yes** | UUID of the source (origin) node | `"550e8400-e29b-41d4-a716-446655440000"` |
| `target_uuid` | UUID v4 | **Yes** | UUID of the target (destination) node | `"550e8400-e29b-41d4-a716-446655440002"` |
| `relationship_name` | String | **Yes** | Label/type describing the connection | `"connects_to"` |
| `relationship_uuid` | UUID v4 | **Yes** | Unique identifier for the relationship | `"550e8400-e29b-41d4-a716-446655440003"` |
| `properties` | JSON String | No | Serialized dictionary of attributes | `"{\"protocol\": \"TCP\", \"port\": 5432}"` |

**Example `relations.csv`:**
```csv
source_uuid,target_uuid,relationship_name,relationship_uuid,properties
550e8400-e29b-41d4-a716-446655440000,550e8400-e29b-41d4-a716-446655440002,connects_to,550e8400-e29b-41d4-a716-446655440003,"{""protocol"": ""TCP"", ""port"": 5432}"
550e8400-e29b-41d4-a716-446655440001,550e8400-e29b-41d4-a716-446655440002,replicates_to,550e8400-e29b-41d4-a716-446655440004,"{""latency"": ""12ms""}"
```

---

## Validation Rules

1. **Header Verification:** Both files must contain all mandatory column names.
2. **UUID v4 Compliance:** All `uuid`, `source_uuid`, `target_uuid`, and `relationship_uuid` values must parse strictly into UUID v4.
3. **Non-Empty Text:** `name` and `relationship_name` cannot be null, whitespace-only, or missing.
4. **Duplicate Prevention:** No duplicate `uuid` values are allowed in `nodes.csv`, and no duplicate `relationship_uuid` values in `relations.csv`.
5. **Referential Integrity (No Orphans):** Every `source_uuid` and `target_uuid` in `relations.csv` must reference a valid `uuid` that exists in `nodes.csv`.
6. **JSON Syntax:** If `properties` is provided, it must be valid JSON object notation.

---

## User Interface & Controls

### Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + O` / `Cmd + O` | Return to File Selection / Upload view |
| `Ctrl + +` / `Cmd + +` | Zoom In |
| `Ctrl + -` / `Cmd + -` | Zoom Out |
| `Ctrl + 0` / `Cmd + 0` | Fit graph to screen |
| `Escape` | Clear current selection / dismiss inspector panel |
| `Ctrl + Q` / `Cmd + Q` | Exit application |

### Mouse Controls

| Mouse Action | Context | Result |
| :--- | :--- | :--- |
| **Left Click** | Node / Relationship badge | Selects entity and displays details in the inspector drawer |
| **Left Click** | Empty canvas | Clears current selection |
| **Left Click + Drag** | Node | Drags node across canvas in real time with dynamic edge updating |
| **Left Click + Drag** | Empty canvas | Pans the viewport across 2D/3D space |
| **Right Click + Drag** *(or Middle Drag)* | Canvas | 3D Camera Orbit (adjusts pitch tilt and yaw azimuth angles) |
| **Scroll Wheel** | Canvas | Zooms smoothly in or out centered at the mouse cursor |

---

## Sample Datasets

The repository includes ready-to-use sample datasets:

1. **Family Tree Graph (`data/`):**
   - [`data/family_nodes.csv`](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/data/family_nodes.csv): 8 family members with generational categories, roles, and profiles.
   - [`data/family_relations.csv`](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/data/family_relations.csv): 26 typed relationships (`FATHER_OF`, `MOTHER_OF`, `SPOUSE_OF`, `BROTHER_OF`, `DAUGHTER_OF`, `PET_OF`).
2. **Test Fixtures (`tests/fixtures/`):**
   - `valid_nodes.csv` and `valid_relations.csv` (used by the "Load Sample Data" button).
   - `invalid_nodes_bad_uuid.csv` (invalid UUID example).
   - `invalid_nodes_missing_header.csv` (missing header validation example).
   - `invalid_relations_orphaned.csv` (orphan reference validation example).

---

## Testing & Quality Assurance

The codebase includes comprehensive unit and integration test suites with headless GUI testing.

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage Report
```bash
pytest --cov=src --cov-report=term-missing
```

### Test Suite Breakdown

- **Model Tests (`tests/test_models.py`):** Pydantic model validation, UUID checks, non-empty constraints, and helper methods.
- **CSV Validation Tests (`tests/test_csv_validation.py`):** Schema verification, UUID formatting, JSON parsing, duplicate IDs, and orphan relationship detection.
- **Graph Parser Tests (`tests/test_graph_parser.py`):** DataFrame to typed Graph transformation and source loader utility tests.
- **GUI Tests (`tests/test_gui.py`):** Headless Tkinter tests (`root.withdraw()`) verifying canvas rendering, selection handling, detail panel display, and view transitions.
- **Dialog Tests (`tests/test_dialogs.py`):** Tests creation and validation logic for `NodeDialog` and `RelationDialog`.
- **Integration Test (`tests/test_family_data.py`):** End-to-end validation and parsing of the 8-node, 26-relationship family dataset.

---

## Troubleshooting

- **`_tkinter.TclError: no display name and no $DISPLAY environment variable`:**
  - When running tests on a headless Linux server or CI/CD container, run with `xvfb-run pytest`.
- **`ModuleNotFoundError: No module named 'src'`:**
  - Ensure you launch via `python main.py` or set `PYTHONPATH=.`.
- **Invalid UTF-8 Encoding:**
  - CSV files must be encoded in UTF-8. If exported from Excel, ensure the format is selected as `CSV UTF-8 (Comma delimited) (*.csv)`.

---

## License

This project is licensed under the MIT License.
