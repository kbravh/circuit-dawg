#!/usr/bin/env python3
"""
Generate DAWG test fixtures using the `dawg` C extension library.

This script must be run with `dawg` installed (requires Python <=3.9 due to
the C extension). The generated .dawg files are committed to tests/fixtures/
so that the test suite can run without the `dawg` dependency.

Usage:
    pip install dawg
    python scripts/generate_fixtures.py
"""

import os
import sys
import zipfile

import dawg

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures")
WORDS_ZIP = os.path.join(os.path.dirname(__file__), "..", "tests", "words100k.zip")


def words100k():
    zf = zipfile.ZipFile(WORDS_ZIP)
    txt = zf.open(zf.namelist()[0]).read().decode("utf8")
    return txt.splitlines()


def main():
    os.makedirs(FIXTURES_DIR, exist_ok=True)

    # 1. Basic DAWG
    keys = ["f", "bar", "foo", "foobar"]
    dawg.DAWG(keys).save(os.path.join(FIXTURES_DIR, "dawg.dawg"))
    print("  dawg.dawg")

    # 2. CompletionDAWG
    dawg.CompletionDAWG(keys).save(os.path.join(FIXTURES_DIR, "completion.dawg"))
    print("  completion.dawg")

    # 3. CompletionDAWG (empty)
    dawg.CompletionDAWG([]).save(os.path.join(FIXTURES_DIR, "completion-empty.dawg"))
    print("  completion-empty.dawg")

    # 4. BytesDAWG
    bytes_data = [
        ("foo", b"data1"),
        ("bar", b"data2"),
        ("foo", b"data3"),
        ("foobar", b"data4"),
    ]
    dawg.BytesDAWG(bytes_data).save(os.path.join(FIXTURES_DIR, "bytes.dawg"))
    print("  bytes.dawg")

    # 5. RecordDAWG (>3H format)
    record_data = [
        ("foo", (3, 2, 256)),
        ("bar", (3, 1, 0)),
        ("foo", (3, 2, 1)),
        ("foobar", (6, 3, 0)),
    ]
    dawg.RecordDAWG(str(">3H"), record_data).save(
        os.path.join(FIXTURES_DIR, "record.dawg")
    )
    print("  record.dawg")

    # 6. RecordDAWG for prediction (=H format, Cyrillic data)
    prediction_words = [
        "ЁЖИК",
        "ЁЖИКЕ",
        "ЁЖ",
        "ДЕРЕВНЯ",
        "ДЕРЁВНЯ",
        "ЕМ",
        "ОЗЕРА",
        "ОЗЁРА",
        "ОЗЕРО",
    ]
    prediction_data = [(k, (len(k),)) for k in prediction_words]
    dawg.RecordDAWG(str("=H"), prediction_data).save(
        os.path.join(FIXTURES_DIR, "prediction-record.dawg")
    )
    print("  prediction-record.dawg")

    # 7. IntDAWG from words100k
    words = words100k()
    values = [len(w) for w in words]
    dawg.IntDAWG(zip(words, values)).save(os.path.join(FIXTURES_DIR, "int.dawg"))
    print("  int.dawg")

    # 8. IntCompletionDAWG (small)
    int_completion_data = {"foo": 1, "bar": 5, "foobar": 3}
    dawg.IntCompletionDAWG(int_completion_data.items()).save(
        os.path.join(FIXTURES_DIR, "int-completion.dawg")
    )
    print("  int-completion.dawg")

    # 9. CompletionDAWG from words100k (for large completion tests)
    dawg.CompletionDAWG(words).save(
        os.path.join(FIXTURES_DIR, "completion-large.dawg")
    )
    print("  completion-large.dawg")

    # 10. DAWG with Unicode keys
    unicode_keys = [
        "hello",
        "мир",
        "日本語",
        "café",
        "naïve",
        "ЁЖИК",
    ]
    dawg.DAWG(unicode_keys).save(os.path.join(FIXTURES_DIR, "unicode.dawg"))
    print("  unicode.dawg")

    # 11. CompletionDAWG for edge cases
    edge_keys = list("abcdefghijklmnopqrstuvwxyz")
    dawg.CompletionDAWG(edge_keys).save(
        os.path.join(FIXTURES_DIR, "single-chars.dawg")
    )
    print("  single-chars.dawg")

    long_keys = ["a" * 100, "b" * 200, "a" * 100 + "b"]
    dawg.CompletionDAWG(long_keys).save(os.path.join(FIXTURES_DIR, "long-keys.dawg"))
    print("  long-keys.dawg")

    prefix_keys = ["a", "ab", "abc", "abcd", "abcde"]
    dawg.CompletionDAWG(prefix_keys).save(
        os.path.join(FIXTURES_DIR, "shared-prefixes.dawg")
    )
    print("  shared-prefixes.dawg")

    print(f"\nAll fixtures generated in {os.path.abspath(FIXTURES_DIR)}")


if __name__ == "__main__":
    main()
