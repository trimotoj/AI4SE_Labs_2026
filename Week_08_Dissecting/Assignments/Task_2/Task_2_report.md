# Task 2 – Custom Slash Command

## Coding Assistant

OpenAI Codex CLI 0.171.0

## Attempted Implementation

I created a custom prompt named `repo-summary.md` in `~/.codex/prompts/`.

The prompt contains instructions to analyze the current repository, summarize its structure and technologies, and suggest improvements.

The file includes the appropriate YAML front matter and was retained in the configuration.

## Compatibility Limitation

The custom command `/prompts:repo-summary` does not appear in the Codex CLI command menu, even after restarting Codex.

According to an OpenAI maintainer, support for custom prompts was removed starting with Codex CLI 0.117.0.

Therefore, the installed Codex CLI version (0.171.0) does not support registering custom commands using the legacy `/prompts:*` mechanism.

## Supported Alternatives

Codex supports **skills**, which provide reusable instructions stored in a `SKILL.md` file.

Skills can be invoked explicitly using their names and can also be made available automatically based on their descriptions.

The repository includes a custom `submission-audit` skill created in Task 5, demonstrating this alternative mechanism.

## Reference

https://github.com/openai/codex/issues/15941

## Conclusion

I attempted to implement a custom slash command, but the installed Codex CLI version no longer supports this feature.

The recommended alternative is to use Codex skills for reusable prompts and workflows.