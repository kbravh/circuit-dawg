import os

import pytest

from circuit_dawg.wrapper import FilePointer, Guide

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestGuide:
    @pytest.fixture(autouse=True, scope="function", name="guide")
    def setup(self):
        fp = FilePointer(open(os.path.join(FIXTURES_DIR, "int.dawg"), "rb"))
        guide = Guide()
        guide.fp = fp
        yield guide

    def test_close(self, guide):
        fp = guide.fp.fp
        guide.close()
        assert fp.closed
