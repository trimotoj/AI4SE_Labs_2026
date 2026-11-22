<!-- TASK8_RULE_APPLIED -->

# Task 8 – Rule Verification

## Coding Assistant

OpenAI Codex CLI 0.171.0

## Rule

A repository-specific rule was defined in `Week_08_Dissecting/Assignments/Task_8/AGENTS.md`.

It requires Codex to insert the following HTML comment as the first line of every newly created Markdown document in the Task 8 directory:

`<!-- TASK8_RULE_APPLIED -->`

The rule should be applied automatically, without explicitly requesting the marker in the user prompt.

## Original User Prompt

```text
Create a new Markdown file named rule_test.md
in the current directory.

The file should contain:

- A heading: Rule Test
- One sentence: This file tests repository guidance.

Do not modify any other files.
```

## Codex Response

Before creating the file, Codex stated:

> I'll read the Task 8 specification, then create `rule_test.md` to test the repository guidance.

The recorded activity included:

```text
• Explored
  └ Read Task_8.md
• Ran (set -o noclobber; printf '%s\n' '<!-- TASK8_RULE_APPLIED -->' '# Rule Test' ...)
```

Codex then reported:

> Created rule_test.md with the required first-line marker, the heading “Rule Test,” and the sentence “This file tests repository guidance.”

## Verification

The file was inspected using:

```bash
cat rule_test.md
```

Actual output:

```text
<!-- TASK8_RULE_APPLIED -->
# Rule Test

This file tests repository guidance.
```

## Conclusion

The experiment successfully demonstrated that Codex followed a repository-specific instruction from `AGENTS.md`.

Although the user prompt did not request the special marker, Codex automatically included it as the first line of the generated Markdown file.

The rule was therefore successfully applied and verified.