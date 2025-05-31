"""
CSV exporter module for md2kg.

This module handles exporting nodes and edges to CSV files 
that comply with RFC 4180 for use with Neo4j, DuckDB and other systems.
"""

import os
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from md2kg.models import Node, Edge


class CsvExporter:
    """
    Exports graph data (nodes and edges) to CSV files.
    """
    
    def __init__(self):
        """Initialize the CSV exporter."""
        pass
    
    def export(
        self, 
        nodes: List[Node], 
        edges: List[Edge], 
        output_dir: str,
        nodes_filename: str = "nodes.csv",
        edges_filename: str = "edges.csv"
    ) -> Dict[str, str]:
        """
        Export nodes and edges to CSV files.
        
        Args:
            nodes: List of Node objects
            edges: List of Edge objects
            output_dir: Directory to write CSV files
            nodes_filename: Custom filename for nodes CSV (default: "nodes.csv")
            edges_filename: Custom filename for edges CSV (default: "edges.csv")
            
        Returns:
            Dictionary with paths to the output files
        """
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Create complete file paths
        nodes_path = os.path.join(output_dir, nodes_filename)
        edges_path = os.path.join(output_dir, edges_filename)
        
        # Convert nodes to a list of dictionaries
        nodes_data = self._nodes_to_dicts(nodes)
        
        # Convert edges to a list of dictionaries
        edges_data = self._edges_to_dicts(edges)
        
        # Convert to pandas DataFrames
        nodes_df = pd.DataFrame(nodes_data)
        edges_df = pd.DataFrame(edges_data)
        
        # Write DataFrames to CSV files
        self._write_nodes_csv(nodes_df, nodes_path)
        self._write_edges_csv(edges_df, edges_path)
        
        return {
            "nodes_csv": nodes_path,
            "edges_csv": edges_path
        }
    
    def _nodes_to_dicts(self, nodes: List[Node]) -> List[Dict[str, Any]]:
        """
        Convert Node objects to dictionaries for DataFrame creation.
        
        Args:
            nodes: List of Node objects
            
        Returns:
            List of dictionaries with node data
        """
        nodes_data = []
        for node in nodes:
            # Convert lists to required string formats
            labels_str = ",".join(node.labels) if node.labels else "Document"
            tags_str = ";".join(node.tags) if node.tags else ""
            
            nodes_data.append({
                "id": node.id,
                "title": node.title,
                "filepath": node.filepath,
                "labels": labels_str,
                "tags": tags_str
            })
        return nodes_data
    
    def _edges_to_dicts(self, edges: List[Edge]) -> List[Dict[str, Any]]:
        """
        Convert Edge objects to dictionaries for DataFrame creation.
        
        Args:
            edges: List of Edge objects
            
        Returns:
            List of dictionaries with edge data
        """
        edges_data = []
        for edge in edges:
            edges_data.append({
                "src_id": edge.src_id,
                "dst_id": edge.dst_id,
                "type": edge.type,
                "context_snippet": edge.context_snippet or ""
            })
        return edges_data
    
    def _write_nodes_csv(self, df: pd.DataFrame, path: str) -> None:
        """
        Write nodes DataFrame to CSV file.
        
        Args:
            df: DataFrame containing node data
            path: Path to write CSV file
        """
        # Ensure columns are in the correct order
        columns = ["id", "title", "filepath", "labels", "tags"]
        if set(columns).issubset(set(df.columns)):
            # Reorder columns if all expected columns exist
            df = df[columns]
        
        # Write to CSV with RFC 4180 compliance
        df.to_csv(path, index=False, encoding='utf-8', quoting=1)
    
    def _write_edges_csv(self, df: pd.DataFrame, path: str) -> None:
        """
        Write edges DataFrame to CSV file.
        
        Args:
            df: DataFrame containing edge data
            path: Path to write CSV file
        """
        # Ensure columns are in the correct order
        columns = ["src_id", "dst_id", "type", "context_snippet"]
        if set(columns).issubset(set(df.columns)):
            # Reorder columns if all expected columns exist
            df = df[columns]
        
        # Write to CSV with RFC 4180 compliance
        df.to_csv(path, index=False, encoding='utf-8', quoting=1)
