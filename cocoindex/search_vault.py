#!/usr/bin/env python3
"""
search_vault.py — semantic search over the CocoIndex/LanceDB vault index built by
index_vault.py. This is the vector-search upgrade to wiki-query's grep.

Prereqs: run `cocoindex update cocoindex/index_vault.py` first (with COCOINDEX_DB set).
    pip install lancedb sentence-transformers

Usage:
    python cocoindex/search_vault.py "why does attention pooling resist injection" [-k 5]

Env: OBSIDIAN_LANCEDB (default ~/.obsidian-grill/lancedb), must match index_vault.py.
"""
import argparse
import os
import pathlib
import sys

LANCEDB_URI = os.environ.get("OBSIDIAN_LANCEDB", str(pathlib.Path.home() / ".obsidian-grill" / "lancedb"))
MODEL = os.environ.get("OBSIDIAN_EMBED_MODEL", "all-MiniLM-L6-v2")


def main():
    ap = argparse.ArgumentParser(description="Semantic search over the vault index.")
    ap.add_argument("query")
    ap.add_argument("-k", "--top", type=int, default=5)
    args = ap.parse_args()

    try:
        import lancedb
        from sentence_transformers import SentenceTransformer
    except ImportError:
        sys.exit("error: pip install lancedb sentence-transformers")

    db = lancedb.connect(LANCEDB_URI)
    try:
        table = db.open_table("vault_chunks")
    except Exception:
        sys.exit("error: index not built — run `cocoindex update cocoindex/index_vault.py` first")

    qv = SentenceTransformer(MODEL).encode(args.query).tolist()
    rows = table.search(qv).limit(args.top).to_list()

    print(f"# semantic search — {args.query!r}  ({table.count_rows()} chunks)\n")
    for r in rows:
        dist = r.get("_distance", 0.0)
        rel = r["path"].split("obsidian-vault/")[-1]
        snippet = " ".join(r["text"].split())[:120]
        print(f"[{dist:.3f}] [[{rel[:-3]}]]\n        {snippet}\n")


if __name__ == "__main__":
    main()
