# Circuit DAWG

This pure-python package provides read-only access for files
created by the [`dawgdic`](https://code.google.com/p/dawgdic/) C++ library and the [`DAWG`](https://github.com/kmike/DAWG) python package. It has been forked from [DAWG-Python](https://github.com/kmike/DAWG-Python) in order to provide support for Circuit Python.

This package is not capable of creating DAWGs. It works with DAWGs built by the [`dawgdic`](https://code.google.com/p/dawgdic/) C++ library or the [`DAWG`](https://github.com/kmike/DAWG) Python extension module. The main purpose of Circuit DAWG is to provide access to DAWGs on a microcontroller without requiring compiled extensions.

## Installation

Clone this repository, or install with pip:

```bash
pip install circuit_dawg
```

## Usage

The aim of `circuit-dawg` is to be API compatible with [`DAWG`](https://github.com/kmike/DAWG) when it is possible.

First, you have to create a dawg using [`DAWG`](https://github.com/kmike/DAWG) module:

    import dawg
    d = dawg.DAWG(data)
    d.save('words.dawg')

And then this dawg can be loaded without requiring C extensions:

    import circuit_dawg
    d = circuit_dawg.DAWG().load('words.dawg')

Please consult [`DAWG`](https://github.com/kmike/DAWG) docs for detailed usage. Some features
(like constructor parameters or `save()` method) are intentionally
unsupported.

## Changes from DAWG Python

Circuit Python has a subset of the functionality of a full Python distribution. There were some built-in array methods from Python used for loading in the DAWG files that aren't present in Circuit Python, so they needed to be re-written.

## Future Goals

### Interact with DAWGs from file without loading into memory

Since Circuit Python is run on microcontrollers, memory is a commodity in very short supply. Loading a large DAWG into memory in order to interact with it is entirely unfeasible. Thus, I plan to make modifications to allow the DAWG to be read directly from the binary file without needing to load it all in.

Contributions are welcome!


## Contributing

Check out the [source code](https://github.com/kbravh/circuit-dawg)
Submit an [issue or suggestion](https://github.com/kbravh/circuit-dawg/issues)

Feel free to submit ideas, bugs or pull requests.

# Authors & Contributors

- [kbravh](https://github.com/kbravh) - <karey.higuera@gmail.com>

Forked from [DAWG-Python](https://github.com/kmike/DAWG-Python) by Mikhail Korobov - <kmike84@gmail.com>

The algorithms are from [`dawgdic`](https://code.google.com/p/dawgdic/) C++ library by Susumu Yata & contributors.

# License

This package is licensed under MIT License.
