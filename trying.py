import circuit_dawg

dictionary = circuit_dawg.DAWG().load("tests/small_dict.dawg")
completion = circuit_dawg.CompletionDAWG().load("tests/small_dict.dawg")

print(completion.keys("ca"))
