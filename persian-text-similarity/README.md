# Persian Text Similarity

A small Python toolkit for normalizing Persian text and retrieving similar
sentences. It provides a dependency-free lexical baseline and an optional
sentence-embedding adapter for semantic retrieval.

**Status:** initial alpha, version 0.1.0. No public adoption or benchmark
accuracy is claimed. This repository contains newly written generic utilities
and synthetic examples, not client code, private datasets, or business rules.

## Why this exists

Persian text can mix Arabic/Persian letter variants, digit forms, diacritics,
and half-spaces. A transparent baseline makes those differences easier to
handle before trying a larger embedding model. Use it to prototype search
over short notes, inspect candidate duplicates, or teach text retrieval.

## Quick start

Requires Python 3.10 or newer. From a downloaded or cloned repository:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install .
python examples/demo.py
persian-similarity 'گزارش پروژه' examples/corpus.txt --top-k 2
```

Windows activation: `.venv\Scripts\activate`.
The package is not claimed to be published on PyPI; install from this checkout.

```python
from persian_text_similarity import normalize, TfidfIndex

assert normalize("كتاب‌های فارسی ۱۲۳") == "کتاب های فارسی 123"
index = TfidfIndex(["گزارش پروژه آماده است", "خرید کتاب فارسی"])
for match in index.search("گزارش پروژه", top_k=3, threshold=0.2):
    print(match.index, match.text, round(match.score, 3))
```

Matches retain original text and zero-based corpus position. The CLI reads one
nonblank candidate per UTF-8 line and returns JSON; its positions refer to that
filtered list. Positive scores are sorted descending; ties retain input order.
Empty queries and unknown-vocabulary queries return no lexical matches.

## Optional semantic retrieval

Install `python -m pip install '.[semantic]'`, then supply an encoder or model:

```python
from persian_text_similarity.semantic import SemanticIndex

index = SemanticIndex.from_model(
    ["گزارش پروژه آماده است", "کتاب را خریدم"],
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    local_files_only=False,  # explicitly allow the first model download
)
print(index.search("نتیجه کار آماده شده", top_k=2))
```

This example is a starting point, not a Persian quality recommendation.
Model loading defaults to local files only and remote model code is disabled.
The first download may be large; weights and their license are separate from
this package's MIT license. Review the selected model's card before use.
Inference runs through the local encoder. The dependency-free baseline performs
no network requests. Do not submit confidential data to external encoders.

## Method and limits

- Normalization uses NFKC, maps `ي/ك` to `ی/ک`, maps Persian and Arabic digits
  to ASCII, removes Arabic marks/tatweel, case-folds, and collapses whitespace.
- ZWNJ and selected invisible separators become spaces. This loses half-space
  spelling. `می‌روم` and `می روم` align; `میروم` is not segmented automatically.
- Tokens are Unicode word runs excluding underscores. No stemming, synonym
  expansion, stopword removal, or language detection is performed.
- TF-IDF uses raw counts and `log((1 + N) / (1 + df)) + 1`; vectors are L2
  normalized. Query words outside the corpus vocabulary are ignored, which
  can inflate similarity for partly unknown queries.
- TF-IDF scores measure word overlap. They do **not** understand paraphrases,
  negation, or meaning. Semantic scores depend on the chosen encoder and also
  can miss negation. Neither score is a probability of duplication.
- Both search methods return only positive scores meeting a threshold in
  `[0, 1]`. Semantic cosine can be negative; those matches are omitted.
- Retrieval scans the corpus in memory. This is intended for small corpora,
  not a large-scale vector database. Tune thresholds on your own labeled data.

## Development

```sh
python -m pip install -e '.[dev]'
python -m unittest discover -s tests -v
python -m build
python -m twine check dist/*
```

Tests check normalization, a manually calculated cosine score, empty inputs,
stable ranking, threshold validation, and semantic adapter behavior using a fake
encoder. They are correctness tests, not a quality benchmark. CI exercises Python
3.10–3.13 and builds source/wheel packages. Real model integration is not tested
by the offline suite. See [CONTRIBUTING.md](CONTRIBUTING.md) and
[RELEASING.md](RELEASING.md).

## Roadmap

Collect an openly licensed Persian sentence-pair evaluation set; compare lexical
and semantic retrieval with documented metrics; add configurable normalization
only when real examples justify it. These are planned tasks, not shipped features.

## License

[MIT](LICENSE). External model weights retain their own licenses.
