#!/usr/bin/env python3
"""
index_vault.py — incremental semantic index of an Obsidian vault with CocoIndex.

This is the *production / incremental* index layer for obsidian-grill: it walks
the vault's Markdown, chunks it, embeds the chunks, and writes vectors to LanceDB
(file-based, no server). When notes change, CocoIndex re-embeds only the changed
files (memoization) — so the index stays fresh without full re-runs, feeding the
"related-but-unlinked" and coverage-gap analysis.

Requirements (not bundled — install before running):
    pip install "cocoindex>=1.0.0" sentence-transformers lancedb
Vault path: $OBSIDIAN_VAULT_PATH or ~/.obsidian-wiki/config (default below).

Run (COCOINDEX_DB is CocoIndex's own incremental-state store, separate from the
LanceDB vector target):
    export COCOINDEX_DB=~/.obsidian-grill/cocoindex-state
    cocoindex update cocoindex/index_vault.py          # build / incremental update
    cocoindex update cocoindex/index_vault.py -L       # live mode (watch the vault)
    python cocoindex/search_vault.py "your query"      # query the index

Verified on cocoindex 1.0.6: uses lancedb.connect_async + LanceAsyncConnection;
the embedding vector column is declared via the dataclass Annotated[NDArray,
EMBEDDER] (no declare_vector_index call — LanceDB tables don't expose one).
"""
import os
import pathlib
from dataclasses import dataclass
from typing import Annotated, AsyncIterator

from numpy.typing import NDArray

import cocoindex as coco
from cocoindex.connectors import localfs, lancedb
from cocoindex.ops.text import RecursiveSplitter
from cocoindex.ops.sentence_transformers import SentenceTransformerEmbedder
from cocoindex.resources.chunk import Chunk
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from cocoindex.resources.id import IdGenerator


def _vault() -> pathlib.Path:
    if os.environ.get("OBSIDIAN_VAULT_PATH"):
        return pathlib.Path(os.environ["OBSIDIAN_VAULT_PATH"])
    cfg = pathlib.Path.home() / ".obsidian-wiki" / "config"
    if cfg.exists():
        for line in cfg.read_text().splitlines():
            if line.startswith("OBSIDIAN_VAULT_PATH="):
                return pathlib.Path(line.split("=", 1)[1].strip().strip('"'))
    return pathlib.Path("/workspace/obsidian-vault")


LANCEDB_URI = os.environ.get("OBSIDIAN_LANCEDB", str(pathlib.Path.home() / ".obsidian-grill" / "lancedb"))
LDB = coco.ContextKey[lancedb.LanceAsyncConnection]("ldb")
EMBEDDER = coco.ContextKey[SentenceTransformerEmbedder]("embedder")

_splitter = RecursiveSplitter()


@dataclass
class NoteChunk:
    id: int
    path: str                 # vault-relative note path (for [[wikilink]] mapping)
    title: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]   # dims inferred from the ContextKey
    chunk_start: int
    chunk_end: int


@coco.lifespan
async def coco_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
    conn = await lancedb.connect_async(LANCEDB_URI)
    builder.provide(LDB, conn)
    builder.provide(EMBEDDER, SentenceTransformerEmbedder("all-MiniLM-L6-v2"))
    yield


@coco.fn
async def process_chunk(chunk: Chunk, path: pathlib.PurePath, title: str,
                        id_gen: IdGenerator, table: lancedb.TableTarget[NoteChunk]) -> None:
    table.declare_row(row=NoteChunk(
        id=await id_gen.next_id(chunk.text),
        path=str(path),
        title=title,
        text=chunk.text,
        embedding=await coco.use_context(EMBEDDER).embed(chunk.text),
        chunk_start=chunk.start.char_offset,
        chunk_end=chunk.end.char_offset,
    ))


@coco.fn(memo=True)   # only re-embeds when a note's content/code changes
async def process_note(file: FileLike, table: lancedb.TableTarget[NoteChunk]) -> None:
    text = await file.read_text()
    title = file.file_path.path.stem
    chunks = _splitter.split(text, chunk_size=1200, chunk_overlap=200)
    id_gen = IdGenerator()
    await coco.map(process_chunk, chunks, file.file_path.path, title, id_gen, table)


@coco.fn
async def app_main(sourcedir: pathlib.Path) -> None:
    table = await lancedb.mount_table_target(
        LDB,
        table_name="vault_chunks",
        table_schema=await lancedb.TableSchema.from_class(NoteChunk, primary_key=["id"]),
    )

    files = localfs.walk_dir(
        sourcedir,
        recursive=True,
        live=True,   # works in catch-up too; `-L` enables continuous watching
        path_matcher=PatternFilePathMatcher(
            included_patterns=["**/*.md"],
            excluded_patterns=["**/.*/**", ".raw/**", ".obsidian/**"],
        ),
    )
    await coco.mount_each(process_note, files.items(), table)


app = coco.App(coco.AppConfig(name="ObsidianVaultIndex"), app_main, sourcedir=_vault())
