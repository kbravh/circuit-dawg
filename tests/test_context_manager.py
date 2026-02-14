import os

from circuit_dawg import DAWG, BytesDAWG, CompletionDAWG, IntDAWG, RecordDAWG

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestContextManager:
    def test_dawg_context_manager(self):
        with DAWG().load(os.path.join(FIXTURES_DIR, "dawg.dawg")) as d:
            assert "foo" in d
        assert d.dct is None

    def test_completion_dawg_context_manager(self):
        with CompletionDAWG().load(os.path.join(FIXTURES_DIR, "completion.dawg")) as d:
            assert d.keys() == ["bar", "f", "foo", "foobar"]
        assert d.dct is None
        assert d.guide is None

    def test_bytes_dawg_context_manager(self):
        with BytesDAWG().load(os.path.join(FIXTURES_DIR, "bytes.dawg")) as d:
            assert d["foo"] == [b"data1", b"data3"]
        assert d.dct is None

    def test_record_dawg_context_manager(self):
        with RecordDAWG(">3H").load(os.path.join(FIXTURES_DIR, "record.dawg")) as d:
            assert d["bar"] == [(3, 1, 0)]
        assert d.dct is None

    def test_int_dawg_context_manager(self):
        with IntDAWG().load(os.path.join(FIXTURES_DIR, "dawg.dawg")) as d:
            assert "foo" in d
        assert d.dct is None
