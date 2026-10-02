"""CSV validators for graph data."""
import json
from io import StringIO
from typing import Tuple, List, Set, Any
from uuid import UUID
from pathlib import Path
import pandas as pd


class CSVValidator:
    """Validates CSV files against expected schemas according to BRD."""

    @staticmethod
    def validate_uuid_format(uuid_str: str) -> bool:
        """Check if string is a valid UUID format."""
        if not uuid_str or pd.isna(uuid_str):
            return False
        try:
            UUID(str(uuid_str).strip())
            return True
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def validate_json_string(json_str: str) -> bool:
        """Check if string is valid JSON."""
        if not json_str or pd.isna(json_str):
            return True
        try:
            json.loads(str(json_str).strip())
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    @classmethod
    def read_csv_source(cls, source: str | Path) -> Tuple[bool, str, pd.DataFrame]:
        """
        Read CSV content from a file path or raw CSV string.
        Returns (success, error_msg, dataframe).
        """
        try:
            # Check if source is a file path
            if isinstance(source, Path) or (isinstance(source, str) and (Path(source).is_file() or '\n' not in source)):
                path = Path(source)
                if not path.exists():
                    return False, f"File not found: {source}", pd.DataFrame()
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                content = str(source)

            df = pd.read_csv(StringIO(content))
            return True, "", df
        except UnicodeDecodeError as e:
            return False, f"File encoding error (UTF-8 required): {str(e)}", pd.DataFrame()
        except Exception as e:
            return False, f"Failed to parse CSV: {str(e)}", pd.DataFrame()

    @classmethod
    def validate_nodes_csv(cls, source: str | Path) -> Tuple[bool, List[str], pd.DataFrame]:
        """
        Validate nodes CSV format and content.

        Args:
            source: CSV file path or raw CSV content string

        Returns:
            Tuple of (is_valid, error_list, dataframe)
        """
        errors: List[str] = []
        success, read_err, df = cls.read_csv_source(source)
        if not success:
            return False, [read_err], pd.DataFrame()

        # Check headers
        required_headers = {"name", "uuid", "properties"}
        actual_headers = set(df.columns)

        if not required_headers.issubset(actual_headers):
            missing = sorted(list(required_headers - actual_headers))
            errors.append(f"Missing required columns: {', '.join(missing)}")
            return False, errors, df

        # Check empty file
        if len(df) == 0:
            errors.append("CSV file is empty (at least 1 node required)")
            return False, errors, df

        # Validate rows
        seen_uuids: Set[str] = set()
        for idx, row in df.iterrows():
            row_num = idx + 2  # +2 for 1-indexed row number after header

            # Validate name
            name = row.get("name")
            if pd.isna(name) or (isinstance(name, str) and not name.strip()):
                errors.append(f"Row {row_num}: 'name' field is empty or missing")

            # Validate uuid
            uuid_val = row.get("uuid")
            if pd.isna(uuid_val) or (isinstance(uuid_val, str) and not uuid_val.strip()):
                errors.append(f"Row {row_num}: 'uuid' field is missing")
            elif not cls.validate_uuid_format(str(uuid_val).strip()):
                errors.append(f"Row {row_num}: Invalid UUID format: {uuid_val}")
            elif str(uuid_val).strip() in seen_uuids:
                errors.append(f"Row {row_num}: Duplicate UUID: {uuid_val}")
            else:
                seen_uuids.add(str(uuid_val).strip())

            # Validate properties if present
            props = row.get("properties")
            if not pd.isna(props) and str(props).strip() and str(props).strip().lower() != "nan":
                if not cls.validate_json_string(str(props).strip()):
                    truncated = str(props)[:50] + ("..." if len(str(props)) > 50 else "")
                    errors.append(f"Row {row_num}: Invalid JSON in properties: {truncated}")

        is_valid = len(errors) == 0
        return is_valid, errors, df

    @classmethod
    def validate_relations_csv(
        cls, source: str | Path, valid_node_uuids: Set[str]
    ) -> Tuple[bool, List[str], pd.DataFrame]:
        """
        Validate relations CSV format and content.

        Args:
            source: CSV file path or raw CSV content string
            valid_node_uuids: Set of valid node UUIDs to check against for orphan detection

        Returns:
            Tuple of (is_valid, error_list, dataframe)
        """
        errors: List[str] = []
        success, read_err, df = cls.read_csv_source(source)
        if not success:
            return False, [read_err], pd.DataFrame()

        # Check headers
        required_headers = {
            "source_uuid",
            "target_uuid",
            "relationship_name",
            "relationship_uuid",
            "properties",
        }
        actual_headers = set(df.columns)

        if not required_headers.issubset(actual_headers):
            missing = sorted(list(required_headers - actual_headers))
            errors.append(f"Missing required columns: {', '.join(missing)}")
            return False, errors, df

        # Empty relations file is permitted (graph with isolated nodes)
        if len(df) == 0:
            return True, [], df

        # Validate rows
        seen_rel_uuids: Set[str] = set()
        for idx, row in df.iterrows():
            row_num = idx + 2

            # Validate source_uuid
            source_uuid = row.get("source_uuid")
            if pd.isna(source_uuid) or (isinstance(source_uuid, str) and not source_uuid.strip()):
                errors.append(f"Row {row_num}: 'source_uuid' field is missing")
            elif not cls.validate_uuid_format(str(source_uuid).strip()):
                errors.append(f"Row {row_num}: Invalid source_uuid format: {source_uuid}")
            elif str(source_uuid).strip() not in valid_node_uuids:
                errors.append(f"Row {row_num}: source_uuid not found in nodes: {source_uuid}")

            # Validate target_uuid
            target_uuid = row.get("target_uuid")
            if pd.isna(target_uuid) or (isinstance(target_uuid, str) and not target_uuid.strip()):
                errors.append(f"Row {row_num}: 'target_uuid' field is missing")
            elif not cls.validate_uuid_format(str(target_uuid).strip()):
                errors.append(f"Row {row_num}: Invalid target_uuid format: {target_uuid}")
            elif str(target_uuid).strip() not in valid_node_uuids:
                errors.append(f"Row {row_num}: target_uuid not found in nodes: {target_uuid}")

            # Validate relationship_name
            rel_name = row.get("relationship_name")
            if pd.isna(rel_name) or (isinstance(rel_name, str) and not rel_name.strip()):
                errors.append(f"Row {row_num}: 'relationship_name' field is empty or missing")

            # Validate relationship_uuid
            rel_uuid = row.get("relationship_uuid")
            if pd.isna(rel_uuid) or (isinstance(rel_uuid, str) and not rel_uuid.strip()):
                errors.append(f"Row {row_num}: 'relationship_uuid' field is missing")
            elif not cls.validate_uuid_format(str(rel_uuid).strip()):
                errors.append(f"Row {row_num}: Invalid relationship_uuid format: {rel_uuid}")
            elif str(rel_uuid).strip() in seen_rel_uuids:
                errors.append(f"Row {row_num}: Duplicate relationship_uuid: {rel_uuid}")
            else:
                seen_rel_uuids.add(str(rel_uuid).strip())

            # Validate properties if present
            props = row.get("properties")
            if not pd.isna(props) and str(props).strip() and str(props).strip().lower() != "nan":
                if not cls.validate_json_string(str(props).strip()):
                    truncated = str(props)[:50] + ("..." if len(str(props)) > 50 else "")
                    errors.append(f"Row {row_num}: Invalid JSON in properties: {truncated}")

        is_valid = len(errors) == 0
        return is_valid, errors, df


__all__ = ["CSVValidator"]
