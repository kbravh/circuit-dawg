import dawg
from circuit_dawg.wrapper import Dictionary
import pytest
import os
from .utils import words100k


class TestDictionary:
    path = "int.dawg"
    words = words100k()

    @pytest.fixture(autouse=True, scope="function", name="dictionary")
    def setup_class(self):
        # Build test dawg using original dawg library
        values = [len(word) for word in self.words]
        dawg.IntDAWG(zip(self.words, values)).save(self.path)
        # load our dictionary
        dictionary = Dictionary().load(self.path)
        # Let tests run
        yield dictionary
        # Cleanup
        if os.path.exists(self.path):
            try:
                os.remove(self.path)
            except OSError:
                pass

    def test_contains(self, dictionary):
        for word in self.words:
            assert dictionary.contains(word.encode("utf8"))

    def test_not_contains(self, dictionary):
        assert not dictionary.contains(b"x")

    def test_find(self, dictionary):
        for word in self.words:
            assert dictionary.find(word.encode("utf8")) == len(word)

    def test_not_find(self, dictionary):
        assert dictionary.find(b"x") == -1

    def test_unloaded_fp(self):
        dictionary = Dictionary()
        with pytest.raises(AssertionError):
            dictionary.find(b"x")

    def test_follow_nonexistent_char(self, dictionary):
        assert dictionary.follow_bytes(b"z", 5) is None
