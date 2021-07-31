import circuit_dawg

from .utils import words100k, data_path

words = words100k()
dawg = circuit_dawg.Dictionary.load(data_path('large', 'int_dawg.dawg'))

class TestDictionary(object):

    def test_contains(self):
        for word in words:
            assert dawg.contains(word.encode('utf8'))

    def test_find(self):
        for word in words:
            assert dawg.find(word.encode('utf8')) == len(word)
