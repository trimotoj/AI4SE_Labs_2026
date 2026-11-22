# Task 1 – System Instructions Configuration

## Coding Assistant

OpenAI Codex CLI 0.171.0

## 1. Initial Configuration Change

I initially added the following setting to `~/.codex/config.toml`:

```toml
developer_instructions = "Before modifying files, briefly explain what you intend to change and why."
```

This instruction was successfully tested. Codex explained its intended file modification before performing it.

Evidence: `config_screenshot.png`

However, `developer_instructions` adds developer-level guidance rather than replacing Codex's built-in model instructions.

## 2. Custom Model Instructions

To demonstrate a more direct modification of the model instructions, I created:

`custom_model_instructions.md`

The file contains custom guidance for repository work, file modifications, and safety.

I also created a separate Codex configuration profile:

`~/.codex/task1-system.config.toml`

The profile sets `model_instructions_file` to the absolute path of `custom_model_instructions.md`.

This setting allows Codex to use a custom file in place of its built-in model instructions. It does not override higher-priority safety constraints.

Evidence: `model_instructions_screenshot.png`

## 3. Verification

I launched Codex using:

```bash
codex --profile task1-system
```

I submitted the following prompt:

> Briefly introduce yourself and explain how you approach modifying files in a repository.
>
> Do not modify any files.

Codex began its response with:

```text
[TASK1-CUSTOM-INSTRUCTIONS]
```

This marker was explicitly required by the custom instructions.

Codex also explained that it would read repository guidance, describe intended changes before editing, and avoid modifications unless requested.

No files were modified during the test.

## 4. Conclusion

Both configuration changes were successfully tested.

The first experiment demonstrated additional developer instructions through `developer_instructions`.

The second demonstrated custom model instructions through `model_instructions_file`.

The original configuration changes and the custom profile have been retained.