import pytest
from circuit_dawg import DAWG, RecordDAWG
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

    @pytest.fixture(autouse=True, scope="function", name="record_dawg")
    def setup_class(self):
        # Build test dawg using original dawg library
        dawg.RecordDAWG(str(">3H"), self.DATA).save(self.path)
        # load test dawg using our wrapper
        record_dawg = RecordDAWG(">3H").load(self.path)
        # Let tests run
        yield record_dawg
        # Cleanup
        if os.path.exists(self.path):
            try:
              os.remove(self.path)
            except PermissionError:
              pass

    def test_getitem(self, record_dawg):
        assert record_dawg["foo"] == [(3, 2, 1), (3, 2, 256)]
        assert record_dawg["bar"] == [(3, 1, 0)]
        assert record_dawg["foobar"] == [(6, 3, 0)]

    def test_getitem_missing(self, record_dawg):

        with pytest.raises(KeyError):
            record_dawg["x"]

        with pytest.raises(KeyError):
            record_dawg["food"]

        with pytest.raises(KeyError):
            record_dawg["foobarz"]

        with pytest.raises(KeyError):
            record_dawg["f"]

    def test_record_items(self, record_dawg):
        assert record_dawg.items() == sorted(self.DATA)

    def test_record_keys(self, record_dawg):
        assert record_dawg.keys() == [
            "bar",
            "foo",
            "foo",
            "foobar",
        ]

    def test_record_keys_prefix(self, record_dawg):
        assert record_dawg.keys("fo") == ["foo", "foo", "foobar"]
        assert record_dawg.keys("bar") == ["bar"]
        assert record_dawg.keys("barz") == []

    def test_prefixes(self, record_dawg):
        assert record_dawg.prefixes("foobarz") == ["foo", "foobar"]
        assert record_dawg.prefixes("x") == []
        assert record_dawg.prefixes("bar") == ["bar"]


class TestPredictionRecordDAWG:
    path = "prediction-record.dawg"

    REPLACES = DAWG.compile_replaces({"Е": "Ё"})

    DATA = [
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

    SUITE_ITEMS = [
        (it[0], [(w, [(len(w),)]) for w in it[1]])  # key  # item, value pair
        for it in SUITE
    ]

    SUITE_VALUES = [(it[0], [[(len(w),)] for w in it[1]]) for it in SUITE]  # key

    @pytest.fixture(autouse=True, scope="function", name="record_dawg")
    def setup_class(self):
        # Build test dawg using original dawg library
        dawg.RecordDAWG(str("=H"), [(k, (len(k),)) for k in self.DATA]).save(self.path)
        # load test dawg using our wrapper
        record_dawg = RecordDAWG(str("=H")).load(self.path)
        # Let tests run
        yield record_dawg
        # Cleanup
        if os.path.exists(self.path):
            try:
              os.remove(self.path)
            except PermissionError:
              pass

    @pytest.mark.parametrize(("word", "prediction"), SUITE)
    def test_record_dawg_prediction(self, word, prediction, record_dawg):
        assert record_dawg.similar_keys(word, self.REPLACES) == prediction

    @pytest.mark.parametrize(("word", "prediction"), SUITE_ITEMS)
    def test_record_dawg_items(self, word, prediction, record_dawg):
        assert record_dawg.similar_items(word, self.REPLACES) == prediction

    @pytest.mark.parametrize(("word", "prediction"), SUITE_VALUES)
    def test_record_dawg_items_values(self, word, prediction, record_dawg):
        assert record_dawg.similar_item_values(word, self.REPLACES) == prediction
