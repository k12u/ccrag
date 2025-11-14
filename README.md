# Claude Code Log Search CLI

This repository contains a command-line tool that indexes and searches Claude Code session logs using a retrieval-augmented generation (RAG) workflow backed by Chroma and Claude embeddings.

## Features

- Automatically resolves the Claude Code log directory for the current project.
- Parses JSONL session summaries and builds a persistent Chroma index per project.
- Uses Claude embedding vectors (via the `anthropic` Python SDK) for semantic similarity search.
- Provides a simple CLI to query the index and display matching `leafUuid` identifiers.

## Requirements

- Python 3.10+
- [`chromadb`](https://docs.trychroma.com/)
- [`anthropic`](https://docs.anthropic.com/claude/reference/getting-started-with-the-api) (requires an API key via `ANTHROPIC_API_KEY`)

Install the dependencies with:

```bash
pip install chromadb anthropic
```

## Usage

After cloning the repository, install the project in editable mode so the `search-logs` entrypoint is added to your `PATH`:

```bash
pip install -e .
```

You can then invoke the CLI from anywhere:

```bash
search-logs "network debugging"
```

Alternatively, you can run the module directly without installing it:

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
