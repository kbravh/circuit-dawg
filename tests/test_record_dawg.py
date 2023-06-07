import pytest
from circuit_dawg import RecordDAWG
import os
import dawg


class TestRecordDAWG:
    DATA = (
        ("foo", (3, 2, 256)),
        ("bar", (3, 1, 0)),
        ("foo", (3, 2, 1)),
        ("foobar", (6, 3, 0)),
    )
    path = "record.dawg"

    @pytest.fixture(autouse=True, scope="function")
    def setup_class(self):
        # Build test dawg using original dawg library
        dawg.RecordDAWG(str(">3H"), self.DATA).save(self.path)
        # Let tests run
        yield
        # Cleanup
        if os.path.exists(self.path):
            os.remove(self.path)

    def dawg(self):
        return RecordDAWG(">3H").load(self.path)

    def test_getitem(self):
        d = self.dawg()
        assert d["foo"] == [(3, 2, 1), (3, 2, 256)]
        assert d["bar"] == [(3, 1, 0)]
        assert d["foobar"] == [(6, 3, 0)]

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

    def test_record_items(self):
        d = self.dawg()
        assert d.items() == sorted(self.DATA)

    def test_record_keys(self):
        d = self.dawg()
        assert d.keys() == [
            "bar",
            "foo",
            "foo",
            "foobar",
        ]

    def test_record_keys_prefix(self):
        d = self.dawg()
        assert d.keys("fo") == ["foo", "foo", "foobar"]
        assert d.keys("bar") == ["bar"]
        assert d.keys("barz") == []

    def test_prefixes(self):
        d = self.dawg()
        assert d.prefixes("foobarz") == ["foo", "foobar"]
        assert d.prefixes("x") == []
        assert d.prefixes("bar") == ["bar"]
