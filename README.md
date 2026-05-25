# obsidian-grill

**A framework for turning an Obsidian vault into a living, tested knowledge base.**

Knowledge isn't dumped once and left to rot. obsidian-grill runs a flywheel:
**grill** new understanding in (human-in-the-loop), **test** the vault with
deterministic checks, **analyse** it with read-only agents, then **iterate** —
each turn the vault gets sharper, less contradictory, and more in sync with
reality.

```
   ① GRILL ──▶ ② TEST ──▶ ③ ANALYSE ──▶ ④ ITERATE ──▶ (back to ①)
   skill        scripts     agents        agenda
```

See [docs/ITERATION-LOOP.md](docs/ITERATION-LOOP.md) for the full cycle.

## What's inside

```
skills/grill-with-obsidian/   the human-in-the-loop grilling skill (capture)
  SKILL.md, GLOSSARY-FORMAT.md, DECISION-FORMAT.md
agents/                       read-only analyzer sub-agents (Claude Code format)
  consistency-reviewer.md  coverage-gap-analyst.md
  freshness-auditor.md     perspective-panel.md
scripts/                      deterministic KB "unit tests"
  vault_lint.py   broken [[links]], orphans, frontmatter, dup names (non-zero exit on issues)
  vault_stats.py  coverage %, index drift, staleness, tag taxonomy
  kb_report.py    runs both → meta/kb-report-<date>.md
docs/                         ITERATION-LOOP.md, AGENTS.md
.claude-plugin/               marketplace.json + plugin.json (install as a plugin)
```

## How it combines existing skills

obsidian-grill packages and connects three skills into one loop:

- **`grill-with-docs`** (mattpocock, MIT) — the relentless one-question-at-a-time
  grilling methodology, glossary discipline, and ADR criteria. Adapted here.
- **`wiki-query`** — how the grilling reads the vault for domain awareness.
- **`wiki-update`** — how crystallised knowledge is written back into the vault.

The grilling skill is the *capture* door; the scripts and agents are the *test*
and *analysis* that decide what the next capture should focus on.

## Install

**Vault config.** All tooling resolves the vault from `~/.obsidian-wiki/config`
(`OBSIDIAN_VAULT_PATH`), or `$OBSIDIAN_VAULT_PATH`, or `--vault PATH`. Works with
any Obsidian vault — nothing is hard-coded.

**As a plugin (skill + agents):**
```bash
/plugin marketplace add 0xKatze/obsidian-grill
/plugin install obsidian-grill
```

**Manual:**
```bash
git clone https://github.com/0xKatze/obsidian-grill
cp -r obsidian-grill/skills/grill-with-obsidian ~/.claude/skills/
cp obsidian-grill/agents/*.md ~/.claude/agents/
```

## Usage

```bash
# ② TEST — health of the vault right now
python scripts/vault_lint.py
python scripts/vault_stats.py
python scripts/kb_report.py            # writes a dated report into <vault>/meta/

# ① GRILL — capture (in Claude Code)
#   "use grill-with-obsidian to stress-test this plan"

# ③ ANALYSE — dispatch the agents (see docs/AGENTS.md), in parallel, read-only
```

Requirements: Python 3.9+ (standard library only). The grilling skill and agents
run inside Claude Code (or any agent that supports SKILL.md / sub-agents).

## License

MIT — see [LICENSE](LICENSE). Bundles/adapts `grill-with-docs` (mattpocock, MIT).
