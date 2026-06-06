"""CSV validators for graph data."""
import json
from io import StringIO
from typing import Tuple, List, Dict, Set, Any
from uuid import UUID
import pandas as pd


class CSVValidator:
    """Validates CSV files against expected schemas."""
    
    @staticmethod
    def validate_uuid_format(uuid_str: str) -> bool:
        """Check if string is valid UUID format."""
        try:
            UUID(uuid_str)
            return True
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def validate_json_string(json_str: str) -> bool:
        """Check if string is valid JSON."""
        try:
            json.loads(json_str)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
    
    @staticmethod
    def validate_nodes_csv(csv_content: str) -> Tuple[bool, List[str], pd.DataFrame]:
        """
        Validate nodes CSV format and content.
        
        Args:
            csv_content: CSV file content as string
            
        Returns:
            Tuple of (is_valid, error_list, dataframe)
        """
        errors = []
        
        try:
            df = pd.read_csv(StringIO(csv_content))
        except Exception as e:
            return False, [f"Failed to parse CSV: {str(e)}"], pd.DataFrame()
        
        # Check headers
        required_headers = {'name', 'uuid', 'properties'}
        actual_headers = set(df.columns)
        
        if not required_headers.issubset(actual_headers):
            missing = required_headers - actual_headers
            errors.append(f"Missing required columns: {', '.join(missing)}")
            return False, errors, df
        
        # Check empty file
        if len(df) == 0:
            errors.append("CSV file is empty")
            return False, errors, df
        
        # Validate rows
        seen_uuids: Set[str] = set()
        for idx, row in df.iterrows():
            row_num = idx + 2  # +2 for header and 0-indexing
            
            # Validate name
            name = row.get('name')
            if pd.isna(name) or (isinstance(name, str) and not name.strip()):
                errors.append(f"Row {row_num}: 'name' field is empty or missing")
            
            # Validate uuid
            uuid_val = row.get('uuid')
            if pd.isna(uuid_val):
                errors.append(f"Row {row_num}: 'uuid' field is missing")
            elif not CSVValidator.validate_uuid_format(str(uuid_val).strip()):
                errors.append(f"Row {row_num}: Invalid UUID format: {uuid_val}")
            elif str(uuid_val).strip() in seen_uuids:
                errors.append(f"Row {row_num}: Duplicate UUID: {uuid_val}")
            else:
                seen_uuids.add(str(uuid_val).strip())
            
            # Validate properties if present
            props = row.get('properties')
            if not pd.isna(props) and props and isinstance(props, str):
                if not CSVValidator.validate_json_string(props):
                    errors.append(f"Row {row_num}: Invalid JSON in properties: {props[:50]}")
        
        is_valid = len(errors) == 0
        return is_valid, errors, df
    
    @staticmethod
    def validate_relations_csv(
        csv_content: str,
        valid_node_uuids: Set[str]
    ) -> Tuple[bool, List[str], pd.DataFrame]:
        """
        Validate relations CSV format and content.
        
        Args:
            csv_content: CSV file content as string
            valid_node_uuids: Set of valid node UUIDs
            
        Returns:
            Tuple of (is_valid, error_list, dataframe)
        """
        errors = []
        
        try:
            df = pd.read_csv(StringIO(csv_content))
        except Exception as e:
            return False, [f"Failed to parse CSV: {str(e)}"], pd.DataFrame()
        
        # Check headers
        required_headers = {
            'source_uuid', 'target_uuid', 'relationship_name',
            'relationship_uuid', 'properties'
        }
        actual_headers = set(df.columns)
        
        if not required_headers.issubset(actual_headers):
            missing = required_headers - actual_headers
            errors.append(f"Missing required columns: {', '.join(missing)}")
            return False, errors, df
        
        # Check empty file (relations can be optional)
        if len(df) == 0:
            return True, [], df
        
        # Validate rows
        seen_rel_uuids: Set[str] = set()
        for idx, row in df.iterrows():
            row_num = idx + 2
            
            # Validate source_uuid
            source_uuid = row.get('source_uuid')
            if pd.isna(source_uuid):
                errors.append(f"Row {row_num}: 'source_uuid' field is missing")
            elif not CSVValidator.validate_uuid_format(str(source_uuid).strip()):
                errors.append(f"Row {row_num}: Invalid source_uuid format: {source_uuid}")
            elif str(source_uuid).strip() not in valid_node_uuids:
                errors.append(f"Row {row_num}: source_uuid not found in nodes: {source_uuid}")
            
            # Validate target_uuid
            target_uuid = row.get('target_uuid')
            if pd.isna(target_uuid):
                errors.append(f"Row {row_num}: 'target_uuid' field is missing")
            elif not CSVValidator.validate_uuid_format(str(target_uuid).strip()):
                errors.append(f"Row {row_num}: Invalid target_uuid format: {target_uuid}")
            elif str(target_uuid).strip() not in valid_node_uuids:
                errors.append(f"Row {row_num}: target_uuid not found in nodes: {target_uuid}")
            
            # Validate relationship_name
            rel_name = row.get('relationship_name')
            if pd.isna(rel_name) or (isinstance(rel_name, str) and not rel_name.strip()):
                errors.append(f"Row {row_num}: 'relationship_name' field is empty or missing")
            
            # Validate relationship_uuid
            rel_uuid = row.get('relationship_uuid')
            if pd.isna(rel_uuid):
                errors.append(f"Row {row_num}: 'relationship_uuid' field is missing")
            elif not CSVValidator.validate_uuid_format(str(rel_uuid).strip()):
                errors.append(f"Row {row_num}: Invalid relationship_uuid format: {rel_uuid}")
            elif str(rel_uuid).strip() in seen_rel_uuids:
                errors.append(f"Row {row_num}: Duplicate relationship_uuid: {rel_uuid}")
            else:
                seen_rel_uuids.add(str(rel_uuid).strip())
            
            # Validate properties if present
            props = row.get('properties')
            if not pd.isna(props) and props and isinstance(props, str):
                if not CSVValidator.validate_json_string(props):
                    errors.append(f"Row {row_num}: Invalid JSON in properties: {props[:50]}")
        
        is_valid = len(errors) == 0
        return is_valid, errors, df
