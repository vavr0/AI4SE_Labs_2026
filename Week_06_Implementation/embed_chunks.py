"""Embed JSONL code chunks locally and save chunk/vector pairs in a NumPy archive."""

import argparse
import hashlib
import json
from importlib.metadata import version
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as functional
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"


def load_chunks(path: Path) -> list[dict]:
    chunks = []
    identifiers = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        chunk = json.loads(line)
        if not isinstance(chunk, dict) or not all(
            key in chunk for key in ("id", "file", "start_line", "end_line", "text")
        ):
            raise ValueError(f"Invalid chunk record on line {line_number}")
        if any(not isinstance(chunk[key], str) or not chunk[key] for key in ("id", "file", "text")):
            raise ValueError(f"Invalid chunk strings on line {line_number}")
        start, end = chunk["start_line"], chunk["end_line"]
        if type(start) is not int or type(end) is not int or not 1 <= start <= end:
            raise ValueError(f"Invalid chunk line range on line {line_number}")
        if chunk["id"] in identifiers:
            raise ValueError(f"Duplicate chunk ID: {chunk['id']}")
        identifiers.add(chunk["id"])
        chunks.append(chunk)
    if not chunks:
        raise ValueError("The chunk file is empty")
    return chunks


def load_model(*, local_files_only: bool = False) -> SentenceTransformer:
    """Load public, pinned weights on CPU; optionally require the local cache."""
    return SentenceTransformer(
        MODEL_NAME,
        revision=MODEL_REVISION,
        local_files_only=local_files_only,
        device="cpu",
        token=False,
        trust_remote_code=False,
        model_kwargs={"use_safetensors": True},
    )


def encode_texts(model, texts: list[str], batch_size: int = 16) -> np.ndarray:
    """Pool every token window so long chunks are not silently truncated."""
    if not texts or batch_size < 1:
        raise ValueError("Provide at least one text and a positive batch size")
    model.eval()
    features = model.tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=model.max_seq_length,
        return_overflowing_tokens=True,
        return_tensors="pt",
    )
    owners = features.pop("overflow_to_sample_mapping")
    sums = torch.zeros((len(texts), model.get_embedding_dimension()))
    totals = torch.zeros(len(texts))
    special_tokens = model.tokenizer.num_special_tokens_to_add(pair=False)
    with torch.inference_mode():
        for start in range(0, len(owners), batch_size):
            batch = {key: value[start:start + batch_size] for key, value in features.items()}
            vectors = functional.normalize(model(batch)["sentence_embedding"], dim=1)
            weights = (batch["attention_mask"].sum(dim=1) - special_tokens).clamp_min(1).float()
            batch_owners = owners[start:start + batch_size]
            sums.index_add_(0, batch_owners, vectors * weights[:, None])
            totals.index_add_(0, batch_owners, weights)
        result = functional.normalize(sums / totals[:, None], dim=1).numpy()
    if not np.isfinite(result).all() or np.any(np.linalg.norm(result, axis=1) == 0):
        raise ValueError("The model returned invalid or zero embeddings")
    return result.astype(np.float32)


def save_index(path: Path, chunks: list[dict], vectors: np.ndarray, metadata: dict) -> None:
    if vectors.ndim != 2 or len(vectors) != len(chunks):
        raise ValueError("Each chunk must have exactly one embedding")
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        vectors=vectors,
        chunks=np.asarray([json.dumps(chunk, ensure_ascii=False) for chunk in chunks]),
        metadata=np.asarray(json.dumps(metadata)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.suffix != ".npz":
            raise ValueError("Output must have the .npz extension")
        chunks = load_chunks(args.chunks)
        model = load_model()
        texts = [f"File: {chunk['file']}\n{chunk['text']}" for chunk in chunks]
        vectors = encode_texts(model, texts)
        metadata = {
            "format_version": 1,
            "model": MODEL_NAME,
            "revision": MODEL_REVISION,
            "max_tokens": model.max_seq_length,
            "dimension": int(vectors.shape[1]),
            "representation": "repository-relative file path followed by original chunk text",
            "pooling": "token-weighted mean of normalized window vectors, then L2 normalization",
            "chunks_sha256": hashlib.sha256(args.chunks.read_bytes()).hexdigest(),
            "packages": {name: version(name) for name in ("numpy", "torch", "sentence-transformers", "transformers")},
        }
        save_index(args.output, chunks, vectors, metadata)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"Saved {len(chunks)} chunk/vector pairs ({vectors.shape[1]} dimensions) to {args.output}")


if __name__ == "__main__":
    main()
