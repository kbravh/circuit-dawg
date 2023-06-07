import dawg
from circuit_dawg.wrapper import Dictionary
import pytest
import os
from .utils import words100k


class TestDictionary:
    path = "int.dawg"
    words = words100k()

    @pytest.fixture(autouse=True, scope="function")
    def setup_class(self):
        # Build test dawg using original dawg library
        values = [len(word) for word in self.words]
        dawg.IntDAWG(zip(self.words, values)).save(self.path)
        # Let tests run
        yield
        # Cleanup
        if os.path.exists(self.path):
            os.remove(self.path)

    def dic(self):
        return Dictionary().load(self.path)

    def test_contains(self):
        dictionary = self.dic()
        for word in self.words:
            assert dictionary.contains(word.encode('utf8'))

    def test_find(self):
        dictionary = self.dic()
        for word in self.words:
            assert dictionary.find(word.encode('utf8')) == len(word)

