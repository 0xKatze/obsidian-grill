# cocoindex — the incremental index layer

obsidian-grill curates the vault (grill + agents + lint). This folder adds the
**index layer**: keep a semantic view of the vault that stays fresh as notes
change, and use it to surface the **coverage / linking gaps** (P2) — *related but
unlinked* notes and *near-duplicate* notes (terminology / redundancy drift).

Two implementations, same goal:

## 1. `index_vault.py` — production / incremental (CocoIndex)

Walks the vault Markdown → `RecursiveSplitter` chunks → `SentenceTransformerEmbedder`
→ **LanceDB** (file-based, no server). With CocoIndex's memoization, editing a note
only re-embeds that note — the index never needs a full rebuild.

```bash
pip install "cocoindex>=1.0.0" sentence-transformers lancedb
export COCOINDEX_DB=~/.obsidian-grill/cocoindex-state   # CocoIndex incremental-state store
cocoindex update cocoindex/index_vault.py        # build / incremental
cocoindex update cocoindex/index_vault.py -L     # live: watch the vault
python cocoindex/search_vault.py "why does attention pooling resist injection"  # query
```

> Verified end-to-end on cocoindex 1.0.6 + lancedb 0.30.2 + sentence-transformers
> 5.5.1: 238 notes → 1330 chunks indexed in ~14s (GPU); semantic search returns
> the right notes (e.g. the attention-pooling query surfaces `concepts/Attention
> Pooling Attack`).

Vector store lands at `$OBSIDIAN_LANCEDB` (default `~/.obsidian-grill/lancedb`).
Query it for true semantic search (upgrades `wiki-query` from grep to vectors).

## 2. `related_unlinked.py` — runs now (scikit-learn, no model/DB)

The lightweight stand-in: TF-IDF cosine over note bodies, cross-referenced with
the `[[wikilink]]` graph. No heavy install.

```bash
python cocoindex/related_unlinked.py --vault /workspace/obsidian-vault \
    --min-sim 0.30 --dup-sim 0.55 --top 30
```

Outputs:
- **Near-duplicate notes** (cosine ≥ `--dup-sim`) → possible redundancy or the
  same concept under two names (feeds the consistency pass).
- **Related but UNLINKED** (cosine ≥ `--min-sim`, no wikilink either way) →
  concrete `[[wikilink]]` suggestions (feeds the coverage pass / fixes orphans).

## Where this fits the loop

`index_vault.py` / `related_unlinked.py` produce **candidates**; the
[analyzer agents](../docs/AGENTS.md) and the human-in-the-loop
[grill-with-obsidian](../skills/grill-with-obsidian/) decide and commit. The
index is the fast substrate; obsidian-grill is the judgement on top.
