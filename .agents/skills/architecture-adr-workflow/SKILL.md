---
name: architecture-adr-workflow
description: Guide interactive software architecture exploration from requirements through comparison of alternatives, user decisions, and iterative Architecture Decision Record (ADR) drafting or review. Use for architecture design discussions and ADR workflows.
---

# Architecture and ADR workflow

Help the user understand architectural options and document a reasoned choice. Apply only the requested phase: requirements analysis, exploration, decision support, ADR drafting, or review. Do not restart completed phases when reviewing an existing decision.

## Scope and checkpoints

- Read the supplied requirements and relevant existing artifacts. Establish the current phase, requested outputs, and writing permissions from the request; ask only about consequential gaps that cannot be inferred.
- Respect analysis-only requests. When writing is authorized, use the user's output locations or a project-appropriate directory; filenames and version conventions are configurable.
- In a full workflow, explore alternatives interactively, let the user formulate the decision, then proceed to ADR drafting within the authorized scope. A recommendation is not a user decision. If the user defers the choice, retain that uncertainty instead of inventing a decision.
- Pause at requested boundaries, after a substantive question needing the user's answer, and after delivering an ADR for requested review. Do not request approval for every routine editorial or reversible step already authorized.
- Final acceptance requires actual user approval. Distinguish approval of the architecture from approval of its written record. Do not implement the application as a side effect of design work.

## 1. Understand the requirements

Summarize functional areas and architecture-relevant constraints with references to their sources. Keep separate:

- confirmed requirements;
- working assumptions, including their origin;
- proposed design details;
- unresolved questions.

Missing workload, budget, availability targets, or team information is unknown, not evidence of small scale or a particular operating model. Clarify the uncertainty with the greatest architectural impact first. Use illustrative scenarios without turning them into requirements.

## 2. Explore alternatives

For a complete exploration, discuss at least three suitable, meaningfully different proposals. Choose them for the actual requirements rather than prescribing a fixed trio or preferred winner. Explain differences through deployment boundaries, execution, communication, data ownership, and failure behavior. If architectural styles overlap, disclose that overlap and show why the concrete proposals differ.

Explore one proposal at a time when working interactively. For each:

- Explain components, responsibilities, communication, state, and deployment.
- Walk through representative functions from the requirements and a relevant concurrency or failure scenario.
- Discuss benefits, costs, low-level implementation difficulties, and limits of mitigations. Cover consistency, resource contention, retries, or external dependencies where relevant, not as a mandatory catalog for every system.
- Compare against already explored proposals using the same project-derived criteria.
- Invite a focused question or ask the user to reason about a trade-off; allow disagreement and follow-up. Do not demand a quiz after every explanation or assume comprehension from silence.

Provide small diagrams or illustrative code when they clarify a difficult point. Label examples and hypothetical growth scenarios. Do not introduce a database, cloud, model provider, or distributed component merely because it appeared in an example.

## 3. Support the decision

Use a concise qualitative comparison tied to the agreed criteria. Explain which criteria matter most in this context and why; do not invent weights, benchmarks, workload measurements, or universal cost rankings.

Record the user's choice, reasoning, accepted disadvantages, conditions of validity, and unresolved details. Keep decisions made while evaluating an unselected option scoped to that option unless the user adopts them more broadly. Identify evidence that could justify reconsideration without promising a migration.

## 4. Draft and iterate the ADR

Base the draft on actual requirements and discussion. Use a compact structure appropriate to the project:

- identifier, title, decision date, document version and status;
- context, confirmed requirements, assumptions, and decision criteria;
- decision and scope, separating accepted points, proposed details, and open choices;
- alternatives evaluated against the same criteria and reasons for the choice;
- consequences, accepted risks, mitigations and their limits;
- future verification scenarios and reconsideration conditions;
- open questions and source links.

Include a small architecture diagram and comparison table when helpful. Make proposed versus accepted elements explicit, and keep the diagram consistent with the text. Suggest measurable indicators and concrete verification scenarios without claiming tests ran or inventing acceptance thresholds.

Present the draft for critical feedback on accuracy, omissions, excess detail, and structure. Revise from real feedback; do not manufacture iterations or presume satisfaction. Preserve prior versions according to the user's requested convention before replacing a draft. Record what changed and why. On actual approval, update acceptance metadata while preserving the approved content and decision date unless the user requests changes.

## Authentic records

When logging is authorized, establish the discussion record before substantive exploration. Keep concise chronological entries with stable turn or entry identifiers so later review can distinguish actual user feedback, decisions, and revisions.

For each substantive exchange, capture the topic, actual user question or feedback, explanation, trade-off, decision if any, and pending issue. Do not copy every repeated explanation. Never prewrite user answers, approvals, completed checks, or future interactions. Clearly separate supplemental assistant notes from discussed material; do not present those notes as user-endorsed conclusions. Append corrections and changed decisions transparently rather than rewriting history to appear more complete.

Record actual revision reasons and performed checks. This should support later counting of exchanges, correction requests, and iterations without generating an experimental score. Shorter output or fewer interactions does not establish better understanding or quality.

## Verification and independent reruns

- Check requirement and decision traceability, internal consistency, unnecessary repetition, relative links, and requested deliverables.
- Distinguish manual diagram inspection, parser validation, actual rendering, and visual review. Report only the checks performed and state unavailable checks explicitly.
- When running an independent repeat experiment, use the designated original requirements and this general workflow. Do not consult previous-run discussions, ADRs, or solutions as design input, and do not link to them from this skill. Keep new outputs separate; compare records only after the independent run is finished and comparison is requested.
- Report observable differences with consistent counting definitions. Do not invent elapsed time or causal speedups; acknowledge learning effects and differences in scope, tools, or conditions.
- Close with actual results and remaining limitations. Leave an unreviewed draft unaccepted, and do not start an experiment or comparison report merely because the skill was created or loaded.
