"""API routes for graph validation and loading."""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List, Dict, Any
from validators import CSVValidator
from validators.graph_parser import GraphParser

router = APIRouter(prefix="/api", tags=["graph"])


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@router.post("/validate")
async def validate_files(
    nodes_file: UploadFile = File(...),
    relations_file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Validate node and relation CSV files.
    
    Args:
        nodes_file: Nodes CSV file
        relations_file: Relations CSV file
        
    Returns:
        Validation result with errors and counts
    """
    errors = []
    
    try:
        # Read files
        nodes_content = (await nodes_file.read()).decode('utf-8')
        relations_content = (await relations_file.read()).decode('utf-8')
    except UnicodeDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File encoding error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File read error: {str(e)}"
        )
    
    # Validate nodes CSV
    nodes_valid, nodes_errors, nodes_df = CSVValidator.validate_nodes_csv(nodes_content)
    errors.extend(nodes_errors)
    
    if not nodes_valid:
        return {
            "valid": False,
            "errors": errors,
            "node_count": 0,
            "relation_count": 0
        }
    
    # Get valid node UUIDs
    valid_uuids = set(nodes_df['uuid'].astype(str).str.strip().tolist())
    
    # Validate relations CSV
    relations_valid, relations_errors, relations_df = CSVValidator.validate_relations_csv(
        relations_content,
        valid_uuids
    )
    errors.extend(relations_errors)
    
    is_valid = nodes_valid and relations_valid
    
    return {
        "valid": is_valid,
        "errors": errors,
        "node_count": len(nodes_df),
        "relation_count": len(relations_df)
    }


@router.post("/load-graph")
async def load_graph(
    nodes_file: UploadFile = File(...),
    relations_file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Load and parse graph data from CSV files.
    
    Args:
        nodes_file: Nodes CSV file
        relations_file: Relations CSV file
        
    Returns:
        Graph data structure with nodes and relations
    """
    errors = []
    
    try:
        # Read files
        nodes_content = (await nodes_file.read()).decode('utf-8')
        relations_content = (await relations_file.read()).decode('utf-8')
    except UnicodeDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File encoding error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File read error: {str(e)}"
        )
    
    # Validate nodes CSV
    nodes_valid, nodes_errors, nodes_df = CSVValidator.validate_nodes_csv(nodes_content)
    errors.extend(nodes_errors)
    
    if not nodes_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": errors, "message": "Invalid nodes CSV"}
        )
    
    # Get valid node UUIDs
    valid_uuids = set(nodes_df['uuid'].astype(str).str.strip().tolist())
    
    # Validate relations CSV
    relations_valid, relations_errors, relations_df = CSVValidator.validate_relations_csv(
        relations_content,
        valid_uuids
    )
    errors.extend(relations_errors)
    
    if not relations_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": errors, "message": "Invalid relations CSV"}
        )
    
    # Build graph
    try:
        graph = GraphParser.build_graph(nodes_df, relations_df)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Graph parsing error: {str(e)}"
        )
    
    return {
        "nodes": [node.model_dump() for node in graph.nodes],
        "relations": [rel.model_dump() for rel in graph.relations],
        "node_count": graph.node_count,
        "relation_count": graph.relation_count
    }
