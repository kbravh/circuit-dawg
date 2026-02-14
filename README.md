# Circuit DAWG

This pure-python package provides read-only access for files
created by the [`dawgdic`](https://code.google.com/p/dawgdic/) C++ library and the [`DAWG`](https://github.com/kmike/DAWG) python package. It has been forked from [DAWG-Python](https://github.com/kmike/DAWG-Python) in order to provide support for Circuit Python.

This package is not capable of creating DAWGs. It works with DAWGs built by the [`dawgdic`](https://code.google.com/p/dawgdic/) C++ library or the [`DAWG`](https://github.com/kmike/DAWG) Python extension module. The main purpose of Circuit DAWG is to provide access to DAWGs on a microcontroller without requiring compiled extensions.

## Installation

Install with pip:

```bash
pip install circuit-dawg
```

Or with uv:

```bash
uv add circuit-dawg
```

## Usage

The aim of `circuit-dawg` is to be API compatible with [`DAWG`](https://github.com/kmike/DAWG) when it is possible.

First, you have to create a dawg using [`DAWG`](https://github.com/kmike/DAWG) module:

```python
import dawg
d = dawg.DAWG(data)
d.save('words.dawg')
```

And then this dawg can be loaded without requiring C extensions:

```python
import circuit_dawg
d = circuit_dawg.DAWG().load('words.dawg')
```

All DAWG types support context managers for automatic cleanup:

```python
with circuit_dawg.CompletionDAWG().load('words.dawg') as d:
    print(d.keys('hello'))
# file handle is automatically closed
```

Please consult [`DAWG`](https://github.com/kmike/DAWG) docs for detailed usage. Some features
(like constructor parameters or `save()` method) are intentionally
unsupported.

## Features

### File-based reading

Circuit DAWG reads DAWG data directly from files using seek and read operations, without loading the entire file into memory. This makes it suitable for memory-constrained environments like CircuitPython on microcontrollers.

## Contributing

Check out the [source code](https://github.com/kbravh/circuit-dawg)
Submit an [issue or suggestion](https://github.com/kbravh/circuit-dawg/issues)

Feel free to submit ideas, bugs or pull requests.

### Local development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest --cov=circuit_dawg tests/

# Lint
uv run ruff check circuit_dawg/
```

# Authors & Contributors

- [kbravh](https://github.com/kbravh) - <karey.higuera@gmail.com>

Forked from [DAWG-Python](https://github.com/kmike/DAWG-Python) by Mikhail Korobov - <kmike84@gmail.com>

The algorithms are from [`dawgdic`](https://code.google.com/p/dawgdic/) C++ library by Susumu Yata & contributors.

# License

This package is licensed under MIT License.
