"""Normalization and an interpretable word-level TF-IDF baseline."""

from collections import Counter
from dataclasses import dataclass
import math
import re
import unicodedata

_TRANSLATION = str.maketrans("يك٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "یک01234567890123456789")
_MARKS = re.compile(r"[\u064b-\u065f\u0670\u06d6-\u06ed]")


def normalize(text: str) -> str:
    """Unify Arabic/Persian variants, digits, marks and whitespace.

    ZWNJ becomes a word boundary; this deliberately loses half-space styling.
    Punctuation remains here and is discarded only by ``tokens``.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    text = unicodedata.normalize("NFKC", text).translate(_TRANSLATION)
    text = _MARKS.sub("", text).replace("ـ", "")
    for char in ("\u200c", "\u200d", "\u200e", "\u200f", "\ufeff"):
        text = text.replace(char, " ")
    return " ".join(text.casefold().split())


def tokens(text: str) -> list[str]:
    """Extract Unicode word tokens, excluding underscores and punctuation."""
    return re.findall(r"[^\W_]+", normalize(text), flags=re.UNICODE)


@dataclass(frozen=True)
class Match:
    index: int
    text: str
    score: float


def _unit(vector: dict[str, float]) -> dict[str, float]:
    length = math.sqrt(sum(value * value for value in vector.values()))
    return {key: value / length for key, value in vector.items()} if length else {}


def _validate(top_k: int, threshold: float) -> None:
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k must be a positive integer")
    if not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("threshold must be finite and between 0 and 1")


class TfidfIndex:
    """Immutable corpus index using smoothed IDF and raw token counts.

    IDF = log((1 + document count) / (1 + document frequency)) + 1.
    Query terms outside the fitted vocabulary are ignored. Scores measure
    lexical overlap, not semantic equivalence or duplicate probability.
    """

    def __init__(self, texts: list[str]):
        if isinstance(texts, (str, bytes)):
            raise TypeError("texts must be a sequence of strings")
        self.texts = tuple(texts)
        counts = [Counter(tokens(text)) for text in self.texts]
        frequency = Counter(word for count in counts for word in count)
        self._idf = {word: math.log((1 + len(counts)) / (1 + n)) + 1
                     for word, n in frequency.items()}
        self._vectors = tuple(self._vector(count) for count in counts)

    def _vector(self, count: Counter) -> dict[str, float]:
        return _unit({word: n * self._idf[word] for word, n in count.items()
                      if word in self._idf})

    def search(self, query: str, top_k: int = 5, threshold: float = 0.0) -> list[Match]:
        """Return positive-score matches, descending; ties use input order."""
        _validate(top_k, threshold)
        vector = self._vector(Counter(tokens(query)))
        matches = []
        for index, document in enumerate(self._vectors):
            score = min(1.0, max(0.0, sum(value * document.get(word, 0.0)
                                        for word, value in vector.items())))
            if score > 0 and score >= threshold:
                matches.append(Match(index, self.texts[index], score))
        return sorted(matches, key=lambda match: (-match.score, match.index))[:top_k]
