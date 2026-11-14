# Bonus Task 1: Improved repository-aware code generation

## Evidence from the implemented pipeline

Tasks 2–5 implemented a deliberately simple baseline: AST-based Python chunks, metadata-aware embeddings, cosine-similarity retrieval of exactly five chunks, AST-extracted target context, and generation with `gpt-5-mini`. This pipeline ultimately generated all ten methods and, after one targeted repair, passed all 481 tests.

The experiment also exposed limits that a practical architecture should address:

- Test chunks dominated some top-five results, including both retrievals for `BulkDiscountPricing.price`.
- The first pricing generation lacked the `Money` dependency and invented `Money.amount`; the real API is `Money.cents`.
- AST-based target and dependency context made the targeted repair reliable without replacing the required retrieval step.
- A focused repair was safer and cheaper than regenerating all ten methods.
- `InventoryLedger.__contains__` revealed that passing tests can still conflict with a written specification.

The architecture below is a proposal. Hybrid indexes, dependency graphs, reranking, and automated feedback-driven regeneration were not implemented in Tasks 2–5.

## 1. Is embedding similarity the best retrieval strategy?

Embedding similarity is useful, but it is not sufficient on its own for source code. It finds conceptually related behavior even when identifiers differ, but it can miss exact API relationships and can over-rank repetitive tests. The pricing defect is direct evidence: semantically relevant tests occupied the result set while the defining `Money` class was absent.

A stronger system would use hybrid retrieval:

- lexical search, such as BM25 or identifier-aware matching, for exact class, method, attribute, exception, and import names;
- embedding search for behavioral and conceptual similarity;
- AST symbol resolution for the target definition, enclosing class, imports, overridden methods, and referenced types;
- a dependency graph for callers, callees, constructors, base classes, and data models;
- links between production symbols and their tests.

Candidates from these sources could be combined with reciprocal-rank fusion and then reranked using exact-symbol matches, graph distance, file locality, source/test category, and semantic relevance. Production code should not always outrank tests: tests are often the clearest behavioral evidence. However, category balancing or minimum source-context requirements would prevent an all-test result set when implementation APIs are needed.

The trade-off is additional indexing and maintenance complexity. Lexical and graph retrieval are inexpensive and deterministic; learned reranking can improve relevance but adds latency, cost, and another model-dependent failure point.

## 2. Would a different number of chunks be better?

There is no universally correct fixed number. Five chunks kept prompts small, but it was too rigid when all five represented the same evidence category. Simply increasing the number would sometimes include the missing dependency, but it would also add duplication, distract the model, and increase token cost.

An improved pipeline should retrieve a broader candidate pool, for example 20–50 inexpensive lexical and vector candidates, and then select context adaptively. Selection should reserve space for mandatory structural context and fill the remaining token budget with reranked, deduplicated evidence. Useful rules include:

- always include the target signature and enclosing class;
- include definitions of referenced repository types and methods;
- include at least one production definition and one focused test when both exist;
- collapse near-duplicate parameterized tests;
- stop adding chunks when their marginal relevance is low;
- allow more context for cross-module changes and less for local utility methods.

The effective result is a task-specific number of chunks rather than a global top-n. Token budget, evidence diversity, and dependency coverage matter more than count alone.

## 3. Should chunking be more sophisticated?

The AST-based chunks were a sound educational choice because they preserved complete functions, methods, classes, paths, symbols, and line ranges. A production system should enrich rather than abandon that approach.

Useful chunk types would include:

- complete symbol definitions with signatures, decorators, docstrings, and type annotations;
- compact class and module summaries for navigation;
- interface and data-model chunks describing public attributes and invariants;
- focused test scenarios linked to the production symbols they exercise;
- dependency-edge records for imports, calls, inheritance, construction, and attribute access;
- relevant configuration and documentation when they affect behavior.

Metadata should include qualified names, symbol kind, imports, referenced symbols, callers and callees, base classes, associated tests, source/test category, and a content hash. Oversized classes should be represented by a class summary plus individual methods, with limited shared class context. Oversized functions should be split only at statement or control-flow boundaries and retain a parent-symbol link.

This design improves precision and dependency coverage, but static analysis of Python is imperfect because imports, attributes, and dispatch can be dynamic. Tree-sitter or language-server indexes can broaden language support, while Python AST remains simpler and more precise for this repository.

## 4. Ideal practical pipeline

### Repository indexing

1. Detect languages and distinguish production code, tests, documentation, generated files, and configuration.
2. Parse source into symbols and build an incrementally updated symbol and dependency graph.
3. Produce semantic chunks and navigation summaries with stable IDs and content hashes.
4. Maintain lexical and vector indexes, caching unchanged records.

### Task understanding and context planning

1. Parse the requested file, symbol, expected behavior, referenced identifiers, and any stack trace.
2. Resolve the target and its dependencies through the symbol graph.
3. Treat the written specification, current implementation, tests, and observed runtime behavior as separate evidence sources.
4. Detect contradictions before generation. For example, the positive-stock requirement and zero-stock membership test should be reported for human resolution rather than silently optimized for either one.

### Hybrid retrieval and selection

1. Gather a broad candidate set through lexical, semantic, symbol, dependency, and test-link retrieval.
2. Expand one or two graph hops around the target only where references justify it.
3. Rerank and deduplicate candidates, with diversity constraints across production code and tests.
4. Assemble an adaptive prompt under a token budget, placing mandatory target and API definitions before optional examples.
5. Record why each context item was selected. Under this policy, `Money` and `FlatPricing.price` would have been mandatory dependencies for the pricing task even if tests dominated semantic ranking.

### Constrained generation and validation

1. Ask the model for a structured patch or method body, not a rewritten file.
2. Limit edits to authorized AST spans and preserve signatures, decorators, imports, and unrelated formatting.
3. Validate the response schema, parse the candidate source, and reject references to repository attributes or methods that cannot be resolved unless they are standard or intentionally introduced.
4. Run lightweight static checks before executing any generated code.
5. Save prompts, context IDs, model metadata, hashes, and reversible patches for provenance.

### Verification and controlled regeneration

1. Run syntax and static checks, then focused tests, followed by the complete suite.
2. Attribute failures to the changed symbol using stack traces and changed-line coverage where available.
3. Permit a small repair budget, such as one or two targeted calls, adding the failure details and newly verified dependencies to the prompt.
4. Roll back only the failed change if validation does not improve.
5. Require human review for specification/test conflicts, broad architectural changes, security-sensitive code, or exhausted repair budgets.

The successful targeted pricing repair illustrates this loop: preserve the nine working methods, add verified dependency context, regenerate one body, and validate focused and full suites.

## Trade-offs and limitations

The proposed system is more reliable but more complex than the assignment baseline. Symbol graphs, multiple indexes, reranking, and incremental invalidation require engineering effort. Broader retrieval and model-based reranking increase latency and cost. Static dependency analysis remains incomplete for dynamic Python, and test feedback can encourage overfitting if written requirements are not independently checked.

A practical implementation should therefore scale its effort with risk. Small local methods may need only target context, lexical retrieval, and a focused test. Cross-module or public-API changes justify graph expansion, reranking, and stricter review. The central improvement is not merely providing more text; it is selecting structurally justified, diverse evidence and preserving a controlled, reversible path from generation to verification.
