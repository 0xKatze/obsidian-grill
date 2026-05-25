#!/usr/bin/env python3
"""
vault_lint.py — deterministic health checks for an Obsidian vault (the "unit
tests" of the knowledge base). Part of the obsidian-grill framework.

Checks:
  - broken [[wikilinks]]            (target resolves to no note)
  - orphan notes                   (no inbound wikilinks; excludes index/meta)
  - missing / invalid frontmatter  (no YAML block, or missing title & tags)
  - duplicate note basenames       (ambiguous wikilink targets)

Vault path resolution (first hit wins):
  1. --vault PATH
  2. $OBSIDIAN_VAULT_PATH
  3. OBSIDIAN_VAULT_PATH in ~/.obsidian-wiki/config

Exit code is non-zero when broken links or invalid frontmatter are found, so it
can gate a CI step or the iteration loop.
"""
import argparse
import os
import pathlib
import re
import sys
from collections import defaultdict

WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")
FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
EXCLUDE_ORPHAN = ("index", "overview", "readme", "hot", "log", "wiki_agent", "moc")


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
    sys.exit("error: no vault path (use --vault, $OBSIDIAN_VAULT_PATH, or ~/.obsidian-wiki/config)")


def link_target(raw):
    """Normalize a raw wikilink body to its note target (drop alias/heading)."""
    t = raw.replace("\\|", "|")  # Obsidian escapes pipes as \| inside tables
    t = t.split("|", 1)[0]         # drop |alias
    t = t.split("#", 1)[0]         # drop #heading
    return t.strip().rstrip("\\")


def main():
    ap = argparse.ArgumentParser(description="Lint an Obsidian vault.")
    ap.add_argument("--vault", help="Vault path (else env / ~/.obsidian-wiki/config).")
    ap.add_argument("--quiet", action="store_true", help="Summary only.")
    args = ap.parse_args()

    vault = resolve_vault(args.vault)
    if not vault.is_dir():
        sys.exit(f"error: vault not found: {vault}")

    notes = [p for p in vault.rglob("*.md")
             if p.is_file()
             and not any(part.startswith(".") for part in p.relative_to(vault).parts)]
    rel = {p.relative_to(vault).as_posix()[:-3]: p for p in notes}   # path w/o .md
    rel_lower = {k.lower() for k in rel}
    by_base = defaultdict(list)
    for p in notes:
        by_base[p.stem].append(p)
    base_lower = {b.lower() for b in by_base}

    MEDIA = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf",
             ".excalidraw", ".canvas", ".mp4", ".mov", ".mp3", ".wav")

    def resolves(target):                       # case-insensitive, path or basename
        t = target.lower()
        if t in rel_lower:
            return True
        if t.endswith(".md") and t[:-3] in rel_lower:
            return True
        return t.rsplit("/", 1)[-1].removesuffix(".md") in base_lower

    broken, no_fm, inbound = [], [], defaultdict(int)
    for p in notes:
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm = FRONTMATTER.match(text)
        if not fm or not ("title" in fm.group(1) or "tags" in fm.group(1)):
            no_fm.append(p.relative_to(vault).as_posix())
        for m in WIKILINK.finditer(text):
            tgt = link_target(m.group(1))
            if not tgt or tgt.lower().endswith(MEDIA):
                continue
            if resolves(tgt):
                # count inbound for the resolved note (best-effort by basename)
                base = tgt.rsplit("/", 1)[-1].removesuffix(".md")
                for q in by_base.get(base, []):
                    if q != p:
                        inbound[q.relative_to(vault).as_posix()] += 1
            else:
                broken.append((p.relative_to(vault).as_posix(), tgt))

    orphans = [p.relative_to(vault).as_posix() for p in notes
               if inbound[p.relative_to(vault).as_posix()] == 0
               and p.stem.lower() not in EXCLUDE_ORPHAN]
    dup = {b: [q.relative_to(vault).as_posix() for q in ps]
           for b, ps in by_base.items() if len(ps) > 1}

    # ---- report ----
    print(f"# vault lint — {vault}")
    print(f"notes: {len(notes)}")
    print(f"broken wikilinks: {len(broken)}")
    print(f"notes missing/!invalid frontmatter: {len(no_fm)}")
    print(f"orphan notes (no inbound links): {len(orphans)}")
    print(f"duplicate basenames: {len(dup)}")
    if not args.quiet:
        if broken:
            print("\n## broken wikilinks")
            for src, tgt in broken[:60]:
                print(f"- {src} → [[{tgt}]]")
            if len(broken) > 60:
                print(f"  …and {len(broken)-60} more")
        if dup:
            print("\n## duplicate basenames (ambiguous link targets)")
            for b, ps in list(dup.items())[:30]:
                print(f"- {b}: {', '.join(ps)}")
        if no_fm:
            print("\n## missing/invalid frontmatter")
            for f in no_fm[:40]:
                print(f"- {f}")
            if len(no_fm) > 40:
                print(f"  …and {len(no_fm)-40} more")
        if orphans:
            print(f"\n## orphan notes ({len(orphans)})")
            for f in orphans[:40]:
                print(f"- {f}")
            if len(orphans) > 40:
                print(f"  …and {len(orphans)-40} more")

    sys.exit(1 if (broken or no_fm) else 0)


if __name__ == "__main__":
    main()
