#!/usr/bin/env python3
"""
vault_stats.py — knowledge-base metrics for the obsidian-grill iteration loop.

Reports coverage and drift signals that tell you what the next grilling round
should focus on:
  - totals (notes, with frontmatter / tags / wikilinks / open-questions)
  - notes per top-level category (folder)
  - index drift (the count index.md claims vs the real note count)
  - staleness (notes whose frontmatter `updated` is older than --stale-days)
  - top tags (taxonomy snapshot)
  - decisions missing a `status` (under any */decisions/ folder)

Vault path resolves from --vault, $OBSIDIAN_VAULT_PATH, or ~/.obsidian-wiki/config.
"""
import argparse
import datetime as dt
import os
import pathlib
import re
import sys
from collections import Counter

FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
UPDATED = re.compile(r"^updated:\s*(.+)$", re.M)
INDEX_CLAIM = re.compile(r"(\d+)\s+pages", re.I)
TAGS = re.compile(r"tags:\s*\[([^\]]*)\]")


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


def parse_date(s):
    s = s.strip().strip('"').strip("'")
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(s[:len(fmt) + 2] if "T" in fmt else s[:10], fmt)
        except ValueError:
            continue
    try:
        return dt.datetime.fromisoformat(s.replace("Z", ""))
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description="Obsidian vault metrics.")
    ap.add_argument("--vault")
    ap.add_argument("--stale-days", type=int, default=120)
    args = ap.parse_args()

    vault = resolve_vault(args.vault)
    notes = [p for p in vault.rglob("*.md")
             if p.is_file()
             and not any(part.startswith(".") for part in p.relative_to(vault).parts)]
    total = len(notes)
    fm = tags = links = openq = 0
    cats, tagc = Counter(), Counter()
    stale, no_status = [], []
    now = dt.datetime.utcnow()
    cutoff = now - dt.timedelta(days=args.stale_days)

    for p in notes:
        text = p.read_text(encoding="utf-8", errors="ignore")
        m = FRONTMATTER.match(text)
        head = m.group(1) if m else ""
        if m:
            fm += 1
        if "tags:" in head:
            tags += 1
            tm = TAGS.search(head)
            if tm:
                for t in tm.group(1).split(","):
                    t = t.strip().strip('"').strip("'").lstrip("#")
                    if t:
                        tagc[t] += 1
        if "[[" in text:
            links += 1
        if re.search(r"open questions", text, re.I):
            openq += 1
        rel = p.relative_to(vault)
        cats[rel.parts[0] if len(rel.parts) > 1 else "(root)"] += 1
        um = UPDATED.search(head)
        if um:
            d = parse_date(um.group(1))
            if d and d < cutoff:
                stale.append((rel.as_posix(), d.date().isoformat()))
        if "decisions/" in rel.as_posix() and "status:" not in head:
            no_status.append(rel.as_posix())

    # index drift
    drift = ""
    idx = vault / "index.md"
    if idx.exists():
        cm = INDEX_CLAIM.search(idx.read_text(encoding="utf-8", errors="ignore"))
        if cm:
            claimed = int(cm.group(1))
            drift = f"index.md claims {claimed} pages; actual {total} → drift {total - claimed:+d}"

    print(f"# vault stats — {vault}")
    print(f"notes: {total}")
    print(f"  with frontmatter: {fm} ({fm*100//max(total,1)}%)")
    print(f"  with tags:        {tags} ({tags*100//max(total,1)}%)")
    print(f"  with wikilinks:   {links} ({links*100//max(total,1)}%)")
    print(f"  with Open Questions: {openq}")
    if drift:
        print(f"\n## index drift\n{drift}")
    print("\n## notes per category")
    for c, n in cats.most_common():
        print(f"  {c:16} {n}")
    print(f"\n## stale notes (updated < {args.stale_days}d ago): {len(stale)}")
    for f, d in sorted(stale, key=lambda x: x[1])[:20]:
        print(f"  {d}  {f}")
    if no_status:
        print(f"\n## decision notes missing `status`: {len(no_status)}")
        for f in no_status[:20]:
            print(f"  {f}")
    print("\n## top tags")
    for t, n in tagc.most_common(20):
        print(f"  #{t:24} {n}")


if __name__ == "__main__":
    main()
