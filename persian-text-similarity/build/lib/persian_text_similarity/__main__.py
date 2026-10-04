"""Search a UTF-8 file containing one candidate per line."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
from .core import TfidfIndex


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--threshold", type=float, default=0.0)
    args = parser.parse_args()
    try:
        texts = [line for line in args.corpus.read_text(encoding="utf-8").splitlines() if line.strip()]
        matches = TfidfIndex(texts).search(args.query, args.top_k, args.threshold)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps([asdict(match) for match in matches], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
