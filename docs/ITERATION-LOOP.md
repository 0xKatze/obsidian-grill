# The iteration loop

obsidian-grill turns an Obsidian vault into a **living, tested knowledge base**.
Knowledge isn't dumped once — it's grilled in, tested, analysed, and sharpened on
every pass. One turn of the flywheel:

```
        ┌──────────────────────────────────────────────┐
        │                                              ▼
   ① GRILL ───────▶ ② TEST ───────▶ ③ ANALYSE ───────▶ ④ ITERATE
   (human-in-loop)   (scripts)        (agents)          (agenda)
        ▲                                              │
        └──────────────────────────────────────────────┘
```

## ① Grill — capture (human-in-the-loop)
Run the **`grill-with-obsidian`** skill. It interviews you one question at a time,
grounds each question in what the vault already says (wiki-query style), and
writes crystallised results into `projects/<project>/`:
- glossary terms → `glossary.md`
- decisions → `decisions/NNNN-slug.md`
- unresolved threads → an **## Open Questions** section

## ② Test — deterministic checks (scripts)
Cheap, repeatable, objective. Run:
```bash
python scripts/vault_lint.py    # broken [[links]], orphans, frontmatter, dup names → non-zero exit on issues
python scripts/vault_stats.py   # coverage %, index drift, staleness, tag taxonomy
python scripts/kb_report.py     # writes meta/kb-report-<date>.md (lint + stats)
```
These are the KB's unit tests. Gate them in CI or a `loop` if you want continuous health.

## ③ Analyse — semantic pass (agents)
Dispatch the analyzer agents (see [AGENTS.md](./AGENTS.md)) — ideally **in
parallel** — over the vault. They read the report from ② and the notes, and
return findings + a next-round agenda:
- `consistency-reviewer` — contradictions, terminology drift
- `coverage-gap-analyst` — undefined concepts, decisions without rationale, gaps
- `freshness-auditor` — stale notes, superseded decisions, index drift
- `perspective-panel` — factual / senior-eng / security / redundancy critique

Agents **propose**; they never edit the vault.

## ④ Iterate — feed the next grill
Collect the agenda items (lint failures + agent findings + accumulated Open
Questions) and bring them into the next **Grill**. Each turn the vault gets:
- fewer broken links and orphans,
- tighter, less-contradictory terminology,
- decisions that record their *why*,
- an index that matches reality.

## Running it continuously
- Manually: do a turn whenever a project's understanding shifts.
- Semi-automated: `/loop` the **Test** stage to keep a health report fresh, and
  schedule the **Analyse** agents; review their agenda, then grill.
- The only stage that *must* stay human-in-the-loop is **Grill** — committing
  knowledge requires your judgement. Tests and analysis are safe to automate.
