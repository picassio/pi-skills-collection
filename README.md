# Pi Skills Collection

Agent skills for real engineering workflows. Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) for the [pi coding agent](https://github.com/mariozechner/coding-agent).

## Installation

Copy any skill folder into `~/.pi/agent/skills/`:

```bash
cp -r grill-me ~/.pi/agent/skills/
```

Or symlink for easy updates:

```bash
ln -s $(pwd)/tdd ~/.pi/agent/skills/tdd
```

## Skills

### Planning & Design

| Skill | Description |
|-------|-------------|
| **grill-me** | Get relentlessly interviewed about a plan or design until every branch of the decision tree is resolved. |
| **design-an-interface** | Generate multiple radically different interface designs for a module using parallel sub-agents. Based on "Design It Twice" from Ousterhout. |

### Development

| Skill | Description |
|-------|-------------|
| **tdd** | Test-driven development with red-green-refactor loop. Vertical slices, integration-style tests, deep module design. |
| **qa** | Interactive QA session — describe bugs conversationally, agent files GitHub issues with proper domain language. |
| **improve-codebase-architecture** | Find deepening opportunities — refactors that turn shallow modules into deep ones. Informed by CONTEXT.md and ADRs. |

### Meta

| Skill | Description |
|-------|-------------|
| **write-a-skill** | Create new agent skills with proper structure, progressive disclosure, and bundled resources. |
| **caveman** | Ultra-compressed communication mode. Cuts token usage ~75% by dropping filler while keeping full technical accuracy. |

## Adaptations from Original

- Replaced Claude Code-specific `Agent tool` / `subagent_type=Explore` references with pi's `subagent` tool and `bash`/`read` for codebase exploration
- Replaced `Task tool` references with pi's `subagent` parallel mode
- Preserved all domain-model references (`CONTEXT.md`, `docs/adr/`, `UBIQUITOUS_LANGUAGE.md`)
- All supporting reference files (LANGUAGE.md, DEEPENING.md, etc.) included alongside SKILL.md

## License

Original skills by [Matt Pocock](https://github.com/mattpocock/skills). See original repo for license.
