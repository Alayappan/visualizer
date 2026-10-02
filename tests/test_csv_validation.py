"""Unit tests for CSV validation in desktop visualizer."""
import os
import pytest
from pathlib import Path
from src.validators import CSVValidator


class TestUUIDValidation:
    """Test UUID format validation."""

    def test_valid_uuid(self):
        """Test valid UUID."""
        assert CSVValidator.validate_uuid_format("550e8400-e29b-41d4-a716-446655440000")

    def test_invalid_uuid(self):
        """Test invalid UUID."""
        assert not CSVValidator.validate_uuid_format("not-a-uuid")

    def test_empty_uuid(self):
        """Test empty UUID."""
        assert not CSVValidator.validate_uuid_format("")


class TestJSONValidation:
    """Test JSON validation."""

    def test_valid_json(self):
        """Test valid JSON."""
        assert CSVValidator.validate_json_string('{"key": "value"}')

    def test_invalid_json(self):
        """Test invalid JSON."""
        assert not CSVValidator.validate_json_string('not json}')

    def test_empty_json(self):
        """Test empty JSON validation."""
        assert CSVValidator.validate_json_string("{}")


class TestNodesCSVValidation:
    """Test nodes CSV validation."""

    @pytest.fixture
    def fixture_dir(self):
        """Get path to fixtures directory."""
        return Path(__file__).parent / "fixtures"

    def test_valid_nodes_csv(self, fixture_dir):
        """Test valid nodes CSV from file path."""
        file_path = fixture_dir / "valid_nodes.csv"
        is_valid, errors, df = CSVValidator.validate_nodes_csv(file_path)
        assert is_valid
        assert len(errors) == 0
        assert len(df) == 3

    def test_invalid_nodes_missing_header(self, fixture_dir):
        """Test nodes CSV with missing header."""
        file_path = fixture_dir / "invalid_nodes_missing_header.csv"
        is_valid, errors, df = CSVValidator.validate_nodes_csv(file_path)
        assert not is_valid
        assert any("Missing required columns" in e for e in errors)

    def test_invalid_nodes_bad_uuid(self, fixture_dir):
        """Test nodes CSV with invalid UUID."""
        file_path = fixture_dir / "invalid_nodes_bad_uuid.csv"
        is_valid, errors, df = CSVValidator.validate_nodes_csv(file_path)
        assert not is_valid
        assert any("Invalid UUID format" in e for e in errors)

    def test_duplicate_uuid(self):
        """Test nodes CSV with duplicate UUIDs."""
        csv_content = """name,uuid,properties
Node-1,550e8400-e29b-41d4-a716-446655440000,
Node-2,550e8400-e29b-41d4-a716-446655440000,
"""
        is_valid, errors, df = CSVValidator.validate_nodes_csv(csv_content)
        assert not is_valid
        assert any("Duplicate UUID" in e for e in errors)

    def test_empty_csv(self):
        """Test empty nodes CSV."""
        csv_content = "name,uuid,properties\n"
        is_valid, errors, df = CSVValidator.validate_nodes_csv(csv_content)
        assert not is_valid
        assert any("CSV file is empty" in e for e in errors)

    def test_invalid_json_properties(self):
        """Test nodes with invalid JSON properties."""
        csv_content = """name,uuid,properties
Node-1,550e8400-e29b-41d4-a716-446655440000,"{invalid json}"
"""
        is_valid, errors, df = CSVValidator.validate_nodes_csv(csv_content)
        assert not is_valid
        assert any("Invalid JSON" in e for e in errors)

    def test_file_not_found(self):
        """Test handling of non-existent file."""
        is_valid, errors, df = CSVValidator.validate_nodes_csv("/non/existent/path.csv")
        assert not is_valid
        assert any("File not found" in e for e in errors)


class TestRelationsCSVValidation:
    """Test relations CSV validation."""

    @pytest.fixture
    def fixture_dir(self):
        """Get path to fixtures directory."""
        return Path(__file__).parent / "fixtures"

    def test_valid_relations_csv(self, fixture_dir):
        """Test valid relations CSV."""
        file_path = fixture_dir / "valid_relations.csv"
        valid_uuids = {
            "550e8400-e29b-41d4-a716-446655440000",
            "550e8400-e29b-41d4-a716-446655440001",
            "550e8400-e29b-41d4-a716-446655440002",
        }

        is_valid, errors, df = CSVValidator.validate_relations_csv(file_path, valid_uuids)
        assert is_valid
        assert len(errors) == 0
        assert len(df) == 2

    def test_invalid_relations_orphaned(self, fixture_dir):
        """Test relations CSV with orphaned UUID."""
        file_path = fixture_dir / "invalid_relations_orphaned.csv"
        valid_uuids = {
            "550e8400-e29b-41d4-a716-446655440001",
            "550e8400-e29b-41d4-a716-446655440002",
        }

        is_valid, errors, df = CSVValidator.validate_relations_csv(file_path, valid_uuids)
        assert not is_valid
        assert any("not found in nodes" in e for e in errors)

    def test_empty_relations_csv(self):
        """Test empty relations CSV is valid."""
        csv_content = """source_uuid,target_uuid,relationship_name,relationship_uuid,properties
"""
        valid_uuids = {"550e8400-e29b-41d4-a716-446655440000"}

        is_valid, errors, df = CSVValidator.validate_relations_csv(csv_content, valid_uuids)
        assert is_valid
        assert len(errors) == 0
