"""
Comprehensive parity tests comparing circuit_dawg against the dawg C library.

These tests require the `dawg` C extension to be installed.
Run with: pytest -m parity tests/test_parity.py
"""

import os
import tempfile

import dawg
import pytest

from circuit_dawg import (
    DAWG,
    BytesDAWG,
    CompletionDAWG,
    IntCompletionDAWG,
    IntDAWG,
    RecordDAWG,
)

from .utils import words100k

pytestmark = pytest.mark.parity


# ---------- helpers ----------


@pytest.fixture(scope="module")
def large_words():
    return words100k()


def _save_tmp(dawg_obj):
    """Save a dawg C-library object to a temp file and return the path."""
    fd, path = tempfile.mkstemp(suffix=".dawg")
    os.close(fd)
    dawg_obj.save(path)
    return path


# ---------- DAWG (basic membership) ----------


class TestDAWGParity:
    KEYS = ["f", "bar", "foo", "foobar"]

    @pytest.fixture(autouse=True)
    def setup(self):
        path = _save_tmp(dawg.DAWG(self.KEYS))
        self.d = DAWG().load(path)
        yield
        os.unlink(path)

    def test_contains(self):
        for key in self.KEYS:
            assert key in self.d

    def test_not_contains(self):
        for key in ["", "x", "fo", "ba", "food", "foobarz"]:
            assert key not in self.d

    def test_prefixes(self):
        assert self.d.prefixes("foobarz") == ["f", "foo", "foobar"]
        assert self.d.prefixes("x") == []
        assert self.d.prefixes("bar") == ["bar"]
        assert self.d.prefixes("f") == ["f"]

    def test_similar_keys(self):
        # similar_keys replaces source→target, not reverse
        # {"o": "0"} means: when we see "o" in the query, also try "0"
        # so it finds keys where "0" appears in place of "o"
        replaces = DAWG.compile_replaces({"o": "0"})
        assert self.d.similar_keys("foo", replaces) == ["foo"]
        assert self.d.similar_keys("xyz", replaces) == []
        # "bar" has no "o", so replaces don't apply
        assert self.d.similar_keys("bar", replaces) == ["bar"]


# ---------- DAWG with Unicode ----------


class TestDAWGUnicode:
    KEYS = [
        "hello",
        "мир",           # Cyrillic
        "日本語",         # CJK
        "café",          # accented Latin
        "naïve",
        "ЁЖИК",          # Cyrillic with Ё
    ]

    @pytest.fixture(autouse=True)
    def setup(self):
        path = _save_tmp(dawg.DAWG(self.KEYS))
        self.d = DAWG().load(path)
        yield
        os.unlink(path)

    def test_contains_unicode(self):
        for key in self.KEYS:
            assert key in self.d

    def test_not_contains_unicode(self):
        for key in ["hell", "мирr", "日本", "caff"]:
            assert key not in self.d

    def test_prefixes_unicode(self):
        # мир has no sub-prefixes in our set
        assert self.d.prefixes("мир") == ["мир"]
        assert self.d.prefixes("ЁЖИК") == ["ЁЖИК"]


# ---------- CompletionDAWG ----------


class TestCompletionDAWGParity:
    KEYS = ["f", "bar", "foo", "foobar"]

    @pytest.fixture(autouse=True)
    def setup(self):
        path = _save_tmp(dawg.CompletionDAWG(self.KEYS))
        self.d = CompletionDAWG().load(path)
        yield
        os.unlink(path)

    def test_contains(self):
        for key in self.KEYS:
            assert key in self.d

    def test_keys_no_prefix(self):
        assert self.d.keys() == sorted(self.KEYS)

    def test_keys_with_prefix(self):
        assert self.d.keys("foo") == ["foo", "foobar"]
        assert self.d.keys("b") == ["bar"]
        assert self.d.keys("z") == []

    def test_iterkeys_matches_keys(self):
        assert list(self.d.iterkeys()) == self.d.keys()
        assert list(self.d.iterkeys("foo")) == self.d.keys("foo")

    def test_prefixes(self):
        assert self.d.prefixes("foobarz") == ["f", "foo", "foobar"]


class TestCompletionDAWGEmpty:
    @pytest.fixture(autouse=True)
    def setup(self):
        path = _save_tmp(dawg.CompletionDAWG([]))
        self.d = CompletionDAWG().load(path)
        yield
        os.unlink(path)

    def test_empty_keys(self):
        assert self.d.keys() == []

    def test_empty_contains(self):
        assert "anything" not in self.d


# ---------- CompletionDAWG with large dataset ----------


class TestCompletionDAWGLarge:
    @pytest.fixture(autouse=True)
    def setup(self, large_words):
        self.words = large_words
        path = _save_tmp(dawg.CompletionDAWG(self.words))
        self.d = CompletionDAWG().load(path)
        yield
        os.unlink(path)

    def test_all_words_present(self):
        for word in self.words:
            assert word in self.d

    def test_keys_sorted(self):
        # CompletionDAWG deduplicates keys
        assert self.d.keys() == sorted(set(self.words))

    def test_iterkeys_equals_keys(self):
        assert list(self.d.iterkeys()) == self.d.keys()

    def test_prefix_completion(self):
        prefix = "abai"
        expected = sorted([w for w in self.words if w.startswith(prefix)])
        assert self.d.keys(prefix) == expected


# ---------- BytesDAWG ----------


class TestBytesDAWGParity:
    DATA = [
        ("foo", b"data1"),
        ("bar", b"data2"),
        ("foo", b"data3"),
        ("foobar", b"data4"),
    ]

    @pytest.fixture(autouse=True)
    def setup(self):
        path = _save_tmp(dawg.BytesDAWG(self.DATA))
        self.d = BytesDAWG().load(path)
        yield
        os.unlink(path)

    def test_contains(self):
        for key, _ in self.DATA:
            assert key in self.d
        assert "missing" not in self.d

    def test_getitem(self):
        assert self.d["foo"] == [b"data1", b"data3"]
        assert self.d["bar"] == [b"data2"]
        assert self.d["foobar"] == [b"data4"]

    def test_getitem_missing(self):
        with pytest.raises(KeyError):
            self.d["missing"]

    def test_keys(self):
        assert self.d.keys() == ["bar", "foo", "foo", "foobar"]

    def test_keys_prefix(self):
        assert self.d.keys("fo") == ["foo", "foo", "foobar"]

    def test_iterkeys(self):
        assert list(self.d.iterkeys()) == self.d.keys()

    def test_items(self):
        assert self.d.items() == sorted(self.DATA)

    def test_iteritems(self):
        assert list(self.d.iteritems()) == self.d.items()
        assert list(self.d.iteritems("fo")) == self.d.items("fo")

    def test_prefixes(self):
        assert self.d.prefixes("foobarz") == ["foo", "foobar"]
        assert self.d.prefixes("x") == []


# ---------- RecordDAWG ----------


class TestRecordDAWGParity:
    DATA = [
        ("foo", (3, 2, 256)),
        ("bar", (3, 1, 0)),
        ("foo", (3, 2, 1)),
        ("foobar", (6, 3, 0)),
    ]

    @pytest.fixture(autouse=True)
    def setup(self):
        path = _save_tmp(dawg.RecordDAWG(str(">3H"), self.DATA))
        self.d = RecordDAWG(">3H").load(path)
        yield
        os.unlink(path)

    def test_getitem(self):
        assert self.d["foo"] == [(3, 2, 1), (3, 2, 256)]
        assert self.d["bar"] == [(3, 1, 0)]
        assert self.d["foobar"] == [(6, 3, 0)]

    def test_getitem_missing(self):
        with pytest.raises(KeyError):
            self.d["missing"]

    def test_keys(self):
        assert self.d.keys() == ["bar", "foo", "foo", "foobar"]

    def test_keys_prefix(self):
        assert self.d.keys("fo") == ["foo", "foo", "foobar"]

    def test_items(self):
        assert self.d.items() == sorted(self.DATA)

    def test_iteritems(self):
        assert list(self.d.iteritems()) == self.d.items()

    def test_prefixes(self):
        assert self.d.prefixes("foobarz") == ["foo", "foobar"]


# ---------- RecordDAWG with prediction (Cyrillic) ----------


class TestRecordDAWGPrediction:
    REPLACES = DAWG.compile_replaces({"Е": "Ё"})

    WORDS = [
        "ЁЖИК", "ЁЖИКЕ", "ЁЖ", "ДЕРЕВНЯ", "ДЕРЁВНЯ",
        "ЕМ", "ОЗЕРА", "ОЗЁРА", "ОЗЕРО",
    ]

    SUITE = [
        ("УЖ", []),
        ("ЕМ", ["ЕМ"]),
        ("ЁМ", []),
        ("ЁЖ", ["ЁЖ"]),
        ("ЕЖ", ["ЁЖ"]),
        ("ЁЖИК", ["ЁЖИК"]),
        ("ЕЖИКЕ", ["ЁЖИКЕ"]),
        ("ДЕРЕВНЯ", ["ДЕРЕВНЯ", "ДЕРЁВНЯ"]),
        ("ДЕРЁВНЯ", ["ДЕРЁВНЯ"]),
        ("ОЗЕРА", ["ОЗЕРА", "ОЗЁРА"]),
        ("ОЗЕРО", ["ОЗЕРО"]),
    ]

    @pytest.fixture(autouse=True)
    def setup(self):
        data = [(k, (len(k),)) for k in self.WORDS]
        path = _save_tmp(dawg.RecordDAWG(str("=H"), data))
        self.d = RecordDAWG(str("=H")).load(path)
        yield
        os.unlink(path)

    @pytest.mark.parametrize(("word", "expected"), SUITE)
    def test_similar_keys(self, word, expected):
        assert self.d.similar_keys(word, self.REPLACES) == expected

    @pytest.mark.parametrize(("word", "expected"), SUITE)
    def test_similar_items(self, word, expected):
        expected_items = [(w, [(len(w),)]) for w in expected]
        assert self.d.similar_items(word, self.REPLACES) == expected_items

    @pytest.mark.parametrize(("word", "expected"), SUITE)
    def test_similar_item_values(self, word, expected):
        expected_values = [[(len(w),)] for w in expected]
        assert self.d.similar_item_values(word, self.REPLACES) == expected_values


# ---------- IntDAWG ----------


class TestIntDAWGParity:
    PAYLOAD = {"foo": 1, "bar": 5, "foobar": 3}

    @pytest.fixture(autouse=True)
    def setup(self):
        path = _save_tmp(dawg.IntDAWG(self.PAYLOAD.items()))
        self.d = IntDAWG().load(path)
        yield
        os.unlink(path)

    def test_getitem(self):
        for key, val in self.PAYLOAD.items():
            assert self.d[key] == val

    def test_getitem_missing(self):
        with pytest.raises(KeyError):
            self.d["missing"]

    def test_get_default(self):
        assert self.d.get("missing") is None
        assert self.d.get("missing", 42) == 42

    def test_contains(self):
        for key in self.PAYLOAD:
            assert key in self.d
        assert "missing" not in self.d


class TestIntDAWGLarge:
    @pytest.fixture(autouse=True)
    def setup(self, large_words):
        self.words = large_words
        values = [len(w) for w in self.words]
        path = _save_tmp(dawg.IntDAWG(zip(self.words, values)))
        self.d = IntDAWG().load(path)
        yield
        os.unlink(path)

    def test_all_words_found(self):
        for word in self.words:
            assert self.d[word] == len(word)

    def test_contains_all(self):
        for word in self.words:
            assert word in self.d

    def test_not_contains(self):
        assert "xyzzy_not_a_word" not in self.d


# ---------- IntCompletionDAWG ----------


class TestIntCompletionDAWGParity:
    PAYLOAD = {"foo": 1, "bar": 5, "foobar": 3}

    @pytest.fixture(autouse=True)
    def setup(self):
        path = _save_tmp(dawg.IntCompletionDAWG(self.PAYLOAD.items()))
        self.d = IntCompletionDAWG().load(path)
        yield
        os.unlink(path)

    def test_getitem(self):
        for key, val in self.PAYLOAD.items():
            assert self.d[key] == val

    def test_getitem_missing(self):
        with pytest.raises(KeyError):
            self.d["missing"]

    def test_keys(self):
        assert self.d.keys() == sorted(self.PAYLOAD.keys())

    def test_keys_prefix(self):
        assert self.d.keys("fo") == ["foo", "foobar"]
        assert self.d.keys("b") == ["bar"]
        assert self.d.keys("z") == []

    def test_items(self):
        assert self.d.items() == sorted(self.PAYLOAD.items(), key=lambda r: r[0])

    def test_iteritems(self):
        assert list(self.d.iteritems()) == self.d.items()

    def test_contains(self):
        for key in self.PAYLOAD:
            assert key in self.d


# ---------- Edge cases ----------


class TestEdgeCases:
    def test_single_char_keys(self):
        keys = list("abcdefghijklmnopqrstuvwxyz")
        path = _save_tmp(dawg.CompletionDAWG(keys))
        d = CompletionDAWG().load(path)
        assert d.keys() == sorted(keys)
        for k in keys:
            assert k in d
        os.unlink(path)

    def test_long_keys(self):
        keys = ["a" * 100, "b" * 200, "a" * 100 + "b"]
        path = _save_tmp(dawg.CompletionDAWG(keys))
        d = CompletionDAWG().load(path)
        assert d.keys() == sorted(keys)
        os.unlink(path)

    def test_keys_sharing_prefixes(self):
        keys = ["a", "ab", "abc", "abcd", "abcde"]
        path = _save_tmp(dawg.CompletionDAWG(keys))
        d = CompletionDAWG().load(path)
        assert d.keys() == keys
        assert d.prefixes("abcde") == keys
        os.unlink(path)
