# ADR Format

Architecture Decision Records — lightweight documents that capture decisions and their rationale so future explorers don't re-litigate settled questions.

## Template

```md
# ADR-NNNN: [Title]

## Status

[Proposed | Accepted | Superseded by ADR-NNNN | Deprecated]

## Context

[What forces are at play? What problem prompted this decision?]

## Decision

[What was decided, stated clearly and concisely]

## Consequences

[What follows from this decision — good, bad, and neutral]
```

## Guidelines

- Number sequentially: ADR-0001, ADR-0002, etc.
- Store in `docs/adr/` (or context-scoped `docs/adr/` directories)
- Keep each ADR to one decision
- Write when a user rejects an architecture suggestion with a load-bearing reason
- Don't write ADRs for ephemeral reasons ("not worth it right now") or self-evident ones
- Reference from CONTEXT.md when a decision affects domain term definitions
