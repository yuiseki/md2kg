"""
Tests for networkx converter module.

This module tests the conversion from CSV files to NetworkX graphs.
"""

import os
import tempfile
import shutil
import pytest
import pandas as pd
import networkx as nx
from pathlib import Path

from md2kg.converters.networkx_converter import NetworkxConverter


@pytest.fixture
def csv_data():
    """Fixture to provide sample CSV data for testing."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Create sample nodes.csv
    nodes_data = [
        {"id": "node1", "title": "Node 1", "filepath": "/path/to/node1.md", "labels": "Document", "tags": "tag1;tag2"},
        {"id": "node2", "title": "Node 2", "filepath": "/path/to/node2.md", "labels": "Document", "tags": "tag2;tag3"}
    ]
    nodes_df = pd.DataFrame(nodes_data)
    nodes_csv = os.path.join(temp_dir, "nodes.csv")
    nodes_df.to_csv(nodes_csv, index=False)
    
    # Create sample edges.csv
    edges_data = [
        {"src_id": "node1", "dst_id": "node2", "type": "LINK", "context_snippet": "Some context"}
    ]
    edges_df = pd.DataFrame(edges_data)
    edges_csv = os.path.join(temp_dir, "edges.csv")
    edges_df.to_csv(edges_csv, index=False)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


def test_convert_to_networkx(csv_data):
    """Test conversion from CSV to NetworkX graph."""
    converter = NetworkxConverter()
    graph = converter.convert(csv_data)
    
    # Verify graph structure
    assert isinstance(graph, nx.Graph)
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    
    # Verify node attributes
    assert graph.nodes["node1"]["title"] == "Node 1"
    assert graph.nodes["node2"]["title"] == "Node 2"
    
    # Verify edge attributes
    assert graph.edges[("node1", "node2")]["type"] == "LINK"


def test_convert_to_gml(csv_data):
    """Test conversion from CSV to GML format."""
    converter = NetworkxConverter()
    gml_path = converter.to_gml(csv_data, output_path=os.path.join(csv_data, "graph.gml"))
    
    # Verify GML file was created
    assert os.path.exists(gml_path)
    
    # Check if GML file can be loaded back
    loaded_graph = nx.read_gml(gml_path)
    assert len(loaded_graph.nodes) == 2
    assert len(loaded_graph.edges) == 1


def test_convert_to_langchain(csv_data):
    """Test conversion compatible with LangChain."""
    try:
        from langchain.graphs import NetworkxEntityGraph
        
        converter = NetworkxConverter()
        gml_path = converter.to_gml(csv_data, output_path=os.path.join(csv_data, "langchain.gml"))
        
        # Try loading with LangChain
        lg_graph = NetworkxEntityGraph.from_gml(gml_path)
        
        # Basic verification
        assert len(lg_graph._graph.nodes) == 2
        
    except ImportError:
        pytest.skip("LangChain not installed, skipping test")


def test_node_attributes_preserved(csv_data):
    """Test that node attributes are properly preserved."""
    converter = NetworkxConverter()
    graph = converter.convert(csv_data)
    
    # Verify all attributes are preserved
    node1 = graph.nodes["node1"]
    assert node1["filepath"] == "/path/to/node1.md"
    assert "tags" in node1
    assert "tag1" in node1["tags"]
    assert "tag2" in node1["tags"]
