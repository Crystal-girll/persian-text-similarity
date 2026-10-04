import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


class CliTests(unittest.TestCase):
    def test_json_output_and_bad_threshold(self):
        root = Path(__file__).resolve().parents[1]
        env = dict(os.environ, PYTHONPATH=str(root / "src"))
        command = [sys.executable, "-m", "persian_text_similarity",
                   "گزارش پروژه", str(root / "examples/corpus.txt")]
        result = subprocess.run(command, env=env, capture_output=True, text=True, check=True)
        matches = json.loads(result.stdout)
        self.assertEqual(matches[0]["index"], 1)
        self.assertIn("گزارش", matches[0]["text"])
        result = subprocess.run(command + ["--threshold", "nan"], env=env,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
