"""Unit tests for graph parser."""
import pytest
import pandas as pd
from validators.graph_parser import GraphParser
from models import Node, Relation


class TestGraphParser:
    """Test cases for graph parsing."""
    
    def test_parse_valid_nodes(self):
        """Test parsing valid nodes."""
        df = pd.DataFrame({
            'name': ['Server-1', 'Server-2'],
            'uuid': [
                '550e8400-e29b-41d4-a716-446655440000',
                '550e8400-e29b-41d4-a716-446655440001'
            ],
            'properties': ['{"cpu": "80%"}', None]
        })
        
        nodes = GraphParser.parse_nodes(df)
        
        assert len(nodes) == 2
        assert nodes[0].name == 'Server-1'
        assert nodes[0].uuid == '550e8400-e29b-41d4-a716-446655440000'
        assert nodes[0].properties == {'cpu': '80%'}
        assert nodes[1].properties is None
    
    def test_parse_nodes_with_properties(self):
        """Test parsing nodes with JSON properties."""
        df = pd.DataFrame({
            'name': ['Node-1'],
            'uuid': ['550e8400-e29b-41d4-a716-446655440000'],
            'properties': ['{"type": "server", "cpu": "80%", "memory": "16GB"}']
        })
        
        nodes = GraphParser.parse_nodes(df)
        
        assert len(nodes) == 1
        assert nodes[0].properties['type'] == 'server'
        assert nodes[0].properties['cpu'] == '80%'
        assert nodes[0].properties['memory'] == '16GB'
    
    def test_parse_valid_relations(self):
        """Test parsing valid relations."""
        df = pd.DataFrame({
            'source_uuid': ['550e8400-e29b-41d4-a716-446655440000'],
            'target_uuid': ['550e8400-e29b-41d4-a716-446655440001'],
            'relationship_name': ['depends_on'],
            'relationship_uuid': ['550e8400-e29b-41d4-a716-446655440002'],
            'properties': ['{"strength": "high"}']
        })
        
        relations = GraphParser.parse_relations(df)
        
        assert len(relations) == 1
        assert relations[0].relationship_name == 'depends_on'
        assert relations[0].properties == {'strength': 'high'}
    
    def test_parse_empty_relations(self):
        """Test parsing empty relations."""
        df = pd.DataFrame({
            'source_uuid': [],
            'target_uuid': [],
            'relationship_name': [],
            'relationship_uuid': [],
            'properties': []
        })
        
        relations = GraphParser.parse_relations(df)
        
        assert len(relations) == 0
    
    def test_build_complete_graph(self):
        """Test building a complete graph."""
        nodes_df = pd.DataFrame({
            'name': ['Node-1', 'Node-2'],
            'uuid': [
                '550e8400-e29b-41d4-a716-446655440000',
                '550e8400-e29b-41d4-a716-446655440001'
            ],
            'properties': [None, None]
        })
        
        relations_df = pd.DataFrame({
            'source_uuid': ['550e8400-e29b-41d4-a716-446655440000'],
            'target_uuid': ['550e8400-e29b-41d4-a716-446655440001'],
            'relationship_name': ['connects'],
            'relationship_uuid': ['550e8400-e29b-41d4-a716-446655440002'],
            'properties': [None]
        })
        
        graph = GraphParser.build_graph(nodes_df, relations_df)
        
        assert graph.node_count == 2
        assert graph.relation_count == 1
        assert len(graph.nodes) == 2
        assert len(graph.relations) == 1
    
    def test_build_graph_with_isolated_nodes(self):
        """Test building graph with isolated nodes."""
        nodes_df = pd.DataFrame({
            'name': ['Node-1', 'Node-2', 'Node-3'],
            'uuid': [
                '550e8400-e29b-41d4-a716-446655440000',
                '550e8400-e29b-41d4-a716-446655440001',
                '550e8400-e29b-41d4-a716-446655440002'
            ],
            'properties': [None, None, None]
        })
        
        relations_df = pd.DataFrame({
            'source_uuid': ['550e8400-e29b-41d4-a716-446655440000'],
            'target_uuid': ['550e8400-e29b-41d4-a716-446655440001'],
            'relationship_name': ['connects'],
            'relationship_uuid': ['550e8400-e29b-41d4-a716-446655440003'],
            'properties': [None]
        })
        
        graph = GraphParser.build_graph(nodes_df, relations_df)
        
        assert graph.node_count == 3
        assert graph.relation_count == 1
