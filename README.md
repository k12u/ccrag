# Claude Code Log Search CLI

This repository contains a command-line tool that indexes and searches Claude Code session logs using a retrieval-augmented generation (RAG) workflow backed by Chroma and Claude embeddings.

## Features

- Automatically resolves the Claude Code log directory for the current project.
- Parses JSONL session summaries and builds a persistent Chroma index per project.
- Uses Claude embedding vectors (via the `anthropic` Python SDK) for semantic similarity search.
- Provides a simple CLI to query the index and display matching `leafUuid` identifiers.

## Installation

### Requirements

- Python 3.10+
- A shell environment where `~/.local/bin` (or your user-level bin directory) is on `PATH`

All runtime dependencies are declared in the Python package metadata, so the standard Python packaging workflow will install them automatically.

### Installing the CLI for the current user

From a checkout of this repository, install the package in user mode:

```bash
python -m pip install --user .
```

The installer creates a `search-logs` executable in your user-level bin directory (typically `~/.local/bin`). Ensure that directory is present on your shell `PATH`—if necessary, add the following line to your shell profile (e.g. `~/.bashrc`, `~/.zshrc`):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

After reloading your shell configuration, the `search-logs` command can be run from any project directory.

### Alternative: pipx

If you prefer isolation, [`pipx`](https://pypa.github.io/pipx/) can manage a dedicated virtual environment for the CLI:

```bash
pipx install .
```

This produces the same `search-logs` command without modifying your base Python environment.

## Usage

Once the command is on your `PATH`, change into the project whose logs you want to search and execute:

```bash
search-logs "network debugging"
```

You can also invoke the module directly with Python when working from the repository checkout:

```bash
python -m search_logs "network debugging"
```

### Options

```
usage: search-logs [-h] [--project-path PROJECT_PATH] [--top-k TOP_K]
                   [--show-summary] [--show-distance] [--force-reindex]
                   query
```

- `--project-path`: Override the project root (defaults to the current working directory).
- `--top-k`: Number of results to return (default: 5).
- `--show-summary`: Include the stored session summary text in the output.
- `--show-distance`: Display the vector distance for each result returned by Chroma.
- `--force-reindex`: Rebuild the index even if the cache appears up to date.

The tool stores per-project indices under `~/.claude/rag-index/` and automatically refreshes them when the source logs change.
