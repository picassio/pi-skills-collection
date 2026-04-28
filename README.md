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

### DSPy (3.2.x)

| Skill | Description |
|-------|-------------|
| **dspy-fundamentals** | Typed Signatures, Modules, Predict/ChainOfThought/ReAct/ProgramOfThought, save/load. |
| **dspy-evaluation-harness** | Rich-feedback metrics, dspy.Evaluate, dev/val splits, CI-ready eval suites. |
| **dspy-gepa-optimizer** | Optimize DSPy programs with dspy.GEPA — reflective/evolutionary Pareto optimizer. |
| **dspy-rlm-module** | Recursive Language Model for >100k token contexts via sandboxed Python REPL. |
| **dspy-advanced-workflow** | End-to-end pipeline: spec → program → metric → baseline → GEPA → export → deploy. |

### UI/UX & Design

| Skill | Description |
|-------|-------------|
| **ui-ux-pro-max** | Master design intelligence — 50+ styles, 161 palettes, 57 font pairings, 99 UX guidelines, searchable CSV databases. |
| **design** | Logo, CIP, icon, social photos, banner generation with Gemini AI. |
| **design-system** | Token architecture (primitive→semantic→component), component specs, slide generation. |
| **ui-styling** | shadcn/ui + Tailwind CSS + canvas-based visual designs. |
| **brand** | Brand voice, visual identity, messaging frameworks, asset management. |
| **slides** | Strategic HTML presentations with Chart.js and design tokens. |
| **banner-design** | Multi-platform banner design for social, ads, web, and print. |

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

Original skills by [Matt Pocock](https://github.com/mattpocock/skills), [intertwine/dspy-agent-skills](https://github.com/intertwine/dspy-agent-skills), [ksimback/tech-debt-skill](https://github.com/ksimback/tech-debt-skill), [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills), and [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill). See original repos for licenses.
