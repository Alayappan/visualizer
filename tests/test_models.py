"""Unit tests for desktop graph data models."""
import pytest
from pydantic import ValidationError
from src.models import Node, Relation, Graph


class TestNodeModel:
    """Test cases for Node model."""

    def test_node_creation_valid(self):
        """Test creating a valid node."""
        node = Node(
            name="Test Node",
            uuid="550e8400-e29b-41d4-a716-446655440000",
            properties={"key": "value", "cpu": "80%"},
        )
        assert node.name == "Test Node"
        assert node.uuid == "550e8400-e29b-41d4-a716-446655440000"
        assert node.properties == {"key": "value", "cpu": "80%"}

    def test_node_creation_without_properties(self):
        """Test creating a node without properties."""
        node = Node(name="Test Node", uuid="550e8400-e29b-41d4-a716-446655440000")
        assert node.properties is None

    def test_node_invalid_uuid(self):
        """Test that invalid UUID raises error."""
        with pytest.raises(ValidationError):
            Node(name="Test", uuid="not-a-uuid")

    def test_node_empty_name(self):
        """Test that empty name raises error."""
        with pytest.raises(ValidationError):
            Node(name="", uuid="550e8400-e29b-41d4-a716-446655440000")

    def test_node_whitespace_name(self):
        """Test that whitespace-only name raises error."""
        with pytest.raises(ValidationError):
            Node(name="   ", uuid="550e8400-e29b-41d4-a716-446655440000")


class TestRelationModel:
    """Test cases for Relation model."""

    def test_relation_creation_valid(self):
        """Test creating a valid relation."""
        relation = Relation(
            source_uuid="550e8400-e29b-41d4-a716-446655440000",
            target_uuid="550e8400-e29b-41d4-a716-446655440001",
            relationship_name="depends_on",
            relationship_uuid="550e8400-e29b-41d4-a716-446655440002",
            properties={"strength": "high"},
        )
        assert relation.source_uuid == "550e8400-e29b-41d4-a716-446655440000"
        assert relation.target_uuid == "550e8400-e29b-41d4-a716-446655440001"
        assert relation.relationship_name == "depends_on"
        assert relation.relationship_uuid == "550e8400-e29b-41d4-a716-446655440002"
        assert relation.properties == {"strength": "high"}

    def test_relation_invalid_source_uuid(self):
        """Test that invalid source UUID raises error."""
        with pytest.raises(ValidationError):
            Relation(
                source_uuid="invalid-uuid",
                target_uuid="550e8400-e29b-41d4-a716-446655440001",
                relationship_name="test",
                relationship_uuid="550e8400-e29b-41d4-a716-446655440002",
            )

    def test_relation_invalid_relationship_name(self):
        """Test that empty relationship name raises error."""
        with pytest.raises(ValidationError):
            Relation(
                source_uuid="550e8400-e29b-41d4-a716-446655440000",
                target_uuid="550e8400-e29b-41d4-a716-446655440001",
                relationship_name="",
                relationship_uuid="550e8400-e29b-41d4-a716-446655440002",
            )


class TestGraphModel:
    """Test cases for Graph model."""

    def test_graph_creation_and_lookups(self):
        """Test creating a graph and helper methods."""
        node1 = Node(name="Node1", uuid="550e8400-e29b-41d4-a716-446655440000")
        node2 = Node(name="Node2", uuid="550e8400-e29b-41d4-a716-446655440001")
        rel1 = Relation(
            source_uuid="550e8400-e29b-41d4-a716-446655440000",
            target_uuid="550e8400-e29b-41d4-a716-446655440001",
            relationship_name="connects",
            relationship_uuid="550e8400-e29b-41d4-a716-446655440002",
        )

        graph = Graph(
            nodes=[node1, node2],
            relations=[rel1],
            node_count=2,
            relation_count=1,
        )

        assert graph.node_count == 2
        assert graph.relation_count == 1
        assert len(graph.nodes) == 2
        assert len(graph.relations) == 1
        assert graph.get_node("550e8400-e29b-41d4-a716-446655440000") == node1
        assert graph.get_node("non-existent") is None
        assert len(graph.get_relations_for_node("550e8400-e29b-41d4-a716-446655440000")) == 1
        assert len(graph.get_relations_for_node("non-existent")) == 0
