"""
Graph builder module for md2kg.

This module handles building a complete knowledge graph from multiple Markdown files,
merging duplicate nodes, and resolving references between documents.
"""

import os
from typing import List, Dict, Tuple, Set
from pathlib import Path
from md2kg.models import Node, Edge
from md2kg.parser import parse_markdown


class GraphBuilder:
    """
    Builds a knowledge graph from multiple Markdown files.
    Handles merging of duplicate nodes and edge creation between documents.
    """
    
    def __init__(self):
        """Initialize an empty graph builder."""
        # Key: node ID, Value: Node object
        self._nodes_by_id: Dict[str, Node] = {}
        # Key: node title, Value: set of node IDs with this title
        self._node_ids_by_title: Dict[str, Set[str]] = {}
        # List of all edges
        self._edges: List[Edge] = []
        # Track files that have been processed
        self._processed_files: Set[str] = set()
    
    def add_file(self, filepath: str) -> None:
        """
        Add a single Markdown file to the graph.
        
        Args:
            filepath: Path to the Markdown file
        """
        # Skip if file already processed
        abs_path = os.path.abspath(filepath)
        if abs_path in self._processed_files:
            return
        
        # Mark file as processed
        self._processed_files.add(abs_path)
        
        # Read file content
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            # Handle file read error
            print(f"Error reading file {filepath}: {e}")
            return
        
        # Parse Markdown content
        nodes, edges = parse_markdown(abs_path, content)
        
        # Add nodes and edges to the graph
        for node in nodes:
            self._add_node(node)
        
        for edge in edges:
            self._edges.append(edge)
    
    def add_directory(self, dirpath: str, pattern: str = "**/*.md") -> None:
        """
        Add all Markdown files in a directory to the graph.
        
        Args:
            dirpath: Path to the directory containing Markdown files
            pattern: Glob pattern to match files (default: "**/*.md")
        """
        abs_path = os.path.abspath(dirpath)
        for filepath in Path(abs_path).glob(pattern):
            # Skip directories
            if os.path.isdir(filepath):
                continue
            
            # Add file to graph
            self.add_file(str(filepath))
    
    def _add_node(self, node: Node) -> None:
        """
        Add a node to the graph, handling duplicate resolution.
        
        Args:
            node: Node object to add
        """
        # If node already exists by ID, skip it
        if node.id in self._nodes_by_id:
            return
        
        # Add the node first
        self._nodes_by_id[node.id] = node
        
        # Register node ID by title
        if node.title not in self._node_ids_by_title:
            self._node_ids_by_title[node.title] = set()
        self._node_ids_by_title[node.title].add(node.id)
        
        # Check if node with same title exists
        existing_ids = self._node_ids_by_title[node.title]
        
        # Skip if this is the only ID for this title
        if len(existing_ids) <= 1:
            return
            
        # For placeholder nodes (empty filepath), try to match with existing node
        if node.filepath == "":
            # Find non-placeholder node with same title
            for existing_id in existing_ids:
                if existing_id != node.id and self._nodes_by_id[existing_id].filepath != "":
                    # Point this placeholder to the real node
                    self._nodes_by_id[node.id] = self._nodes_by_id[existing_id]
                    return
        else:
            # For real nodes, update placeholders to point to this node
            for existing_id in existing_ids:
                if existing_id != node.id and self._nodes_by_id[existing_id].filepath == "":
                    # Point placeholder to this real node
                    self._nodes_by_id[existing_id] = node
    
    def get_graph(self) -> Tuple[List[Node], List[Edge]]:
        """
        Get the built graph as lists of unique nodes and edges.
        
        Returns:
            Tuple of (nodes, edges)
        """
        # Get unique nodes using a dictionary to track object identity
        unique_nodes = {}
        for node_id, node in self._nodes_by_id.items():
            # Use object ID as key to ensure uniqueness
            obj_id = id(node)
            if obj_id not in unique_nodes:
                unique_nodes[obj_id] = node
        
        # Convert to list to return
        return list(unique_nodes.values()), self._edges
