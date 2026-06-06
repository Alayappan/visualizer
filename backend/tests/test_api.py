"""Integration tests for API endpoints."""
import pytest
import os
from io import BytesIO
from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def fixture_dir():
    """Get path to fixtures directory."""
    return os.path.join(os.path.dirname(__file__), 'fixtures')


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestValidateEndpoint:
    """Test validate endpoint."""
    
    def test_validate_valid_files(self, client, fixture_dir):
        """Test validate endpoint with valid files."""
        with open(os.path.join(fixture_dir, 'valid_nodes.csv'), 'rb') as f:
            nodes_content = f.read()
        with open(os.path.join(fixture_dir, 'valid_relations.csv'), 'rb') as f:
            relations_content = f.read()
        
        response = client.post(
            "/api/validate",
            files={
                "nodes_file": ("nodes.csv", BytesIO(nodes_content)),
                "relations_file": ("relations.csv", BytesIO(relations_content))
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["node_count"] == 3
        assert data["relation_count"] == 2
        assert len(data["errors"]) == 0
    
    def test_validate_invalid_nodes(self, client, fixture_dir):
        """Test validate endpoint with invalid nodes."""
        with open(os.path.join(fixture_dir, 'invalid_nodes_bad_uuid.csv'), 'rb') as f:
            nodes_content = f.read()
        with open(os.path.join(fixture_dir, 'valid_relations.csv'), 'rb') as f:
            relations_content = f.read()
        
        response = client.post(
            "/api/validate",
            files={
                "nodes_file": ("nodes.csv", BytesIO(nodes_content)),
                "relations_file": ("relations.csv", BytesIO(relations_content))
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0


class TestLoadGraphEndpoint:
    """Test load-graph endpoint."""
    
    def test_load_graph_valid_files(self, client, fixture_dir):
        """Test load-graph endpoint with valid files."""
        with open(os.path.join(fixture_dir, 'valid_nodes.csv'), 'rb') as f:
            nodes_content = f.read()
        with open(os.path.join(fixture_dir, 'valid_relations.csv'), 'rb') as f:
            relations_content = f.read()
        
        response = client.post(
            "/api/load-graph",
            files={
                "nodes_file": ("nodes.csv", BytesIO(nodes_content)),
                "relations_file": ("relations.csv", BytesIO(relations_content))
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["node_count"] == 3
        assert data["relation_count"] == 2
        assert len(data["nodes"]) == 3
        assert len(data["relations"]) == 2
        
        # Check node structure
        node = data["nodes"][0]
        assert "name" in node
        assert "uuid" in node
        assert "properties" in node
        
        # Check relation structure
        rel = data["relations"][0]
        assert "source_uuid" in rel
        assert "target_uuid" in rel
        assert "relationship_name" in rel
        assert "relationship_uuid" in rel
        assert "properties" in rel
    
    def test_load_graph_invalid_nodes(self, client, fixture_dir):
        """Test load-graph endpoint with invalid nodes."""
        with open(os.path.join(fixture_dir, 'invalid_nodes_bad_uuid.csv'), 'rb') as f:
            nodes_content = f.read()
        with open(os.path.join(fixture_dir, 'valid_relations.csv'), 'rb') as f:
            relations_content = f.read()
        
        response = client.post(
            "/api/load-graph",
            files={
                "nodes_file": ("nodes.csv", BytesIO(nodes_content)),
                "relations_file": ("relations.csv", BytesIO(relations_content))
            }
        )
        
        assert response.status_code == 400
    
    def test_load_graph_orphaned_relations(self, client, fixture_dir):
        """Test load-graph endpoint with orphaned relations."""
        with open(os.path.join(fixture_dir, 'valid_nodes.csv'), 'rb') as f:
            nodes_content = f.read()
        with open(os.path.join(fixture_dir, 'invalid_relations_orphaned.csv'), 'rb') as f:
            relations_content = f.read()
        
        response = client.post(
            "/api/load-graph",
            files={
                "nodes_file": ("nodes.csv", BytesIO(nodes_content)),
                "relations_file": ("relations.csv", BytesIO(relations_content))
            }
        )
        
        assert response.status_code == 400
