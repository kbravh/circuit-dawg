# DAWG-Python

This pure-python package provides read-only access for files
created by [`dawgdic`](https://code.google.com/p/dawgdic/) C++ library and [`DAWG`](https://github.com/kmike/DAWG) python package.

This package is not capable of creating DAWGs. It works with DAWGs built by
[`dawgdic`](https://code.google.com/p/dawgdic/) C++ library or [`DAWG`](https://github.com/kmike/DAWG) Python extension module. The main purpose
of DAWG-Python is to provide an access to DAWGs without requiring compiled
extensions. It is also quite fast under PyPy (see benchmarks).

## Installation

pip install DAWG-Python

## Usage

The aim of `circuit-dawg` is to be API- and binary-compatible with [`DAWG`](https://github.com/kmike/DAWG) when it is possible.

First, you have to create a dawg using [`DAWG`](https://github.com/kmike/DAWG) module::

    import dawg
    d = dawg.DAWG(data)
    d.save('words.dawg')

And then this dawg can be loaded without requiring C extensions::

    import circuit_dawg
    d = circuit_dawg.DAWG().load('words.dawg')

Please consult [`DAWG`](https://github.com/kmike/DAWG) docs for detailed usage. Some features
(like constructor parameters or `save()` method) are intentionally
unsupported.

## Current limitations

* This package is not capable of creating DAWGs
* all the limitations of [`DAWG`](https://github.com/kmike/DAWG) apply

Contributions are welcome!


## Contributing

Check out the [source code](https://github.com/kbravh/circuit-dawg)
Submit an [issue or suggestion](https://github.com/kbravh/circuit-dawg/issues)

Feel free to submit ideas, bugs or pull requests.

# Authors & Contributors

- [kbravh](https://github.com/kbravh) <karey.higuera@gmail.com>

Forked from [DAWG-Python](https://github.com/kmike/DAWG-Python) by Mikhail Korobov <kmike84@gmail.com>

The algorithms are from [`dawgdic`](https://code.google.com/p/dawgdic/) C++ library by Susumu Yata & contributors.

# License

This package is licensed under MIT License.
