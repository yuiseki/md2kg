# md2kg

Convert Markdown documents with WikiLinks to Knowledge Graph

## Overview

`md2kg` is a CLI tool that extracts explicit link structures created with WikiLinks (`[[Page Title]]`) from Markdown documents and converts them into a Knowledge Graph (KG) that can be used in various applications.

## Features

- Parse Markdown documents with WikiLinks
- Extract nodes and edges from link structures
- Output to `nodes.csv` / `edges.csv` with a common schema
- Support for Neo4j and DuckDB + PGQ extension (DuckPGQ)
- Convert to NetworkX GML format for use with LangChain

## Installation

```bash
pip install md2kg
```

## Usage

```bash
# Parse Markdown and generate CSV
md2kg parse docs/ --output kg_out/

# Load into Neo4j
md2kg load kg_out/ --neo4j bolt://localhost:7687 --user neo4j --pass ****

# Load into DuckDB + PGQ
md2kg load kg_out/ --duckpgq kg.duckdb

# Start NetworkX graph and Python REPL
md2kg graph kg_out/
```

## Requirements

- Python 3.10 or later

## Development

This project uses `uv` for dependency management.

### Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Synchronize dependencies
uv sync

# Activate virtual environment
. .venv/bin/activate
```

### Testing

```bash
# Run all tests with verbose output
python -m pytest -v
```

All test files follow the naming convention `{module_name}_test.py` (e.g., `parser_test.py`, `builder_test.py`). This naming convention is mandatory for the project.

## License

MIT
