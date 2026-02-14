import os

import pytest

from circuit_dawg import CompletionDAWG

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestCompletionDAWG:
    keys = ["f", "bar", "foo", "foobar"]

    def dawg(self):
        return CompletionDAWG().load(os.path.join(FIXTURES_DIR, "completion.dawg"))

    @pytest.mark.parametrize("key", keys)
    def test_contains(self, key):
        d = self.dawg()
        assert key in d

    def test_contains_bytes(self):
        d = self.dawg()
        for key in self.keys:
            assert key.encode("utf8") in d

    def test_keys(self):
        d = self.dawg()
        assert d.keys() == sorted(self.keys)

    def test_iterkeys(self):
        d = self.dawg()
        assert list(d.iterkeys()) == sorted(self.keys)

    def test_bad_iterkeys(self):
        d = self.dawg()
        d.iterkeys("8675309") == None

    def test_completion(self):
        d = self.dawg()

        assert d.keys("z") == []
        assert d.keys("b") == ["bar"]
        assert d.keys("foo") == ["foo", "foobar"]

    def test_prefixes(self):
        d = self.dawg()
        assert d.prefixes("foobarz") == ["f", "foo", "foobar"]
        assert d.prefixes("x") == []
        assert d.prefixes("bar") == ["bar"]

    def test_empty_dawg(self):
        d = CompletionDAWG().load(os.path.join(FIXTURES_DIR, "completion-empty.dawg"))
        assert d.keys() == []

    def test_unloaded_dawg(self):
        """Test that an error is raised when using a dawg before loading a file"""
        d = CompletionDAWG()
        with pytest.raises(AssertionError):
            d.keys()
