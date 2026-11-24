# Task 3 – AGENTS.md Creation Report

**Coding assistant:** OpenAI Codex (CLI 0.171.0 and VS Code extension)

## Creation process

I used two approaches to create the repository's `AGENTS.md` files.

**1. Built-in `/init` command**

I launched Codex CLI from the repository root and executed `/init`.

Codex analyzed the repository and generated a root-level `AGENTS.md` containing project structure, development and testing instructions, coding conventions, and Git workflow guidelines.

**2. Natural-language prompt**

I then asked Codex to review the root instructions for compatibility with Ubuntu and create a specialized `AGENTS.md` inside `Week_08_Dissecting/`.

The new file contains instructions specific to Week 08, including deliverable organization, configuration preservation, evidence collection, and protection of sensitive information.

## Result

Two instruction files were created:

- `AGENTS.md` – general repository guidelines.
- `Week_08_Dissecting/AGENTS.md` – instructions specific to Week 08.

Both files were reviewed for relevance to the repository and its assignments.

This experiment demonstrated that Codex supports both automatic initialization through `/init` and instruction-file creation through ordinary prompts.