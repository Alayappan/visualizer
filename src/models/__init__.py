"""Data models for graph visualization and editing."""
from typing import Dict, Any, Optional, List, Tuple
from uuid import UUID
from pathlib import Path
import json
import pandas as pd
from pydantic import BaseModel, field_validator


class Node(BaseModel):
    """Represents a node in the graph."""

    name: str
    uuid: str
    properties: Optional[Dict[str, Any]] = None

    @field_validator("uuid")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate that uuid is a valid UUID v4 format."""
        try:
            UUID(str(v).strip())
            return str(v).strip()
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid UUID format: {v}")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that name is not empty."""
        if not v or not str(v).strip():
            raise ValueError("Name cannot be empty")
        return str(v).strip()


class Relation(BaseModel):
    """Represents a relationship between nodes."""

    source_uuid: str
    target_uuid: str
    relationship_name: str
    relationship_uuid: str
    properties: Optional[Dict[str, Any]] = None

    @field_validator("source_uuid", "target_uuid", "relationship_uuid")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate that uuid fields are valid UUID v4 format."""
        try:
            UUID(str(v).strip())
            return str(v).strip()
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid UUID format: {v}")

    @field_validator("relationship_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that relationship name is not empty."""
        if not v or not str(v).strip():
            raise ValueError("Relationship name cannot be empty")
        return str(v).strip()


class Graph(BaseModel):
    """Represents a complete graph with nodes, relations, and mutation methods."""

    nodes: List[Node]
    relations: List[Relation]
    node_count: int
    relation_count: int

    def get_node(self, uuid: str) -> Optional[Node]:
        """Find a node by UUID."""
        for n in self.nodes:
            if n.uuid == uuid:
                return n
        return None

    def get_relation(self, uuid: str) -> Optional[Relation]:
        """Find a relationship by UUID."""
        for r in self.relations:
            if r.relationship_uuid == uuid:
                return r
        return None

    def get_relations_for_node(self, uuid: str) -> List[Relation]:
        """Find all incoming and outgoing relations for a node."""
        return [r for r in self.relations if r.source_uuid == uuid or r.target_uuid == uuid]

    def add_node(self, node: Node):
        """Add a new node to the graph."""
        if any(n.uuid == node.uuid for n in self.nodes):
            raise ValueError(f"Node with UUID {node.uuid} already exists")
        self.nodes.append(node)
        self.node_count = len(self.nodes)

    def update_node(self, uuid: str, name: str, properties: Optional[Dict[str, Any]] = None) -> Optional[Node]:
        """Update display name and properties of an existing node."""
        node = self.get_node(uuid)
        if not node:
            return None
        node.name = name.strip()
        node.properties = properties or {}
        return node

    def delete_node(self, uuid: str) -> Tuple[bool, List[Relation]]:
        """
        Delete a node by UUID and cascade-delete all connected relationships
        to maintain referential integrity (no orphaned relations).
        Returns (success_flag, list_of_deleted_relations).
        """
        node = self.get_node(uuid)
        if not node:
            return False, []

        self.nodes = [n for n in self.nodes if n.uuid != uuid]
        self.node_count = len(self.nodes)

        # Cascade-delete connected relationships
        deleted_rels = [r for r in self.relations if r.source_uuid == uuid or r.target_uuid == uuid]
        self.relations = [r for r in self.relations if r.source_uuid != uuid and r.target_uuid != uuid]
        self.relation_count = len(self.relations)

        return True, deleted_rels

    def add_relation(self, relation: Relation):
        """Add a new relationship ensuring both endpoints exist."""
        if not self.get_node(relation.source_uuid):
            raise ValueError(f"Source node {relation.source_uuid} does not exist in graph")
        if not self.get_node(relation.target_uuid):
            raise ValueError(f"Target node {relation.target_uuid} does not exist in graph")
        if any(r.relationship_uuid == relation.relationship_uuid for r in self.relations):
            raise ValueError(f"Relationship with UUID {relation.relationship_uuid} already exists")
        self.relations.append(relation)
        self.relation_count = len(self.relations)

    def update_relation(self, uuid: str, name: str, properties: Optional[Dict[str, Any]] = None) -> Optional[Relation]:
        """Update type/name and properties of an existing relationship."""
        rel = self.get_relation(uuid)
        if not rel:
            return None
        rel.relationship_name = name.strip()
        rel.properties = properties or {}
        return rel

    def delete_relation(self, uuid: str) -> bool:
        """Delete a relationship by UUID."""
        initial_len = len(self.relations)
        self.relations = [r for r in self.relations if r.relationship_uuid != uuid]
        self.relation_count = len(self.relations)
        return len(self.relations) < initial_len

    def save_to_csv(self, nodes_path: str | Path, relations_path: str | Path):
        """
        Persist current graph state directly back to nodes.csv and relations.csv.
        """
        # Build nodes DataFrame
        nodes_data = []
        for n in self.nodes:
            props_str = json.dumps(n.properties) if n.properties else "{}"
            nodes_data.append({
                "name": n.name,
                "uuid": n.uuid,
                "properties": props_str,
            })
        nodes_df = pd.DataFrame(nodes_data)
        nodes_df.to_csv(nodes_path, index=False)

        # Build relations DataFrame
        rels_data = []
        for r in self.relations:
            props_str = json.dumps(r.properties) if r.properties else "{}"
            rels_data.append({
                "source_uuid": r.source_uuid,
                "target_uuid": r.target_uuid,
                "relationship_name": r.relationship_name,
                "relationship_uuid": r.relationship_uuid,
                "properties": props_str,
            })
        rels_df = pd.DataFrame(rels_data)
        rels_df.to_csv(relations_path, index=False)


__all__ = ["Node", "Relation", "Graph"]

