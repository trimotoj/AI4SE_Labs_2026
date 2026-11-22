---
name: submission-audit
description: Review an AI4SE coursework task for submission readiness. Use when checking assignment deliverables, evidence, and compliance with task requirements. Do not use to implement assignments.
---

# Submission Audit

Review a coursework assignment against its original specification.

## Workflow

1. Identify the assignment directory.
2. Read the original assignment specification.
3. Inspect the existing deliverables in the task directory.
4. Compare the deliverables with every requirement.
5. Check whether required reports, screenshots, and configuration files are present.
6. Identify missing evidence and unverified requirements.
7. Provide a concise readiness report.

## Output

Report the following:

- Assignment name.
- Requirements satisfied.
- Missing or incomplete deliverables.
- Requirements that could not be verified.
- Final status: READY, INCOMPLETE, or UNVERIFIED.

## Constraints

- Do not modify any files.
- Do not invent test results or claim that unverified actions succeeded.
- Do not expose API keys, credentials, or other sensitive information.
- Report uncertainty explicitly.