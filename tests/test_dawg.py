import os

import pytest

from circuit_dawg import DAWG

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestDAWG:
    def test_load(self):
        d = DAWG().load(os.path.join(FIXTURES_DIR, "dawg.dawg"))
        assert d.dct.fp.skip != 0

    def test_bad_replaces(self):
        with pytest.raises(ValueError):
            DAWG.compile_replaces({"air": "bear", "bear": "air"})
