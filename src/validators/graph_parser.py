"""Graph parser for building graph structures from CSV data."""
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import pandas as pd
from src.models import Node, Relation, Graph
from src.validators import CSVValidator


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
            props_str = row.get("properties")

            if not pd.isna(props_str) and str(props_str).strip() and str(props_str).strip().lower() != "nan":
                try:
                    properties = json.loads(str(props_str).strip())
                except (json.JSONDecodeError, TypeError):
                    properties = None

            node = Node(
                name=str(row["name"]).strip(),
                uuid=str(row["uuid"]).strip(),
                properties=properties,
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
            props_str = row.get("properties")

            if not pd.isna(props_str) and str(props_str).strip() and str(props_str).strip().lower() != "nan":
                try:
                    properties = json.loads(str(props_str).strip())
                except (json.JSONDecodeError, TypeError):
                    properties = None

            relation = Relation(
                source_uuid=str(row["source_uuid"]).strip(),
                target_uuid=str(row["target_uuid"]).strip(),
                relationship_name=str(row["relationship_name"]).strip(),
                relationship_uuid=str(row["relationship_uuid"]).strip(),
                properties=properties,
            )
            relations.append(relation)

        return relations

    @classmethod
    def build_graph(cls, nodes_df: pd.DataFrame, relations_df: pd.DataFrame) -> Graph:
        """
        Build complete graph from nodes and relations dataframes.

        Args:
            nodes_df: Nodes dataframe
            relations_df: Relations dataframe

        Returns:
            Graph object with all nodes and relations
        """
        nodes = cls.parse_nodes(nodes_df)
        relations = cls.parse_relations(relations_df)

        return Graph(
            nodes=nodes,
            relations=relations,
            node_count=len(nodes),
            relation_count=len(relations),
        )

    @classmethod
    def load_graph_from_sources(
        cls, nodes_source: str | Path, relations_source: str | Path
    ) -> Tuple[bool, List[str], Optional[Graph]]:
        """
        Convenience method to validate sources and build a Graph object.

        Returns:
            Tuple of (is_valid, errors_list, graph_or_none)
        """
        errors: List[str] = []

        # Validate nodes
        nodes_valid, node_errs, nodes_df = CSVValidator.validate_nodes_csv(nodes_source)
        errors.extend(node_errs)
        if not nodes_valid:
            return False, errors, None

        # Extract valid node UUIDs
        valid_uuids = set(nodes_df["uuid"].astype(str).str.strip().tolist())

        # Validate relations
        rels_valid, rel_errs, rels_df = CSVValidator.validate_relations_csv(
            relations_source, valid_uuids
        )
        errors.extend(rel_errs)
        if not rels_valid:
            return False, errors, None

        # Build graph
        graph = cls.build_graph(nodes_df, rels_df)
        return True, [], graph


__all__ = ["GraphParser"]
