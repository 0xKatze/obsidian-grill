---
name: grill-with-obsidian
description: Grilling session that stress-tests your plan against your Obsidian vault's established knowledge — terminology, prior decisions, and open questions — then writes crystallised glossary terms and decision notes back into the vault as linked Obsidian notes. Use when the user wants to challenge a plan against what their knowledge base already says, in the language of their vault, and capture the outcome in Obsidian. The vault is the source of truth and the destination; the codebase is cross-referenced too.
---

<what-to-do>

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing.

If a question can be answered by exploring the **Obsidian vault** or the **codebase**, explore them instead of asking.

</what-to-do>

<supporting-info>

This skill combines three installed skills:
- **`grill-with-docs`** (mattpocock) — the grilling methodology, glossary discipline, and ADR criteria. This skill adapts it.
- **`wiki-query`** — how to read/search the vault for domain awareness during the interview.
- **`wiki-update`** — how to write distilled knowledge back into the vault.

## Connect to the vault first

1. Read `~/.obsidian-wiki/config` to get `OBSIDIAN_VAULT_PATH` (the vault) and
   `OBSIDIAN_WIKI_REPO`. If the file doesn't exist, tell the user to run
   `bash setup.sh` from their obsidian-wiki repo, and stop.
2. Read `$OBSIDIAN_VAULT_PATH/index.md` (and `overview.md` if present) to learn
   the vault's scope and conventions.
3. Decide the **project scope**: derive a project name from the current working
   directory (as `wiki-update` does) and target `projects/<project-name>/`. If
   the topic doesn't map cleanly to an existing project, ask which project (or
   propose creating a new one).

## Domain awareness — from the vault (and the code)

Before asking a question, see whether the vault already answers it or whether
the plan contradicts what's recorded. Search like `wiki-query`:

- Glob `**/*.md` over `$OBSIDIAN_VAULT_PATH` for matching titles, then Grep content.
- Follow `[[wikilinks]]` from hits to related notes; check frontmatter `tags`.
- Read **"Open Questions"** sections — unresolved threads are prime grilling material.
- Look in `projects/<project>/` first (its `glossary.md`, `decisions/`, concepts),
  then the wider vault (`concepts/`, `entities/`).

Also cross-reference the **codebase** when the user states how something works.

## During the session

### Challenge against the vault's language
When a term conflicts with how the vault already defines it, call it out immediately:
"Your vault's glossary defines **cancellation** as X (see `[[cancellation]]`), but you
seem to mean Y — which is it?"

### Sharpen fuzzy language
When a term is vague or overloaded, propose a precise canonical term.
"You're saying 'account' — do you mean the **Customer** or the **User**? Those are
different things." Prefer terms already canonical in the vault.

### Discuss concrete scenarios
Invent specific scenarios that probe edge cases and force precise boundaries
between concepts.

### Cross-reference vault *and* code
If the vault, the code, and the user disagree, surface the contradiction:
"`[[order-cancellation]]` says orders cancel whole; your code cancels line items;
you just said partial — which is right?"

## Write to the vault inline (don't batch)

Capture decisions as they crystallise, in Obsidian-native form. All writes go
under `projects/<project-name>/`. Create files lazily — only when you have
something to write.

### Glossary terms → `projects/<project>/glossary.md`
When a term is resolved, update the project glossary right there. Use the format
in [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md): frontmatter `tags`, bold term
names, `[[wikilinks]]` to related notes, aliases to avoid. The glossary is a
**glossary only** — no implementation details, no spec, no scratch pad.
Cross-link terms to existing vault notes where they already exist.

### Decisions (ADRs) → `projects/<project>/decisions/NNNN-slug.md`
Offer a decision note only when **all three** are true:

1. **Hard to reverse** — changing your mind later is costly.
2. **Surprising without context** — a future reader will wonder "why this way?".
3. **The result of a real trade-off** — genuine alternatives, picked one for reasons.

If any is missing, skip it. Use the format in [DECISION-FORMAT.md](./DECISION-FORMAT.md):
frontmatter (`status`, `date`, `tags`), 1–3 sentences, `[[wikilinks]]` to the
terms and notes it touches. Number by scanning `projects/<project>/decisions/`
for the highest existing `NNNN` and incrementing.

### Unresolved threads → "Open Questions"
When a grilling branch can't be settled now, record it under an **## Open
Questions** section in the relevant note (glossary, decision, or the project
overview). This keeps the gap visible and lets `wiki-query` surface it later.

## Keep the vault tidy

- Use `[[wikilinks]]`, not bare text, when referencing other notes/terms.
- Add frontmatter `tags` consistent with the vault's existing taxonomy (peek at
  `Tags/` or neighbouring notes).
- If `projects/<project>/<project>.md` (the project overview) exists, link new
  glossary/decision notes from it; if it doesn't and you've created notes, add a
  short overview that links them.
- Don't restructure the vault. Add notes; link them; leave the rest alone.

</supporting-info>
