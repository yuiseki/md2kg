"""
md2kg - Convert Markdown documents with WikiLinks to Knowledge Graph.

This package provides tools to extract knowledge graph from Markdown documents
with WikiLinks notation and export it to various formats.
"""

from md2kg.models import Node, Edge
from md2kg.parser import parse_markdown
from md2kg.builder import GraphBuilder
from md2kg.exporter import CsvExporter

__version__ = "0.1.0"
