import dawg
from circuit_dawg.wrapper import FilePointer, Guide
import pytest
import os
from .utils import words100k


class TestGuide:
    path = "int.dawg"
    words = words100k()

    @pytest.fixture(autouse=True, scope="function", name="guide")
    def setup_class(self):
        # Build test dawg using original dawg library
        values = [len(word) for word in self.words]
        dawg.IntDAWG(zip(self.words, values)).save(self.path)
        # load our guide
        fp = FilePointer(open(self.path, "rb"))
        guide = Guide()
        guide.fp = fp
        # Let tests run
        yield guide
        # Cleanup
        if os.path.exists(self.path):
            try:
                os.remove(self.path)
            except OSError:
                pass

    def test_close(self, guide):
        fp = guide.fp.fp
        guide.close()
        assert fp.closed
