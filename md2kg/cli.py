"""
Command line interface for md2kg.

This module provides the command line interface for the md2kg tool,
enabling users to parse Markdown files, export to various formats,
load into graph databases, and work with the generated graphs.
"""

import os
import sys
from typing import List, Optional
import click

from md2kg.builder import GraphBuilder
from md2kg.exporter import CsvExporter


@click.group()
@click.version_option()
def app():
    """Convert Markdown documents with WikiLinks to Knowledge Graph."""
    pass


@app.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output', '-o', 
              default='./kg_output',
              help='Directory to write output files. Will be created if it doesn\'t exist.')
@click.option('--include',
              default='**/*.md',
              help='Glob pattern to include files (default: "**/*.md").')
@click.option('--exclude',
              help='Glob pattern to exclude files.')
@click.option('--frontmatter-tags/--no-frontmatter-tags',
              default=True,
              help='Use tags from frontmatter as node labels (default: True).')
def parse(input_path: str, output: str, include: str, exclude: Optional[str], frontmatter_tags: bool):
    """
    Parse Markdown files and create a knowledge graph.
    
    INPUT_PATH can be a single Markdown file or a directory containing Markdown files.
    """
    try:
        # Initialize the graph builder
        builder = GraphBuilder()
        
        # Process input path
        if os.path.isdir(input_path):
            click.echo(f"Parsing Markdown files in directory: {input_path}")
            # Process directory with include pattern
            builder.add_directory(input_path, pattern=include)
        else:
            click.echo(f"Parsing Markdown file: {input_path}")
            # Process single file
            builder.add_file(input_path)
        
        # Get the resulting graph
        nodes, edges = builder.get_graph()
        
        # Report node and edge counts
        click.echo(f"Found {len(nodes)} nodes and {len(edges)} edges")
        
        # Export to CSV
        exporter = CsvExporter()
        output_files = exporter.export(nodes, edges, output)
        
        # Report success
        click.echo(f"Exported nodes to {output_files['nodes_csv']}")
        click.echo(f"Exported edges to {output_files['edges_csv']}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@app.command()
@click.argument('input_directory', type=click.Path(exists=True, file_okay=False))
@click.option('--neo4j', 
              help='Neo4j connection URI (e.g., "bolt://localhost:7687").')
@click.option('--user', 
              help='Neo4j username.')
@click.option('--pass', 'password',
              help='Neo4j password.')
@click.option('--duckpgq',
              help='DuckDB database file to load data into.')
def load(input_directory: str, neo4j: Optional[str], user: Optional[str], 
         password: Optional[str], duckpgq: Optional[str]):
    """
    Load CSV files into a graph database (Neo4j or DuckDB PGQ).
    
    INPUT_DIRECTORY should contain nodes.csv and edges.csv files.
    """
    click.echo("The 'load' command is not yet implemented.")
    click.echo("This will load data into Neo4j or DuckDB in future versions.")
    sys.exit(1)


@app.command()
@click.argument('input_directory', type=click.Path(exists=True, file_okay=False))
@click.option('--format', '-f',
              type=click.Choice(['networkx', 'gml']),
              default='networkx',
              help='Output format (default: networkx).')
def graph(input_directory: str, format: str):
    """
    Create a graph from CSV files and optionally start an interactive Python session.
    
    INPUT_DIRECTORY should contain nodes.csv and edges.csv files.
    """
    click.echo("The 'graph' command is not yet implemented.")
    click.echo("This will create NetworkX graphs and start Python REPL in future versions.")
    sys.exit(1)


if __name__ == '__main__':
    app()
