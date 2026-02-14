# Circuit DAWG

This pure-python package provides read-only access for files
created by the [`dawgdic`](https://code.google.com/p/dawgdic/) C++ library and the [`DAWG`](https://github.com/kmike/DAWG) python package. It has been forked from [DAWG-Python](https://github.com/kmike/DAWG-Python) in order to provide support for Circuit Python.

This package is not capable of creating DAWGs. It works with DAWGs built by the [`dawgdic`](https://code.google.com/p/dawgdic/) C++ library or the [`DAWG`](https://github.com/kmike/DAWG) Python extension module. The main purpose of Circuit DAWG is to provide access to DAWGs on a microcontroller without requiring compiled extensions.

## Installation

Download the latest release from [GitHub Releases](https://github.com/kbravh/circuit-dawg/releases).

Each release includes three zip files:

- `circuit-dawg-X.Y.Z-py.zip` — raw `.py` source files (works on any CircuitPython board)
- `circuit-dawg-X.Y.Z-9.x-mpy.zip` — compiled `.mpy` files for CircuitPython 9.x
- `circuit-dawg-X.Y.Z-10.x-mpy.zip` — compiled `.mpy` files for CircuitPython 10.x

Using `.mpy` files is recommended as they use less memory and load faster. Choose the zip that matches your CircuitPython version.

### CircuitPython install steps

1. Download the appropriate zip for your board
2. Extract the zip — it contains a `circuit_dawg/` directory
3. Copy the `circuit_dawg/` directory to the `lib/` folder on your CIRCUITPY drive

Your drive should look like this:

```
CIRCUITPY/
├── lib/
│   └── circuit_dawg/
│       ├── __init__.py  (or .mpy)
│       ├── dawgs.py
│       ├── units.py
│       └── wrapper.py
├── code.py
└── words.dawg
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

## Memory Usage

Circuit DAWG is designed for memory-constrained microcontrollers. The library reads directly from files using seek/read operations, so **DAWG file size does not determine RAM usage** — even large DAWG files use minimal memory.

The numbers below were measured on CPython using `tracemalloc`. MicroPython typically uses less memory than CPython for equivalent operations.

### Library overhead

| Operation | Peak memory |
|-----------|------------|
| Load a DAWG | ~6 KB |
| Load a CompletionDAWG | ~6 KB |
| Load a BytesDAWG | ~6 KB |

### Per-operation costs

| Operation | Memory |
|-----------|--------|
| `__contains__` / lookup | < 1 KB |
| `get()` | < 1 KB |
| `keys()` / `iterkeys()` | < 1 KB (scales with result count) |

### Board compatibility

| Board class | Available RAM | Suitability |
|-------------|--------------|-------------|
| SAMD21 (e.g. Trinket M0) | ~32 KB | Basic lookups only, small DAWGs |
| SAMD51 (e.g. Feather M4) | ~192 KB | Comfortable for most operations |
| RP2040 (e.g. Pico) | ~160 KB after boot | Comfortable for most operations |
| ESP32-S2/S3 | 2 MB+ PSRAM | Large DAWGs, bulk completions |

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
