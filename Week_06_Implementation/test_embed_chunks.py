"""Embedding tests use fixed local vectors, not a downloaded model or an API."""

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch

from embed_chunks import encode_texts, load_chunks, save_index


class FixedTokenizer:
    def __call__(self, texts, **kwargs):
        self.options = kwargs
        return {
            "input_ids": torch.tensor([[0, 0, 0, 0], [1, 0, 0, 0], [2, 0, 0, 0]]),
            "attention_mask": torch.tensor([[1, 1, 1, 1], [1, 1, 1, 0], [1, 1, 1, 1]]),
            "overflow_to_sample_mapping": torch.tensor([0, 0, 1]),
        }

    def num_special_tokens_to_add(self, pair=False):
        return 2


class FixedModel:
    max_seq_length = 4

    def __init__(self):
        self.tokenizer = FixedTokenizer()

    def eval(self):
        return self

    def get_embedding_dimension(self):
        return 2

    def __call__(self, batch):
        vectors = torch.tensor([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        return {"sentence_embedding": vectors[batch["input_ids"][:, 0]]}


class EmbedChunksTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.chunk = {"id": "a.py:1-1", "file": "a.py", "start_line": 1, "end_line": 1, "text": "pass\n"}

    def test_all_overflow_windows_are_weighted_and_normalized(self):
        model = FixedModel()
        result = encode_texts(model, ["long text", "short text"], batch_size=1)
        np.testing.assert_allclose(result[0], np.array([2.0, 1.0]) / np.sqrt(5), atol=1e-6)
        np.testing.assert_allclose(result[1], np.array([1.0, 1.0]) / np.sqrt(2), atol=1e-6)
        np.testing.assert_allclose(np.linalg.norm(result, axis=1), 1, atol=1e-6)
        self.assertTrue(model.tokenizer.options["return_overflowing_tokens"])
        self.assertEqual(model.tokenizer.options["max_length"], model.max_seq_length)
        self.assertEqual(result.dtype, np.float32)

    def test_encoding_is_independent_of_batch_boundaries(self):
        one = encode_texts(FixedModel(), ["one", "two"], batch_size=1)
        both = encode_texts(FixedModel(), ["one", "two"], batch_size=2)
        np.testing.assert_allclose(one, both)

    def test_invalid_encoding_inputs(self):
        for texts, batch_size in (([], 1), (["text"], 0)):
            with self.subTest(texts=texts, batch_size=batch_size):
                with self.assertRaises(ValueError):
                    encode_texts(FixedModel(), texts, batch_size)

    def test_load_chunks_and_reject_duplicates(self):
        path = self.root / "chunks.jsonl"
        path.write_text(json.dumps(self.chunk) + "\n", encoding="utf-8")
        self.assertEqual(load_chunks(path), [self.chunk])
        path.write_text((json.dumps(self.chunk) + "\n") * 2, encoding="utf-8")
        with self.assertRaises(ValueError):
            load_chunks(path)

    def test_reject_empty_or_malformed_chunks(self):
        path = self.root / "chunks.jsonl"
        for content in ("", "{}\n", json.dumps({**self.chunk, "start_line": 0})):
            with self.subTest(content=content):
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_chunks(path)

    def test_storage_preserves_pairs_without_pickle(self):
        path = self.root / "index.npz"
        vectors = np.array([[1.0, 0.0]], dtype=np.float32)
        save_index(path, [self.chunk], vectors, {"model": "test"})
        with np.load(path, allow_pickle=False) as stored:
            np.testing.assert_array_equal(stored["vectors"], vectors)
            self.assertEqual(json.loads(stored["chunks"][0]), self.chunk)
            self.assertEqual(json.loads(stored["metadata"].item()), {"model": "test"})
        with self.assertRaises(ValueError):
            save_index(path, [self.chunk], np.empty((0, 2)), {})


if __name__ == "__main__":
    unittest.main()
