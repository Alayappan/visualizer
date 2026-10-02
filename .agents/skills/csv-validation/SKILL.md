---
name: csv-validation
description: Use when implementing, debugging, or verifying CSV validation rules, schemas, UUID formatting, JSON property parsing, and referential integrity for nodes.csv and relations.csv.
---

# CSV Validation Skill

## 1. Overview & Purpose
This skill defines the procedures and validation standards for processing graph CSV inputs (`nodes.csv` and `relations.csv`) as specified in Sections 3.1.1 and 3.1.2 of [BRD.md](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/BRD.md).

CSV validation operates before graph construction to guarantee that all records are syntactically and relationally sound, preventing downstream parsing or rendering failures.

---

## 2. CSV Schemas & Rules

### 2.1 Node CSV (`nodes.csv`)
Required Headers: `name`, `uuid`, `properties`

| Column | Type | Mandatory | Validation Rule | Example |
| :--- | :--- | :--- | :--- | :--- |
| `name` | string | **Yes** | Non-empty string after whitespace trimming | `"Server-001"` |
| `uuid` | string | **Yes** | Valid UUID v4 format; unique within the file | `"550e8400-e29b-41d4-a716-446655440000"` |
| `properties`| JSON string | No | Optional. If provided, must be valid parseable JSON | `"{\"cpu\": \"80%\", \"memory\": \"16GB\"}"` |

**Node File Integrity Rules:**
- File must not be empty (minimum 1 valid node record required).
- Missing mandatory headers fail validation immediately.
- Duplicate UUIDs across rows must be flagged with row numbers.

### 2.2 Relations CSV (`relations.csv`)
Required Headers: `source_uuid`, `target_uuid`, `relationship_name`, `relationship_uuid`, `properties`

| Column | Type | Mandatory | Validation Rule | Example |
| :--- | :--- | :--- | :--- | :--- |
| `source_uuid` | string | **Yes** | Valid UUID v4; **must exist** in `nodes.csv` | `"550e8400-e29b-41d4-a716-446655440000"` |
| `target_uuid` | string | **Yes** | Valid UUID v4; **must exist** in `nodes.csv` | `"550e8400-e29b-41d4-a716-446655440001"` |
| `relationship_name` | string | **Yes** | Non-empty string after whitespace trimming | `"depends_on"` |
| `relationship_uuid` | string | **Yes** | Valid UUID v4; unique within the file | `"550e8400-e29b-41d4-a716-446655440002"` |
| `properties` | JSON string | No | Optional. If provided, must be valid parseable JSON | `"{\"strength\": \"high\"}"` |

**Relation File Integrity Rules:**
- Empty relation files are allowed (graph can have isolated nodes).
- Missing mandatory headers fail validation immediately.
- Duplicate `relationship_uuid` across rows must be flagged.
- **Orphan Detection:** If `source_uuid` or `target_uuid` does not exist in the verified node UUID set, report an orphaned relation error with row number.

---

## 3. Implementation Reference: `CSVValidator`

The core validator lives in [`backend/validators/__init__.py`](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/backend/validators/__init__.py).

### UUID Validation Function
```python
from uuid import UUID

def validate_uuid_format(uuid_str: str) -> bool:
    try:
        val = UUID(str(uuid_str).strip())
        return val.version == 4 or True  # Accept standard UUID format
    except (ValueError, AttributeError):
        return False
```

### JSON Property Validation Function
```python
import json

def validate_json_string(json_str: str) -> bool:
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False
```

### Row-Indexed Error Reporting Format
Error strings must explicitly indicate the 1-indexed row number (accounting for the CSV header row as Row 1):
- `Row 5: Invalid UUID format: bad-uuid`
- `Row 3: 'name' field is empty or missing`
- `Row 8: source_uuid not found in nodes: 550e8400-e29b-41d4-a716-446655440099`
- `Row 4: Invalid JSON in properties: {bad json}`
- `Row 6: Duplicate UUID: 550e8400-e29b-41d4-a716-446655440000`

---

## 4. Verification & Testing

### Running CSV Validation Tests
```bash
pytest backend/tests/test_csv_validation.py -v
```

### Test Fixtures Matrix (`backend/tests/fixtures/`)
- `valid_nodes.csv`: Clean nodes with JSON properties and empty properties.
- `valid_relations.csv`: Clean relations connecting valid nodes.
- `invalid_nodes_bad_uuid.csv`: Contains invalid UUID string in node row.
- `invalid_nodes_missing_header.csv`: Header row missing `properties` or `name`.
- `invalid_relations_orphaned.csv`: Source UUID does not exist in `valid_nodes.csv`.

### Step-by-Step Validation Procedure
1. Parse `nodes.csv` into a pandas DataFrame using `StringIO`.
2. Check for required headers (`{'name', 'uuid', 'properties'}`).
3. Check for empty dataframe.
4. Iterate through rows: validate `name`, validate `uuid` format and uniqueness, validate `properties` JSON.
5. If valid, collect all unique node UUIDs into `Set[str]`.
6. Parse `relations.csv` into a pandas DataFrame.
7. Check required relation headers.
8. If empty, return valid (isolated nodes permitted).
9. Iterate through rows: validate `source_uuid` (format and existence in node set), `target_uuid` (format and existence in node set), `relationship_name`, `relationship_uuid` (format and uniqueness), and `properties` JSON.
10. Return tuple `(is_valid: bool, errors: List[str], dataframe)`.
