# Task 7 – MCP Server Test

## Environment

- Operating system: Ubuntu 26.04.1 LTS
- Python: 3.14.4
- MCP SDK: 2.3.0
- Coding assistant: OpenAI Codex CLI 0.171.0

## 1. Python Verification

The server passed Python syntax validation:

```bash
python -m py_compile server.py
```

The `count_words` function was tested directly:

```bash
python -c "from server import count_words; print(count_words('Artificial intelligence improves software development.'))"
```

Actual result:

```text
5
```

## 2. MCP Registration

The server was registered using `codex mcp add text-tools`.

The `codex mcp get text-tools` command confirmed:

- Server name: `text-tools`
- Status: enabled
- Transport: stdio
- Command: Python interpreter from the project's virtual environment
- Argument: path to `server.py`

## 3. Actual MCP Tool Invocation

The following request was submitted to Codex:

> Use the count_words tool provided by the text-tools MCP server to count the words in "Artificial intelligence improves software development."
>
> You MUST invoke the actual MCP tool. Do not count the words yourself. Report the tool name, input, and returned result.

Codex reported the following tool invocation:

```text
• Called text-tools.count_words
  └ 5
```

Final response:

```text
MCP tool: mcp__text_tools__count_words
Input: Artificial intelligence improves software development.
Returned result: 5
```

## 4. Conclusion

The custom MCP server was successfully registered and tested with OpenAI Codex.

Codex invoked the actual MCP tool and received the correct result.

The experiment confirms that the locally implemented Python tool is accessible to Codex through the MCP protocol.