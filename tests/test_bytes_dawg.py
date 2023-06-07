import dawg
from circuit_dawg import BytesDAWG
import os
import pytest


class TestBytesDAWG:
    DATA = (
        ("foo", b"data1"),
        ("bar", b"data2"),
        ("foo", b"data3"),
        ("foobar", b"data4"),
    )

    @pytest.fixture(autouse=True, scope="function")
    def setup_class(self):
        # Build test dawg using original dawg library
        dawg.BytesDAWG(self.DATA).save("bytes.dawg")
        # Let tests run
        yield
        # Cleanup
        if os.path.exists("bytes.dawg"):
            os.remove("bytes.dawg")

    def dawg(self):
        return BytesDAWG().load("bytes.dawg")

    def test_contains(self):
        d = self.dawg()
        for key, _ in self.DATA:
            assert key in d

        assert "food" not in d
        assert "x" not in d
        assert "fo" not in d

    def test_getitem(self):
        d = self.dawg()

        assert d["foo"] == [b"data1", b"data3"]
        assert d["bar"] == [b"data2"]
        assert d["foobar"] == [b"data4"]

    def test_getitem_missing(self):
        d = self.dawg()

        with pytest.raises(KeyError):
            d["x"]

        with pytest.raises(KeyError):
            d["food"]

        with pytest.raises(KeyError):
            d["foobarz"]

        with pytest.raises(KeyError):
            d["f"]

    def test_keys(self):
        d = self.dawg()
        assert d.keys() == ["bar", "foo", "foo", "foobar"]

    def test_iterkeys(self):
        d = self.dawg()
        assert list(d.iterkeys()) == d.keys()

    def test_key_completion(self):
        d = self.dawg()
        assert d.keys("fo") == ["foo", "foo", "foobar"]

    def test_items(self):
        d = self.dawg()
        assert d.items() == sorted(self.DATA)

    def test_iteritems(self):
        d = self.dawg()
        assert list(d.iteritems("xxx")) == []
        assert list(d.iteritems("fo")) == d.items("fo")
        assert list(d.iteritems()) == d.items()

    def test_items_completion(self):
        d = self.dawg()
        assert d.items("foob") == [("foobar", b"data4")]

    def test_prefixes(self):
        d = self.dawg()
        assert d.prefixes("foobarz") == ["foo", "foobar"]
        assert d.prefixes("x") == []
        assert d.prefixes("bar") == ["bar"]
