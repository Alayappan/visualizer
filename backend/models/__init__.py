"""Data models for graph visualization."""
from typing import Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel, field_validator


class Node(BaseModel):
    """Represents a node in the graph."""
    
    name: str
    uuid: str
    properties: Optional[Dict[str, Any]] = None
    
    @field_validator('uuid')
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate that uuid is a valid UUID v4 format."""
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid UUID format: {v}")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that name is not empty."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class Relation(BaseModel):
    """Represents a relationship between nodes."""
    
    source_uuid: str
    target_uuid: str
    relationship_name: str
    relationship_uuid: str
    properties: Optional[Dict[str, Any]] = None
    
    @field_validator('source_uuid', 'target_uuid', 'relationship_uuid')
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate that uuid fields are valid UUID v4 format."""
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid UUID format: {v}")
    
    @field_validator('relationship_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that relationship name is not empty."""
        if not v or not v.strip():
            raise ValueError("Relationship name cannot be empty")
        return v.strip()


class Graph(BaseModel):
    """Represents a complete graph with nodes and relations."""
    
    nodes: list[Node]
    relations: list[Relation]
    node_count: int
    relation_count: int
