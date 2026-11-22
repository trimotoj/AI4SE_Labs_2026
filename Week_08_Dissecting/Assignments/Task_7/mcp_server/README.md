# Text Tools MCP Server

A simple local MCP server implemented in Python using the official Model Context Protocol SDK.

## Functionality

The server exposes one tool:

**`count_words(text: str) -> int`**

It counts whitespace-separated words in the supplied text.

Example:

Input: `Artificial intelligence improves software development.`

Output: `5`

## Requirements

- Python 3.11 or newer
- OpenAI Codex CLI
- MCP Python SDK 2.3.0

## Installation

Run these commands from the `mcp_server` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Registering with Codex

While inside the `mcp_server` directory, run:

```bash
codex mcp add text-tools -- "$(pwd)/.venv/bin/python" "$(pwd)/server.py"
```

Verify the registration:

```bash
codex mcp list
```

Start a new Codex session and use `/mcp` to inspect the available tools.

## Testing

Ask Codex:

> Use the `count_words` tool from the `text-tools` MCP server to count the words in "Artificial intelligence improves software development." Do not calculate the result manually.

Expected result: `5`.

## Implementation

- `server.py` implements the MCP server and its tool.
- `requirements.txt` specifies the Python dependency.
- The server communicates with Codex through the standard input/output (stdio) transport.
- No API keys or external services are required.

## Notes

The virtual environment `.venv/` is local and should not be committed to Git.

The MCP server configuration is stored separately in the user's Codex configuration.