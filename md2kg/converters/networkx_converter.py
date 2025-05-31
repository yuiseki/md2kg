"""
NetworkX converter module.

This module provides functionality to convert CSV knowledge graph data
to NetworkX graphs and GML files that are compatible with LangChain.
"""

import os
import pandas as pd
import networkx as nx
from pathlib import Path
from typing import Dict, Any, List, Optional, Union


class NetworkxConverter:
    """
    Converts knowledge graph CSV files to NetworkX graphs and GML format.
    
    This converter reads nodes.csv and edges.csv files and builds a NetworkX
    graph that can be used for analysis or exported to GML format for use
    with LangChain's NetworkxEntityGraph.
    """
    
    def convert(self, csv_dir: Union[str, Path]) -> nx.Graph:
        """
        Convert CSV files to a NetworkX graph.
        
        Args:
            csv_dir: Directory containing nodes.csv and edges.csv files
            
        Returns:
            NetworkX graph object
        
        Raises:
            FileNotFoundError: If nodes.csv or edges.csv are not found
            ValueError: If the CSV files have unexpected structure
        """
        csv_dir = Path(csv_dir)
        nodes_path = csv_dir / "nodes.csv"
        edges_path = csv_dir / "edges.csv"
        
        if not nodes_path.exists():
            raise FileNotFoundError(f"Nodes CSV file not found: {nodes_path}")
        if not edges_path.exists():
            raise FileNotFoundError(f"Edges CSV file not found: {edges_path}")
        
        # Load CSV files
        nodes_df = pd.read_csv(nodes_path)
        edges_df = pd.read_csv(edges_path)
        
        # Create undirected graph (can be changed to DiGraph if needed)
        graph = nx.Graph()
        
        # Add nodes with attributes
        for _, node in nodes_df.iterrows():
            node_attrs = dict(node)
            node_id = node_attrs.pop('id')
            
            # Process tags from semicolon-separated to list
            if 'tags' in node_attrs and node_attrs['tags'] and isinstance(node_attrs['tags'], str):
                node_attrs['tags'] = node_attrs['tags'].split(';')
            elif 'tags' in node_attrs and not isinstance(node_attrs['tags'], str):
                # Handle case where tags is not a string (e.g., NaN or other non-string value)
                node_attrs['tags'] = []
                
            # Add node to graph
            graph.add_node(node_id, **node_attrs)
        
        # Add edges with attributes
        for _, edge in edges_df.iterrows():
            edge_attrs = dict(edge)
            src_id = edge_attrs.pop('src_id')
            dst_id = edge_attrs.pop('dst_id')
            
            # Add edge to graph
            graph.add_edge(src_id, dst_id, **edge_attrs)
        
        return graph
    
    def to_gml(self, csv_dir: Union[str, Path], output_path: Optional[str] = None) -> str:
        """
        Convert CSV files to GML format.
        
        Args:
            csv_dir: Directory containing nodes.csv and edges.csv files
            output_path: Path to output GML file (optional)
            
        Returns:
            Path to the generated GML file
            
        Raises:
            FileNotFoundError: If nodes.csv or edges.csv are not found
            ValueError: If output directory doesn't exist
        """
        # Convert to NetworkX graph first
        graph = self.convert(csv_dir)
        
        # Determine output path if not provided
        if output_path is None:
            csv_dir = Path(csv_dir)
            output_path = str(csv_dir / "graph.gml")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Write to GML file
        nx.write_gml(graph, output_path)
        return output_path
