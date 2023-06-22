import dawg
from circuit_dawg import DAWG
import os
import pytest


class TestDAWG:
    @pytest.fixture(autouse=True, scope="function")
    def setup_class(self):
        # Build test dawgs using original dawg library
        dawg.DAWG(["f", "bar", "foo", "foobar"]).save("dawg.dawg")
        # Let tests run
        yield
        # Cleanup
        if os.path.exists("dawg.dawg"):
            try:
                os.remove("dawg.dawg")
            except OSError:
                pass


    def test_load(self):
        d = DAWG().load("dawg.dawg")
        assert d.dct.fp.skip != 0

    def test_bad_replaces(self):
        with pytest.raises(ValueError):
            DAWG.compile_replaces({"air": "bear", "bear": "air"})
