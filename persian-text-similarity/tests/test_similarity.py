import math
import unittest
from persian_text_similarity import TfidfIndex, normalize, tokens
from persian_text_similarity.semantic import SemanticIndex


class SimilarityTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(normalize("  كِتاب‌های\u200f فارسی ١۲ـ۳  "), "کتاب های فارسی 123")
        self.assertEqual(normalize(normalize("ي ك ۱۲")), normalize("ي ك ۱۲"))
        self.assertEqual(tokens("سلام، دنیا! foo_bar"), ["سلام", "دنیا", "foo", "bar"])

    def test_exact_and_empty(self):
        self.assertAlmostEqual(TfidfIndex(["کتاب فارسی"]).search("كتاب فارسی")[0].score, 1)
        self.assertEqual(TfidfIndex(["", "کتاب"]).search("ناشناخته"), [])
        self.assertEqual(TfidfIndex([]).search("کتاب"), [])
        self.assertEqual(TfidfIndex(["کتاب"]).search(""), [])

    def test_known_cosine(self):
        matches = TfidfIndex(["الف ب", "الف ج"]).search("الف")
        expected = 1 / math.sqrt(1 + (math.log(3 / 2) + 1) ** 2)
        self.assertAlmostEqual(matches[0].score, expected)
        self.assertEqual([m.index for m in matches], [0, 1])

    def test_threshold_and_limits(self):
        index = TfidfIndex(["الف ب", "الف"])
        self.assertEqual([m.index for m in index.search("الف", threshold=0.9)], [1])
        self.assertEqual(len(index.search("الف", top_k=1)), 1)
        for k in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                index.search("الف", top_k=k)
        for threshold in (-1, 2, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                index.search("الف", threshold=threshold)

    def test_input_validation(self):
        with self.assertRaises(TypeError):
            normalize(None)
        with self.assertRaises(TypeError):
            TfidfIndex("کتاب")

    def test_semantic_adapter_without_download(self):
        class Encoder:
            def encode(self, texts, normalize_embeddings):
                self_flag = normalize_embeddings
                assert self_flag
                return [[0.0, 1.0] if t == "کتاب" else [1.0, 0.0] for t in texts]
        index = SemanticIndex(["كتاب", "جلسه", ""], encoder=Encoder())
        self.assertEqual([m.index for m in index.search("کتاب")], [0])
        self.assertEqual(index.search(""), [])
        self.assertEqual(SemanticIndex([], encoder=Encoder()).search("کتاب"), [])


if __name__ == "__main__":
    unittest.main()
