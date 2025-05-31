"""
Data models for md2kg.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Node:
    """Node representing a document or entity in the knowledge graph."""
    id: str
    title: str
    filepath: str
    labels: List[str] = field(default_factory=lambda: ["Document"])
    tags: List[str] = field(default_factory=list)


@dataclass
class Edge:
    """Edge representing a link between two nodes."""
    src_id: str
    dst_id: str
    type: str = "LINK"
    context_snippet: Optional[str] = None
