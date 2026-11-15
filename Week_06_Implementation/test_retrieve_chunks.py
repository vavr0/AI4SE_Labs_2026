"""Cosine ranking and index compatibility tests; no model or API needed."""

import tempfile
import unittest
from pathlib import Path

import numpy as np

from embed_chunks import MODEL_NAME, MODEL_REVISION, save_index
from retrieve_chunks import load_index, match_chunks


class RetrieveChunksTests(unittest.TestCase):
    def setUp(self):
        self.chunks = [
            {"id": f"{name}.py:1-1", "file": f"{name}.py", "start_line": 1, "end_line": 1, "text": "pass\n"}
            for name in ("a", "b", "c")
        ]
        self.vectors = np.array([[1, 0], [0, 1], [-1, 0]], dtype=np.float32)

    def test_top_n_are_returned_in_descending_similarity(self):
        matches = match_chunks([1, 0], self.chunks, self.vectors, 2)
        self.assertEqual([m["id"] for m in matches], ["a.py:1-1", "b.py:1-1"])
        np.testing.assert_allclose([m["score"] for m in matches], [1, 0])
        self.assertEqual(matches[0]["text"], "pass\n")
        self.assertNotIn("score", self.chunks[0])

    def test_cosine_is_independent_of_vector_magnitude(self):
        vectors = np.array([[100, 100], [1, 0]], dtype=np.float32)
        matches = match_chunks([2, 0], self.chunks[:2], vectors, 2)
        self.assertEqual(matches[0]["id"], "b.py:1-1")
        np.testing.assert_allclose([m["score"] for m in matches], [1, 1 / np.sqrt(2)], atol=1e-6)

    def test_ties_are_stable_and_n_is_limited_to_available_chunks(self):
        vectors = np.array([[1, 0], [1, 0]], dtype=np.float32)
        matches = match_chunks([1, 0], self.chunks[:2], vectors, 10)
        self.assertEqual([m["id"] for m in matches], ["a.py:1-1", "b.py:1-1"])

    def test_invalid_queries_vectors_or_n_are_rejected(self):
        cases = [
            ([1, 0], self.chunks, self.vectors, 0),
            ([0, 0], self.chunks, self.vectors, 2),
            ([float("nan"), 0], self.chunks, self.vectors, 2),
            ([[1, 0]], self.chunks, self.vectors, 2),
            ([1, 0, 0], self.chunks, self.vectors, 2),
            ([1, 0], self.chunks[:1], self.vectors, 2),
            ([1, 0], [], np.empty((0, 2)), 2),
            ([1, 0], self.chunks, np.zeros((3, 2)), 2),
            ([1, 0], self.chunks, np.full((3, 2), np.inf), 2),
        ]
        for query, chunks, vectors, n in cases:
            with self.subTest(query=query, n=n):
                with self.assertRaises(ValueError):
                    match_chunks(query, chunks, vectors, n)

    def test_index_round_trip(self):
        metadata = {"format_version": 1, "dimension": 2, "model": MODEL_NAME, "revision": MODEL_REVISION}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.npz"
            save_index(path, self.chunks, self.vectors, metadata)
            chunks, vectors, loaded_metadata = load_index(path)
        self.assertEqual(chunks, self.chunks)
        np.testing.assert_array_equal(vectors, self.vectors)
        self.assertEqual(loaded_metadata, metadata)

    def test_incompatible_index_metadata_is_rejected(self):
        metadata = {"format_version": 1, "dimension": 2, "model": MODEL_NAME, "revision": MODEL_REVISION}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.npz"
            for changed in ({"model": "other"}, {"revision": "other"}, {"dimension": 3}, {"format_version": 2}):
                with self.subTest(changed=changed):
                    save_index(path, self.chunks, self.vectors, {**metadata, **changed})
                    with self.assertRaises(ValueError):
                        load_index(path)


if __name__ == "__main__":
    unittest.main()
