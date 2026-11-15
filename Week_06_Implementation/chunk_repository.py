"""Split a Python repository into overlapping, traceable JSONL chunks."""

import argparse
import json
from pathlib import Path


IGNORED_DIRECTORIES = {".git", ".jj", ".venv", "venv", "__pycache__"}


def chunk_repository(
    repository: Path, chunk_lines: int = 100, overlap_lines: int = 20
) -> list[dict]:
    """Return deterministic chunks with repository-relative paths and line ranges."""
    if chunk_lines < 1:
        raise ValueError("chunk_lines must be positive")
    if not 0 <= overlap_lines < chunk_lines:
        raise ValueError("overlap_lines must be between 0 and chunk_lines - 1")
    repository = repository.resolve()
    if not repository.is_dir():
        raise ValueError(f"Repository directory does not exist: {repository}")

    chunks = []
    step = chunk_lines - overlap_lines
    for path in sorted(repository.rglob("*.py")):
        relative = path.relative_to(repository)
        if (
            not path.is_file()
            or path.is_symlink()
            or IGNORED_DIRECTORIES.intersection(relative.parts[:-1])
        ):
            continue
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        filename = relative.as_posix()
        for start in range(0, len(lines), step):
            end = min(start + chunk_lines, len(lines))
            chunks.append(
                {
                    "id": f"{filename}:{start + 1}-{end}",
                    "file": filename,
                    "start_line": start + 1,
                    "end_line": end,
                    "text": "".join(lines[start:end]),
                }
            )
            if end == len(lines):
                break
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--chunk-lines", type=int, default=100)
    parser.add_argument("--overlap-lines", type=int, default=20)
    args = parser.parse_args()
    try:
        if args.output.suffix == ".py":
            raise ValueError("Output must not overwrite a Python source file")
        chunks = chunk_repository(args.repo, args.chunk_lines, args.overlap_lines)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            "".join(json.dumps(chunk, ensure_ascii=False) + "\n" for chunk in chunks),
            encoding="utf-8",
        )
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    files = len({chunk["file"] for chunk in chunks})
    print(f"Saved {len(chunks)} chunks from {files} files to {args.output}")


if __name__ == "__main__":
    main()
