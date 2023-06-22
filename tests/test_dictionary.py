import dawg
from circuit_dawg.wrapper import Dictionary
import pytest
import os
from .utils import words100k
from unittest.mock import MagicMock


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
