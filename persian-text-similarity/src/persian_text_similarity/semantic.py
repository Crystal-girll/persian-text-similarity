"""Optional sentence-transformers adapter; model weights are not bundled."""

from .core import Match, _validate, normalize


class SemanticIndex:
    """Cosine retrieval using a caller-supplied sentence encoder.

    The encoder must support encode(texts, normalize_embeddings=True).
    A supplied encoder permits offline tests and custom/local models.
    """

    def __init__(self, texts: list[str], *, encoder):
        if isinstance(texts, (str, bytes)):
            raise TypeError("texts must be a sequence of strings")
        self.texts = tuple(texts)
        self.encoder = encoder
        self._vectors = encoder.encode([normalize(t) for t in self.texts],
                                       normalize_embeddings=True) if self.texts else []

    @classmethod
    def from_model(cls, texts: list[str], model_name: str, *, local_files_only: bool = True):
        """Load a model; downloads require explicitly opting out of local-only."""
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError('Install the optional extra: pip install ".[semantic]"') from exc
        return cls(texts, encoder=SentenceTransformer(
            model_name, local_files_only=local_files_only, trust_remote_code=False))

    def search(self, query: str, top_k: int = 5, threshold: float = 0.0) -> list[Match]:
        _validate(top_k, threshold)
        query = normalize(query)
        if not query or not self.texts:
            return []
        vector = self.encoder.encode([query], normalize_embeddings=True)[0]
        matches = []
        for i, document in enumerate(self._vectors):
            if len(vector) != len(document):
                raise ValueError("encoder returned inconsistent vector dimensions")
            score = max(-1.0, min(1.0, float(sum(a * b for a, b in zip(vector, document)))))
            if score > 0 and score >= threshold and normalize(self.texts[i]):
                matches.append(Match(i, self.texts[i], score))
        return sorted(matches, key=lambda match: (-match.score, match.index))[:top_k]
