"""
Tests for the command line interface.

This module tests the command line interface of md2kg using click.testing.CliRunner.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from click.testing import CliRunner

from md2kg.cli import app


@pytest.fixture
def runner():
    """Provide a CliRunner for testing CLI commands."""
    return CliRunner()


@pytest.fixture
def sample_md_directory():
    """Create a temporary directory with sample markdown files."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Create some sample markdown files
    files = {
        "file1.md": """---
tags: test, sample
---
# Test File 1

This is a test file with a [[Link to File 2]].
""",
        "file2.md": """# Test File 2

This file links back to [[Test File 1]].
""",
        "subdir/file3.md": """# Test File 3

This links to both [[Test File 1]] and [[Test File 2]].
"""
    }
    
    # Write the files
    for filepath, content in files.items():
        # Create subdirectories if needed
        full_path = os.path.join(temp_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write file
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


def test_cli_help(runner):
    """Test the CLI help output."""
    result = runner.invoke(app, ['--help'])
    assert result.exit_code == 0
    assert 'Convert Markdown documents' in result.output
    assert 'parse' in result.output
    assert 'load' in result.output
    assert 'graph' in result.output


def test_parse_command_help(runner):
    """Test the parse command help output."""
    result = runner.invoke(app, ['parse', '--help'])
    assert result.exit_code == 0
    assert 'Parse Markdown files' in result.output
    assert '--output' in result.output
    assert '--include' in result.output
    assert '--exclude' in result.output


def test_parse_single_file(runner, sample_md_directory):
    """Test parsing a single markdown file."""
    with tempfile.TemporaryDirectory() as output_dir:
        result = runner.invoke(app, [
            'parse',
            os.path.join(sample_md_directory, 'file1.md'),
            '--output', output_dir
        ])
        
        assert result.exit_code == 0
        assert 'Parsing Markdown file' in result.output
        assert 'Exported nodes to' in result.output
        assert 'Exported edges to' in result.output
        
        # Check that output files exist
        assert os.path.exists(os.path.join(output_dir, 'nodes.csv'))
        assert os.path.exists(os.path.join(output_dir, 'edges.csv'))


def test_parse_directory(runner, sample_md_directory):
    """Test parsing a directory of markdown files."""
    with tempfile.TemporaryDirectory() as output_dir:
        result = runner.invoke(app, [
            'parse',
            sample_md_directory,
            '--output', output_dir
        ])
        
        assert result.exit_code == 0
        assert 'Parsing Markdown files in directory' in result.output
        assert 'Exported nodes to' in result.output
        assert 'Exported edges to' in result.output
        
        # Check that output files exist
        assert os.path.exists(os.path.join(output_dir, 'nodes.csv'))
        assert os.path.exists(os.path.join(output_dir, 'edges.csv'))


def test_parse_with_include_option(runner, sample_md_directory):
    """Test parsing with include pattern."""
    with tempfile.TemporaryDirectory() as output_dir:
        result = runner.invoke(app, [
            'parse',
            sample_md_directory,
            '--output', output_dir,
            '--include', '**/file[12].md'  # Only include file1.md and file2.md
        ])
        
        assert result.exit_code == 0
        
        # TODO: Add more specific assertions when include filtering is implemented
        assert os.path.exists(os.path.join(output_dir, 'nodes.csv'))
        assert os.path.exists(os.path.join(output_dir, 'edges.csv'))


# Additional tests for future implementation
def test_load_command_help(runner):
    """Test the load command help output."""
    result = runner.invoke(app, ['load', '--help'])
    assert result.exit_code == 0
    assert 'Load CSV files into a graph database' in result.output
    assert '--neo4j' in result.output
    assert '--duckpgq' in result.output


def test_graph_command_help(runner):
    """Test the graph command help output."""
    result = runner.invoke(app, ['graph', '--help'])
    assert result.exit_code == 0
    assert 'Create a graph from CSV files' in result.output
    assert '--format' in result.output
