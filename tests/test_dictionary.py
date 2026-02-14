import os

import pytest

from circuit_dawg.wrapper import Dictionary

from .utils import words100k

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestDictionary:
    words = words100k()

    @pytest.fixture(autouse=True, scope="function", name="dictionary")
    def setup(self):
        dictionary = Dictionary().load(os.path.join(FIXTURES_DIR, "int.dawg"))
        yield dictionary

    def test_contains(self, dictionary):
        """Test that all words are contained in the dictionary"""
        for word in self.words:
            assert dictionary.contains(word.encode("utf8"))

    def test_not_contains(self, dictionary):
        """Test that a word not in the dictionary is not contained in the dictionary"""
        assert dictionary.contains(b"xylophone") == False

    def test_find(self, dictionary):
        """Test the find method for word retrieval"""
        for word in self.words:
            assert dictionary.find(word.encode("utf8")) == len(word)

    def test_not_find(self, dictionary):
        """Test that the find method returns -1 for a word not in the dictionary"""
        assert dictionary.find(b"x") == -1

    def test_unloaded_fp(self):
        """Test that an assertion error is raised when trying to use an unloaded dictionary"""
        dictionary = Dictionary()
        with pytest.raises(AssertionError):
            dictionary.find(b"x")

    def test_follow_nonexistent_char(self, dictionary):
        """Test that None is returned when following a nonexistent character"""
        assert dictionary.follow_bytes(b"z", 5) is None

    def test_close(self, dictionary):
        """Test that the underlying file pointer is closed when the dictionary is closed"""
        fp = dictionary.fp.fp
        dictionary.close()
        assert fp.closed
