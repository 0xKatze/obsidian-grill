#!/usr/bin/env python3
"""
related_unlinked.py — find semantically related notes that are NOT linked, and
near-duplicate notes, in an Obsidian vault. Runs *now* with scikit-learn (no
embedding model / DB install). It's the lightweight stand-in for the CocoIndex
semantic index (index_vault.py) and targets obsidian-grill's P2 coverage layer:
"related but unlinked" → missing [[wikilinks]]; "near-duplicate" → terminology /
redundancy drift.

Requirements: scikit-learn, numpy (already common). Read-only.

Usage:
    python cocoindex/related_unlinked.py [--vault PATH] [--min-sim 0.30] [--top 30]
"""
import argparse
import os
import pathlib
import re
import sys
from collections import defaultdict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")
FRONTMATTER = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.S)
MEDIA = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".excalidraw", ".canvas")


def resolve_vault(arg):
    if arg:
        return pathlib.Path(arg).expanduser()
    if os.environ.get("OBSIDIAN_VAULT_PATH"):
        return pathlib.Path(os.environ["OBSIDIAN_VAULT_PATH"])
    cfg = pathlib.Path.home() / ".obsidian-wiki" / "config"
    if cfg.exists():
        for line in cfg.read_text().splitlines():
            if line.startswith("OBSIDIAN_VAULT_PATH="):
                return pathlib.Path(line.split("=", 1)[1].strip().strip('"'))
    sys.exit("error: no vault path (--vault / $OBSIDIAN_VAULT_PATH / ~/.obsidian-wiki/config)")


def link_target(raw):
    t = raw.replace("\\|", "|").split("|", 1)[0].split("#", 1)[0]
    return t.strip().rstrip("\\")


def main():
    ap = argparse.ArgumentParser(description="Related-but-unlinked + near-duplicate notes.")
    ap.add_argument("--vault")
    ap.add_argument("--min-sim", type=float, default=0.30, help="min cosine to suggest a link")
    ap.add_argument("--dup-sim", type=float, default=0.55, help="cosine above this = near-duplicate")
    ap.add_argument("--top", type=int, default=30)
    ap.add_argument("--exclude", default="copilot,meta,Tags,.raw",
                    help="comma-separated top-level dirs to skip")
    args = ap.parse_args()

    vault = resolve_vault(args.vault)
    skip = tuple(x.strip() for x in args.exclude.split(",") if x.strip())

    notes = [p for p in vault.rglob("*.md")
             if p.is_file()
             and not any(part.startswith(".") for part in p.relative_to(vault).parts)
             and (not p.relative_to(vault).parts[:-1] or p.relative_to(vault).parts[0] not in skip)]

    rels, bodies, bases = [], [], []
    for p in notes:
        raw = p.read_text(encoding="utf-8", errors="ignore")
        body = FRONTMATTER.sub("", raw)
        rels.append(p.relative_to(vault).as_posix())
        bodies.append(body)
        bases.append(p.stem.lower())

    n = len(notes)
    if n < 2:
        sys.exit("need >= 2 notes")

    # ---- wikilink adjacency (undirected), case-insensitive by basename or relpath ----
    rel_lower = {r[:-3].lower(): i for i, r in enumerate(rels)}
    base_lower = defaultdict(list)
    for i, b in enumerate(bases):
        base_lower[b].append(i)
    linked = set()
    for i, raw in enumerate(bodies):
        for m in WIKILINK.finditer(raw):
            t = link_target(m.group(1)).lower()
            if not t or t.endswith(MEDIA):
                continue
            j = rel_lower.get(t) or rel_lower.get(t.removesuffix(".md"))
            cands = [j] if j is not None else base_lower.get(t.rsplit("/", 1)[-1].removesuffix(".md"), [])
            for k in cands:
                if k is not None and k != i:
                    linked.add((min(i, k), max(i, k)))

    # ---- TF-IDF cosine ----
    X = TfidfVectorizer(stop_words="english", max_df=0.5, min_df=2,
                        ngram_range=(1, 2), sublinear_tf=True).fit_transform(bodies)
    sim = linear_kernel(X, X)   # rows are L2-normalised by TfidfVectorizer → cosine

    pairs = []
    for i in range(n):
        row = sim[i]
        for j in np.where(row >= args.min_sim)[0]:
            if j <= i:
                continue
            pairs.append((float(row[j]), i, int(j)))
    pairs.sort(reverse=True)

    related_unlinked = [(s, i, j) for s, i, j in pairs if (i, j) not in linked and s < args.dup_sim]
    near_dupes = [(s, i, j) for s, i, j in pairs if s >= args.dup_sim]

    print(f"# related-but-unlinked + near-duplicates — {vault}")
    print(f"notes analysed: {n} | existing links: {len(linked)} | min-sim {args.min_sim}\n")

    print(f"## Near-duplicate notes (cosine >= {args.dup_sim}) — possible redundancy / terminology drift")
    if not near_dupes:
        print("  (none)")
    for s, i, j in near_dupes[:args.top]:
        tag = "LINKED" if (i, j) in linked else "UNLINKED"
        print(f"  {s:.2f} [{tag}] {rels[i]}  ≈  {rels[j]}")

    print(f"\n## Related but UNLINKED (suggest adding [[wikilinks]]) — top {args.top}")
    if not related_unlinked:
        print("  (none above threshold)")
    for s, i, j in related_unlinked[:args.top]:
        print(f"  {s:.2f}  [[{rels[i][:-3]}]]  ⇄  [[{rels[j][:-3]}]]")


if __name__ == "__main__":
    main()
