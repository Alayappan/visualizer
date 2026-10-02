---
name: testing-and-coverage
description: Use when writing, maintaining, or executing automated pytest suites, managing CSV test fixtures, enforcing Test-Driven Development (TDD), and auditing code coverage thresholds (>85%).
---

# Testing & Coverage Skill (Desktop Application)

## 1. Overview & Purpose
This skill operationalizes the Test Strategy for the Python/Tkinter desktop visualizer.

It provides standardized commands, test structure guidelines, edge-case fixture patterns, and coverage requirements.

---

## 2. Test Structure (`tests/`)

- `conftest.py`: Test environment setup and sys.path configuration.
- `test_models.py`: Validates Pydantic `Node`, `Relation`, and `Graph` model instantiation, UUID v4 format rejection, empty name rejection, and JSON property handling.
- `test_csv_validation.py`: Tests `CSVValidator` against missing headers, invalid UUIDs, orphaned relations, self-relations, duplicate IDs, and invalid JSON.
- `test_graph_parser.py`: Tests `GraphParser.build_graph()` to ensure correct graph assembly, node connectivity, isolated nodes, and direct source file loading.
- `test_gui.py`: Headless Tkinter tests verifying window creation, file validation triggers, graph loading, canvas rendering, node selection, and detail panel formatting using `root.withdraw()`.
- `fixtures/`: Valid & invalid CSV files (`valid_nodes.csv`, `valid_relations.csv`, `invalid_nodes_bad_uuid.csv`, `invalid_nodes_missing_header.csv`, `invalid_relations_orphaned.csv`).

---

## 3. Test Execution Commands

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report (>85% requirement)
pytest --cov=src --cov-report=term-missing tests/

# Run specific suite
pytest tests/test_gui.py -v
```

---

## 4. Headless GUI Testing Best Practices
To avoid popup windows or display errors during automated test execution:
```python
@pytest.fixture(scope="module")
def tk_root():
    root = tk.Tk()
    root.withdraw()  # Keeps window hidden
    yield root
    root.destroy()
```
Verify widget state with `str(widget.cget('state'))` to maintain cross-platform compatibility across Tcl/Tk versions.
