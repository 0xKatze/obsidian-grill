# Glossary note format (Obsidian)

The project glossary lives at `projects/<project>/glossary.md`. It is the vault's
canonical language for this project — a **glossary only**, never a spec or a place
for implementation details.

## Structure

```md
---
tags: [glossary, <project>]
---

# {Project} — Glossary

{One or two sentences: what this project's context is and why it exists.}

## Language

**Order**:
A confirmed request from a [[customer]] to buy goods. One Order has many line items.
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a [[customer]] after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places [[order|Orders]].
_Avoid_: Client, buyer, account

## Flagged ambiguities

- **account** — used for both [[customer]] and login [[user]]. Resolved: use
  **Customer** for the buyer, **User** for the login identity.

## Example dialogue

> **Dev:** Can a Customer have two Orders open at once?
> **Domain expert:** Yes — each Order is independent; an Invoice is raised per Order.
```

## Rules

- **Be opinionated.** When several words mean the same thing, pick the best and
  list the rest under `_Avoid_`.
- **Link, don't repeat.** Reference other terms and existing vault notes with
  `[[wikilinks]]`. If a term already has its own note in the vault, link to it
  rather than redefining it.
- **Keep definitions tight.** One or two sentences. Define what it *is*, not what
  it *does*.
- **Show relationships.** Bold term names; express cardinality where obvious.
- **Only project-specific terms.** General programming concepts (timeouts, error
  types, utility patterns) don't belong. Ask: is this unique to this context, or
  general? Only the former.
- **Group under subheadings** when natural clusters emerge; a flat list is fine
  for a single cohesive area.
- **Frontmatter `tags`** must fit the vault's existing taxonomy (check `Tags/` or
  neighbouring notes). Always include `glossary` and the project tag.
- **Write the example dialogue** — a short dev ↔ domain-expert exchange that shows
  the terms interacting and clarifies boundaries.

## Atomic-note option

If the vault already keeps one note per concept (zettelkasten style), you may
instead create/extend an atomic note per term under `projects/<project>/concepts/`
(or link to an existing vault concept note) and keep `glossary.md` as an index of
`[[wikilinks]]`. Match whatever the surrounding vault already does.
