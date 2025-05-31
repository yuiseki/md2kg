"""
Markdown parser module for extracting WikiLinks.

This module uses markdown-it-py and extensions to parse Markdown files
and extract WikiLinks to build a knowledge graph.
"""

import re
import hashlib
from typing import List, Tuple, Dict, Any, Optional
import yaml

from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from md2kg.models import Node, Edge


def _extract_front_matter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Extract YAML front matter from markdown content.
    
    Args:
        content: The markdown content with possible front matter
        
    Returns:
        Tuple of (front_matter_dict, remaining_content)
    """
    if content.startswith('---'):
        try:
            # Find the end of front matter
            end_pos = content.find('---', 3)
            if end_pos != -1:
                front_matter_text = content[3:end_pos].strip()
                front_matter = yaml.safe_load(front_matter_text) or {}
                remaining_content = content[end_pos+3:].strip()
                return front_matter, remaining_content
        except yaml.YAMLError:
            pass
    
    return {}, content


def _extract_title(content: str, filepath: str) -> str:
    """
    Extract title from markdown content.
    Uses the first h1 heading or filename if no heading found.
    
    Args:
        content: The markdown content
        filepath: Path to the file for fallback title
        
    Returns:
        Title string
    """
    # Try to find the first h1 heading
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    
    # Fallback to filename without extension
    import os
    filename = os.path.basename(filepath)
    return os.path.splitext(filename)[0]


def _generate_id(filepath: str, title: str) -> str:
    """
    Generate a unique SHA-256 ID for a node based on filepath and title.
    
    Args:
        filepath: Path to the markdown file
        title: Title of the document
        
    Returns:
        SHA-256 hash string
    """
    unique_string = f"{filepath}:{title}"
    return hashlib.sha256(unique_string.encode('utf-8')).hexdigest()


def _extract_wikilinks(content: str) -> List[str]:
    """
    Extract WikiLinks from markdown content.
    
    Args:
        content: The markdown content
        
    Returns:
        List of link titles found in WikiLinks
    """
    # Simple regex to extract WikiLinks [[Link]]
    wikilinks = re.findall(r'\[\[([^\]]+)\]\]', content)
    return wikilinks


def parse_markdown(filepath: str, content: str) -> Tuple[List[Node], List[Edge]]:
    """
    Parse markdown content to extract nodes and edges.
    
    Args:
        filepath: Path to the markdown file
        content: The markdown content
        
    Returns:
        Tuple of (nodes, edges)
    """
    # Extract front matter and clean content
    front_matter, clean_content = _extract_front_matter(content)
    
    # Extract title
    title = _extract_title(clean_content, filepath)
    
    # Generate node ID
    node_id = _generate_id(filepath, title)
    
    # Extract tags from front matter
    tags = front_matter.get('tags', [])
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(',')]
    
    # Create the source node
    source_node = Node(
        id=node_id,
        title=title,
        filepath=filepath,
        tags=tags
    )
    
    # Extract WikiLinks
    wikilinks = _extract_wikilinks(clean_content)
    
    nodes = [source_node]
    edges = []
    
    # Create target nodes and edges for each WikiLink
    for link_title in wikilinks:
        # For now, we create placeholder target nodes without filepath
        # In a real implementation, we'd resolve these to actual files
        target_node_id = _generate_id("", link_title)
        target_node = Node(
            id=target_node_id,
            title=link_title,
            filepath=""
        )
        
        # Create edge from source to target
        edge = Edge(
            src_id=source_node.id,
            dst_id=target_node_id,
            context_snippet=_find_context(clean_content, link_title)
        )
        
        nodes.append(target_node)
        edges.append(edge)
    
    return nodes, edges


def _find_context(content: str, link_title: str, context_length: int = 100) -> str:
    """
    Find surrounding context for a WikiLink.
    
    Args:
        content: The markdown content
        link_title: The title of the WikiLink
        context_length: The length of context snippet (characters)
        
    Returns:
        Context snippet string
    """
    pattern = f"\\[\\[{re.escape(link_title)}\\]\\]"
    match = re.search(pattern, content)
    
    if match:
        start = max(0, match.start() - context_length // 2)
        end = min(len(content), match.end() + context_length // 2)
        context = content[start:end].strip()
        return context
    
    return ""
