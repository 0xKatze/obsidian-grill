# Analyzer agents

The "Analyse" stage of the [iteration loop](./ITERATION-LOOP.md) uses four
read-only sub-agents. Each is a Claude Code subagent definition in `../agents/`
(frontmatter `name` / `description` / `tools` / `model`). They **propose** —
never edit the vault; the human-in-the-loop grilling commits.

| Agent | Finds | Feeds |
|---|---|---|
| `consistency-reviewer` | contradictions, terminology drift, glossary↔code conflicts | terms to canonicalise |
| `coverage-gap-analyst` | undefined concepts, decisions w/o rationale, Open-Question pile-up | gaps to fill |
| `freshness-auditor` | stale/wrong notes, superseded decisions, index drift | what to refresh |
| `perspective-panel` | factual / senior-eng / security / redundancy critique | blockers before commit |

## Install

```bash
# project-scoped
mkdir -p .claude/agents && cp agents/*.md .claude/agents/
# or user-scoped (available everywhere)
mkdir -p ~/.claude/agents && cp agents/*.md ~/.claude/agents/
```
Or install the whole framework as a plugin (see the repo README), which registers
the skill and agents together.

## Dispatch

Run them in parallel over the vault (they share no state), then merge the agenda:

> "Dispatch consistency-reviewer, coverage-gap-analyst, freshness-auditor and
> perspective-panel over the vault. Each returns findings + a next-grill agenda.
> Then consolidate into one prioritised agenda for the next grill-with-obsidian
> round."

Give each agent the vault path (or rely on `~/.obsidian-wiki/config`) and, if you
ran it, the path to `meta/kb-report-<date>.md` so they build on the deterministic
pass instead of repeating it.

## Why read-only

Knowledge enters the vault through **one** door — the human-in-the-loop grilling —
so every committed term and decision has been judged, not auto-written. Agents
widen the funnel of *candidates*; they don't get commit rights.
