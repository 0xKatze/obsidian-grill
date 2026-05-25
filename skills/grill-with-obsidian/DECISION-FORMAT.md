# Decision note format (Obsidian)

Decision notes (ADRs) live in `projects/<project>/decisions/` with sequential
numbering: `0001-slug.md`, `0002-slug.md`, … Create the folder lazily — only when
the first decision is worth recording.

The value is recording *that* a decision was made and *why* — and wiring it into
the vault so it surfaces later. Keep it short; lean on `[[wikilinks]]`.

## Template

```md
---
status: accepted        # proposed | accepted | deprecated | superseded by [[0007-slug]]
date: 2026-05-25
tags: [decision, <project>]
---

# {Short title of the decision}

{1–3 sentences: the context, what we decided, and why.}

Touches: [[order]], [[invoice]], [[0002-event-sourced-orders]]
```

That's it. A decision note can be a single paragraph. Link the glossary terms and
other notes it relates to with `[[wikilinks]]` so the vault graph connects it.

## Optional sections

Add only when they earn their place (most won't need them):

- **Considered options** — when the rejected alternatives are worth remembering.
- **Consequences** — when non-obvious downstream effects need calling out.
- **## Open Questions** — anything the grilling left unresolved (so `wiki-query`
  can find the gap later).

## Numbering

Scan `projects/<project>/decisions/` for the highest existing `NNNN` and add one.

## Frontmatter conventions

- `status` — track the lifecycle; use `superseded by [[NNNN-slug]]` when replaced.
- `date` — ISO date the decision was accepted.
- `tags` — include `decision`, the project tag, and any taxonomy tags the vault
  already uses (peek at `Tags/` or neighbouring notes).

## When to write a decision note

All three must be true (same bar as `grill-with-docs`):

1. **Hard to reverse** — changing your mind later is costly.
2. **Surprising without context** — a future reader will wonder "why this way?".
3. **The result of a real trade-off** — genuine alternatives, one chosen for reasons.

If a decision is easy to reverse, skip it. If it's not surprising, nobody will
wonder. If there was no real alternative, there's nothing to record.

### What qualifies

- **Architectural shape** (monorepo; event-sourced write model; …).
- **Integration patterns between contexts** (domain events vs synchronous HTTP).
- **Technology choices that carry lock-in** (DB, message bus, auth, deploy target).
- **Boundary / scope decisions** (who owns Customer data; explicit no-s).
- **Deliberate deviations from the obvious path** (manual SQL instead of an ORM, and why).
- **Constraints not visible in the code** (compliance, latency contracts).
- **Rejected alternatives when the rejection is non-obvious** (picked REST over
  GraphQL for subtle reasons — record it so it isn't re-litigated in six months).

## Link it back

After writing a decision note, link it from the project overview
(`projects/<project>/<project>.md`) and from any glossary terms it concerns, so
it's reachable in the Obsidian graph rather than orphaned.
