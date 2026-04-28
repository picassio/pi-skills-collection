# CONTEXT.md Format

A living document that defines the domain language for the project. Referenced by architecture skills to name modules and seams using the project's own vocabulary.

## Structure

```md
# [Project Name] Context

## Domain Terms

### [Term]
[Definition — what this means in this project, not the general industry meaning]

### [Term]
[Definition]

## Bounded Contexts (if multi-context)

### [Context Name]
- **Owns**: [which domain terms this context is authoritative for]
- **Consumes**: [which terms it uses from other contexts]
```

## Guidelines

- Add terms as they emerge during architecture conversations
- Update definitions when they sharpen during grilling sessions
- Use these terms in all architecture discussions, issues, and ADRs
- One term per heading — no aliases in the heading (put aliases in the definition)
