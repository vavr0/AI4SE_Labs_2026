"""Focused tests for repository chunking; no models or network access required."""

import tempfile
import unittest
from pathlib import Path

from chunk_repository import chunk_repository


class ChunkRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repository = Path(temporary.name)

    def write_file(self, name: str, text: str) -> None:
        path = self.repository / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_line_ranges_overlap_and_complete_content(self) -> None:
        lines = [f"line {number}\n" for number in range(1, 206)]
        self.write_file("source.py", "".join(lines))
        chunks = chunk_repository(self.repository)
        self.assertEqual(
            [(c["start_line"], c["end_line"]) for c in chunks],
            [(1, 100), (81, 180), (161, 205)],
        )
        reconstructed = chunks[0]["text"]
        for previous, following in zip(chunks, chunks[1:]):
            self.assertEqual(
                previous["text"].splitlines(keepends=True)[-20:],
                following["text"].splitlines(keepends=True)[:20],
            )
            reconstructed += "".join(following["text"].splitlines(keepends=True)[20:])
        self.assertEqual(reconstructed, "".join(lines))
        self.assertEqual(chunks[0]["id"], "source.py:1-100")

    def test_no_redundant_overlap_only_chunk(self) -> None:
        self.write_file("source.py", "line\n" * 180)
        self.assertEqual(len(chunk_repository(self.repository)), 2)

    def test_python_sources_and_tests_only_with_relative_paths(self) -> None:
        self.write_file("package/module.py", "x = 1\n")
        self.write_file("tests/test_module.py", "assert True\n")
        self.write_file("tests/__init__.py", "")
        self.write_file("notes.md", "Not code")
        for directory in (".git", ".jj", ".venv", "venv", "__pycache__"):
            self.write_file(f"{directory}/ignored.py", "ignore = True\n")
        chunks = chunk_repository(self.repository)
        self.assertEqual(
            [c["file"] for c in chunks],
            ["package/module.py", "tests/test_module.py"],
        )

    def test_deterministic_and_unique_ids(self) -> None:
        self.write_file("b.py", "b = 2\n")
        self.write_file("a.py", "a = 1\n")
        first = chunk_repository(self.repository)
        self.assertEqual(first, chunk_repository(self.repository))
        self.assertEqual(len(first), len({c["id"] for c in first}))

    def test_invalid_parameters(self) -> None:
        for size, overlap in ((0, 0), (-1, 0), (100, -1), (100, 100)):
            with self.subTest(size=size, overlap=overlap):
                with self.assertRaises(ValueError):
                    chunk_repository(self.repository, size, overlap)

    def test_missing_repository(self) -> None:
        with self.assertRaises(ValueError):
            chunk_repository(self.repository / "missing")


if __name__ == "__main__":
    unittest.main()
