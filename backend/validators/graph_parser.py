"""Graph parser for building graph structures from CSV data."""
import json
from typing import Dict, List, Any, Optional
import pandas as pd
from models import Node, Relation, Graph


class GraphParser:
    """Parses CSV data and builds graph structures."""
    
    @staticmethod
    def parse_nodes(df: pd.DataFrame) -> List[Node]:
        """
        Parse nodes dataframe into Node objects.
        
        Args:
            df: DataFrame with columns: name, uuid, properties
            
        Returns:
            List of Node objects
        """
        nodes = []
        for _, row in df.iterrows():
            properties = None
            props_str = row.get('properties')
            
            if not pd.isna(props_str) and props_str and isinstance(props_str, str):
                try:
                    properties = json.loads(props_str)
                except json.JSONDecodeError:
                    properties = None
            
            node = Node(
                name=str(row['name']).strip(),
                uuid=str(row['uuid']).strip(),
                properties=properties
            )
            nodes.append(node)
        
        return nodes
    
    @staticmethod
    def parse_relations(df: pd.DataFrame) -> List[Relation]:
        """
        Parse relations dataframe into Relation objects.
        
        Args:
            df: DataFrame with columns: source_uuid, target_uuid, relationship_name,
                relationship_uuid, properties
                
        Returns:
            List of Relation objects
        """
        relations = []
        
        if len(df) == 0:
            return relations
        
        for _, row in df.iterrows():
            properties = None
            props_str = row.get('properties')
            
            if not pd.isna(props_str) and props_str and isinstance(props_str, str):
                try:
                    properties = json.loads(props_str)
                except json.JSONDecodeError:
                    properties = None
            
            relation = Relation(
                source_uuid=str(row['source_uuid']).strip(),
                target_uuid=str(row['target_uuid']).strip(),
                relationship_name=str(row['relationship_name']).strip(),
                relationship_uuid=str(row['relationship_uuid']).strip(),
                properties=properties
            )
            relations.append(relation)
        
        return relations
    
    @staticmethod
    def build_graph(nodes_df: pd.DataFrame, relations_df: pd.DataFrame) -> Graph:
        """
        Build complete graph from nodes and relations dataframes.
        
        Args:
            nodes_df: Nodes dataframe
            relations_df: Relations dataframe
            
        Returns:
            Graph object with all nodes and relations
        """
        nodes = GraphParser.parse_nodes(nodes_df)
        relations = GraphParser.parse_relations(relations_df)
        
        graph = Graph(
            nodes=nodes,
            relations=relations,
            node_count=len(nodes),
            relation_count=len(relations)
        )
        
        return graph
