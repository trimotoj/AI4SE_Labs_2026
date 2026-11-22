# Task 9 – Codex Configuration Export

## 1. Coding Assistant

**Assistant:** OpenAI Codex CLI 0.171.0 with the VS Code extension

**Operating system:** Ubuntu 26.04.1 LTS

## 2. Exported Configuration Files

| File | Purpose |
|---|---|
| `config.redacted.toml` | Main Codex configuration, including developer instructions and MCP server settings |
| `deep-review.config.toml` | Custom read-only profile created in Task 4 |
| `task1-system.config.toml` | Custom model instructions profile created in Task 1 |
| `repo-summary.md` | Legacy custom prompt attempted in Task 2 |

Additional repository-level instructions and skills are preserved at their original locations:

- `../../../AGENTS.md`
- `../../AGENTS.md`
- `../../../.agents/skills/submission-audit/SKILL.md`

The custom instructions referenced by the Task 1 profile are stored in:

- `../Task_1/custom_model_instructions.md`

## 3. Configuration Changes

### Task 1 – Model Instructions

Two approaches were tested.

**Developer instructions**

The main `config.toml` contains:

```toml
developer_instructions = "Before modifying files, briefly explain what you intend to change and why."
```

Codex successfully followed this instruction before creating a test file.

**Custom model instructions**

A separate configuration profile, `task1-system.config.toml`, uses the `model_instructions_file` setting to reference a custom Markdown instruction file.

The profile was activated using:

```bash
codex --profile task1-system
```

The test succeeded: Codex started its response with the marker `[TASK1-CUSTOM-INSTRUCTIONS]`, as required by the custom file.

Both configurations were retained.

### Task 2 – Custom Slash Command

A reusable prompt was created at:

`~/.codex/prompts/repo-summary.md`

The attempted command was:

`/prompts:repo-summary`

However, the custom command did not appear in the command menu of Codex CLI 0.171.0.

The legacy custom prompts mechanism is no longer supported in this version.

A compatibility report was submitted as the alternative permitted by Task 2. Codex skills provide a supported mechanism for reusable instructions.

The original prompt file was retained as evidence of the attempted configuration.

### Task 4 – Configuration Profile

The `deep-review` profile was created with:

- High reasoning effort
- Read-only sandbox
- On-request approval policy

The profile was activated using:

```bash
codex --profile deep-review
```

Its configuration is preserved in `deep-review.config.toml`.

### Task 5 – Skills

The repository contains a custom `submission-audit` skill.

The skill was successfully loaded by Codex and used to conduct a final submission audit.

### Task 7 – MCP Server

A local MCP server named `text-tools` was registered using the stdio transport.

The server exposes the `count_words` tool.

Codex successfully invoked the tool and received the expected result of `5` for the test sentence.

## 4. Security and Redaction

The exported configuration files are copies of the original Codex configuration.

Absolute paths containing the local home directory were anonymized by replacing the home directory prefix with:

`/home/REDACTED_USER`

Authentication files, including `auth.json`, were not included.

The exported configurations retain the original settings but are not directly portable because the anonymized paths must be adjusted for another computer.

The original configuration files in `~/.codex/` remain unchanged.

## 5. Verification

The exported TOML files were checked using Python's `tomllib` parser.

| Check | Result |
|---|---|
| Main configuration syntax | PASS |
| Deep-review profile syntax | PASS |
| Task 1 profile syntax | PASS |
| Main configuration matches the original after path redaction | PASS |
| Deep-review profile matches the original after path redaction | PASS |
| Task 1 profile matches the original after path redaction | PASS |
| Original home directory path absent from the three TOML exports | PASS |
| Legacy prompt matches the original file | PASS |

These checks establish the validity and consistency of the exported files. They do not replace a manual review for sensitive information.

## 6. Conclusion

The submitted configuration documents the settings used throughout the Week 08 assignments.

It includes developer instructions, custom model instructions, configuration profiles, an attempted legacy slash command, and a registered MCP server.

The report distinguishes between features that were successfully tested and the unsupported legacy slash-command mechanism.

The exported files preserve the configuration changes while anonymizing local home directory paths.