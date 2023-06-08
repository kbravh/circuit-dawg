import dawg
from circuit_dawg import CompletionDAWG
import os
import pytest


class TestCompletionDAWG:
    keys = ["f", "bar", "foo", "foobar"]
    test_files = ["completion.dawg", "completion-empty.dawg"]

    @pytest.fixture(autouse=True, scope="function")
    def setup_class(self):
        # Build test dawgs using original dawg library
        dawg.CompletionDAWG(self.keys).save(self.test_files[0])
        dawg.CompletionDAWG([]).save(self.test_files[1])
        # Let tests run
        yield
        # Cleanup
        for f in self.test_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except PermissionError:
                    pass

    @pytest.mark.parametrize("key", keys)
    def test_contains(self, key):
        d = CompletionDAWG().load(self.test_files[0])
        assert key in d

    def test_contains_bytes(self):
        d = CompletionDAWG().load(self.test_files[0])
        for key in self.keys:
            assert key.encode("utf8") in d

    def test_keys(self):
        d = CompletionDAWG().load(self.test_files[0])
        assert d.keys() == sorted(self.keys)

    def test_iterkeys(self):
        d = CompletionDAWG().load(self.test_files[0])
        assert list(d.iterkeys()) == sorted(self.keys)

    def test_bad_iterkeys(self):
        d = CompletionDAWG().load(self.test_files[0])
        d.iterkeys("8675309") == None

    def test_completion(self):
        d = CompletionDAWG().load(self.test_files[0])

        assert d.keys("z") == []
        assert d.keys("b") == ["bar"]
        assert d.keys("foo") == ["foo", "foobar"]

    def test_prefixes(self):
        d = CompletionDAWG().load(self.test_files[0])
        assert d.prefixes("foobarz") == ["f", "foo", "foobar"]
        assert d.prefixes("x") == []
        assert d.prefixes("bar") == ["bar"]

    def test_empty_dawg(self):
        d = CompletionDAWG().load(self.test_files[1])
        assert d.keys() == []

    def test_unloaded_dawg(self):
        """Test that an error is raised when using a dawg before loading a file"""
        d = CompletionDAWG()
        with pytest.raises(AssertionError):
            d.keys()
