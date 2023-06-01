import circuit_dawg

dictionary = circuit_dawg.DAWG().load('tests/small_dict.dawg')

def test_contains():
  assert 'cat' in dictionary
  assert 'cañon' in dictionary
  assert 'cancer' in dictionary
  assert 'car' in dictionary

def test_notcontains():
  assert not 'cable' in dictionary
