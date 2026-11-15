"""Retrieve the n most similar code chunks using local cosine matching."""

import argparse
import json
from pathlib import Path

import numpy as np

from embed_chunks import MODEL_NAME, MODEL_REVISION, encode_texts, load_model


def load_index(path: Path) -> tuple[list[dict], np.ndarray, dict]:
    with np.load(path, allow_pickle=False) as stored:
        chunks = [json.loads(record) for record in stored["chunks"]]
        vectors = stored["vectors"].astype(np.float32)
        metadata = json.loads(stored["metadata"].item())
    if not chunks or vectors.ndim != 2 or len(vectors) != len(chunks):
        raise ValueError("Index must contain one vector for every chunk")
    if not all(
        isinstance(chunk, dict)
        and all(key in chunk for key in ("id", "file", "start_line", "end_line", "text"))
        for chunk in chunks
    ):
        raise ValueError("Index contains invalid chunk records")
    if len({chunk["id"] for chunk in chunks}) != len(chunks):
        raise ValueError("Index contains duplicate chunk IDs")
    if metadata.get("format_version") != 1 or metadata.get("dimension") != vectors.shape[1]:
        raise ValueError("Unsupported index format or inconsistent vector dimensions")
    if metadata.get("model") != MODEL_NAME or metadata.get("revision") != MODEL_REVISION:
        raise ValueError("Index was built with a different embedding model or revision")
    return chunks, vectors, metadata


def match_chunks(
    query_embedding: np.ndarray, chunks: list[dict], vectors: np.ndarray, n: int = 5
) -> list[dict]:
    """Return up to n chunk records, including cosine scores, highest first."""
    query = np.asarray(query_embedding, dtype=np.float32)
    vectors = np.asarray(vectors, dtype=np.float32)
    if n < 1:
        raise ValueError("n must be positive")
    if vectors.ndim != 2 or not len(chunks) or len(vectors) != len(chunks):
        raise ValueError("Provide a nonempty vector matrix matching the chunk records")
    if query.ndim != 1 or query.shape[0] != vectors.shape[1]:
        raise ValueError("Query embedding must match the index vector dimension")
    if not np.isfinite(query).all() or not np.isfinite(vectors).all():
        raise ValueError("Embeddings must contain only finite values")
    query_norm = np.linalg.norm(query)
    vector_norms = np.linalg.norm(vectors, axis=1)
    if not np.isfinite(query_norm) or query_norm == 0 or np.any(vector_norms == 0) or not np.isfinite(vector_norms).all():
        raise ValueError("Embeddings must have finite, nonzero norms")
    scores = (vectors / vector_norms[:, None]) @ (query / query_norm)
    order = np.argsort(-scores, kind="stable")[:n]
    return [{**chunks[int(i)], "score": float(scores[i])} for i in order]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    try:
        if not args.query.strip() or args.top_k < 1:
            raise ValueError("Provide a nonempty query and a positive --top-k")
        chunks, vectors, metadata = load_index(args.index)
        model = load_model(local_files_only=True)
        if metadata.get("max_tokens") != model.max_seq_length:
            raise ValueError("Query encoder token limit differs from the stored index")
        query = encode_texts(model, [args.query])[0]
        matches = match_chunks(query, chunks, vectors, args.top_k)
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    for rank, match in enumerate(matches, 1):
        print(f"{rank}. {match['score']:.4f} {match['file']}:{match['start_line']}-{match['end_line']}")


if __name__ == "__main__":
    main()
