# Circuit DAWG migration status and plan

## Current status at a glance

- The core library already reads DAWG data directly from files and avoids loading full structures into memory.
  - `Dictionary` and `Guide` access data via a shared `FilePointer` that seeks and reads on demand from the `.dawg` file.
  - `CompletionDAWG`, `BytesDAWG`, `RecordDAWG`, and `Int*` classes operate on top of these file-backed primitives.
- Test status in this environment:
  - `tests/test_filepointer.py`: PASS (6 tests)
  - Most other tests require the compiled `DAWG` package to generate `.dawg` files at runtime; building it failed here. The repo includes several prebuilt `.dawg` fixtures that can be leveraged to run tests without the C extension.

## Repository components relevant to file-backed I/O

- `circuit_dawg/wrapper.py`
  - `FilePointer`: wraps a file-like object, reads base sizes, and offsets all seeks by a logical “skip” region.
  - `Dictionary`: exposes `contains`, `find`, `follow_char`, `follow_bytes`, `has_value`, and `value` by reading 32-bit units directly from the file.
  - `Guide`: reads 2-byte per-node navigation data (child and sibling labels) from the file; also uses `FilePointer` for on-demand access.
  - `Completer`: performs traversal using `Dictionary` and `Guide` without preloading the structure.
- `circuit_dawg/dawgs.py`
  - High-level DAWG types: `DAWG`, `CompletionDAWG`, `BytesDAWG`, `RecordDAWG`, `IntDAWG`, `IntCompletionDAWG`.
  - `CompletionDAWG.load(path)` opens the file once and wires a single file handle into both `Dictionary` and `Guide` via two `FilePointer` views (with different skips).
- `circuit_dawg/units.py`
  - Bitfield helpers to interpret 32-bit DAWG units (offset, label, leaf/value flags) used by `Dictionary`.

## DAWG file structure used here

A `.dawg` file is laid out as contiguous binary sections. This library reads them in-place via seeks and small reads.

- 4 bytes at file start: number of 32-bit `Dictionary` units (called `base_size`). Read with `struct.unpack("=I", ...)`.
- `Dictionary` units: `base_size * 4` bytes, each unit a 32-bit unsigned integer.
- `Guide` units: `base_size * 2` bytes, conceptually two 1-byte labels per node: `child` then `sibling`.

This is reflected in `CompletionDAWG.load`:

```python
# dictionary at file start; guide follows it
self.dct.read(fp, path)
self.guide.read(fp, path, 4 + self.dct.fp.base_size * 4)
```

### Interpreting 32-bit dictionary units

`circuit_dawg/units.py` defines masks and helpers for decoding each 32-bit unit:

- `IS_LEAF_BIT = 1 << 31`
- `HAS_LEAF_BIT = 1 << 8`
- `EXTENSION_BIT = 1 << 9`
- `PRECISION_MASK = 0xFFFFFFFF`

Functions:

- `has_leaf(base) -> bool`: whether a node has a terminal edge (end of key).
- `value(base) -> int`: returns the value from a leaf unit (top bit masked off).
- `label(base) -> int`: returns the transition label byte from a non-leaf unit (low 8 bits; top bit may be set for leaf information but is not used when comparing to byte labels).
- `offset(base) -> int`: computes the child offset. Specifically: `((base >> 10) << ((base & EXTENSION_BIT) >> 6)) & PRECISION_MASK`.
  - In practice this derives the base address for transitions; the extra shift controlled by `EXTENSION_BIT` extends the range for larger automata.

`Dictionary` uses these as follows (pseudocode):

```python
# has_value(index)
seek(index * 4); base = unpack('I'); return has_leaf(base)

# value(index)
seek(index * 4); base = unpack('I'); value_index = (index ^ offset(base)) & PRECISION_MASK
seek(value_index * 4); return value(unpack('I'))

# follow_char(label, index)
seek(index * 4); base = unpack('I'); next_index = (index ^ offset(base) ^ label) & PRECISION_MASK
seek(next_index * 4); return next_index if label(unpack('I')) == label else None
```

### Guide section

The `Guide` provides fast traversal during completion:

- `child(i)`: read 1 byte at offset `i * 2`.
- `sibling(i)`: read 1 byte at offset `i * 2 + 1`.
- Total size is `base_size * 2` bytes. The `Completer` uses `child/sibling` to perform DFS-like enumeration without materializing the graph.

### BytesDAWG and encoded payloads

For `BytesDAWG`, payloads are encoded within keys using a byte separator `b"\x01"` followed by base64-encoded data. Retrieval pattern:

- Traverse key bytes to an index.
- Follow the payload separator as a transition.
- Enumerate completions and base64-decode each terminal suffix to produce `bytes` payloads.

`RecordDAWG` wraps `BytesDAWG`, decoding each payload with a Python struct format.

### Structs for record payloads

- `RecordDAWG(fmt)` constructs `self._struct = struct.Struct(str(fmt))`.
  - Example: `">3H"` means big-endian, 3 unsigned 16-bit integers.
- Values are produced by `self._struct.unpack(...)` over each payload emitted by `BytesDAWG`.

Note on endianness: the dictionary/guide integers are read with native endianness in a few places (`"I"`). `base_size` is explicitly read with `"=I"` (native, standard size). If cross-platform, stable endianness is required, prefer changing all integer reads to `"=I"` for consistency.

## What’s already microcontroller-friendly

- Access pattern is streaming/seeking with 4–8 byte reads. No arrays or large buffers are loaded.
- A single OS file handle is shared across `Dictionary` and `Guide` via two `FilePointer` views.
- Iteration APIs (`iterkeys`, `iteritems`) are generator-based and avoid large materializations.
- Explicit `close()` is available for `Dictionary`, `Guide`, and `CompletionDAWG` to release the handle early.

## Gaps and proposed changes for CircuitPython readiness

1. Eliminate the test-time dependency on compiled `DAWG` by using prebuilt fixtures.
   - The repo already includes `dictionary.dawg`, `record.dawg`, and `prediction-record.dawg` in the project root. Update tests to use these fixtures instead of building new files with `dawg.*.save(...)`.
   - Alternatively, add a tiny helper script (run on CP-incompatible environments only) to pre-generate fixtures into `tests/fixtures/` and commit them.
2. Ensure `struct` use is CircuitPython-compatible.
   - CircuitPython supports `struct` but be explicit with formats (`"=I"`, `"=B"`) to avoid alignment/endianness surprises.
   - Audit `wrapper.Dictionary` to use `"=I"` in all 32-bit reads for consistency.
3. Add generator-based variants to reduce transient list allocations:
   - `BytesDAWG.iteritems_values()`/`iter_values()` to yield payloads lazily.
   - `RecordDAWG` equivalents yielding unpacked tuples incrementally.
   - Keep current list-returning APIs for compatibility; implement them on top of the iterators.
4. File lifecycle/robustness improvements:
   - Avoid `__del__` for critical cleanup; rely on explicit `close()` and context managers. Add `__enter__/__exit__` to `Dictionary`/`Guide`/DAWG types so `with` works on CP.
   - Validate that both `Dictionary` and `Guide` share the same underlying `fp` and that closing one does not invalidate the other prematurely. Today `CompletionDAWG.close()` calls both; that is fine when used as a unit.
5. Optional: micro-optimizations helpful on CP
   - Replace repeated `struct.unpack("I", data)[0]` with a pre-bound unpacker: `UNPACK_I = struct.Struct("=I").unpack_from` and reuse a scratch buffer to minimize allocations.
   - Inline small hot-path helpers to reduce call overhead.
   - Consider a small read-through cache for `Dictionary` units (e.g., last N indices) if profiling shows benefit without significant RAM footprint.

## Testing strategy in low-memory environments

- Host-based low-memory simulation:
  - Run CP interpreter locally (CircuitPython or MicroPython) and execute a reduced test suite that uses the prebuilt fixtures. This is the best fidelity.
  - Add CI job that runs `pytest -k "filepointer or dictionary or guide or completion or bytes or record"` under `micropython-cpy-test` or `adafruit-circuitpython` runner where possible.
- Python-on-host stress tests:
  - Monkeypatch `FilePointer.read/seek` to track read sizes and counts; assert no large reads are performed and I/O remains small and proportional to query.
  - Add tests using the included fixtures that call `iter*` APIs and ensure peak memory stays below a threshold.
    - On CP: use `gc.mem_free()` snapshots before/after and during iteration.
    - On CP emulator or MicroPython: use `gc.collect()` and `micropython.mem_info()` where available.
- Allocation pressure tests:
  - Configure environment variable (e.g., `CIRCUIT_DAWG_MAX_LIST_SIZE`) and, when set in tests, force list-returning APIs to stream via iterators internally, confirming behavior under constrained settings.
  - Property-based tests (Hypothesis on host) generating random prefixes and verifying results of iterator vs list-returning methods match while tracking allocation counts (via `tracemalloc` on host).

## Concrete next steps

1. Replace DAWG-build steps in tests with prebuilt fixtures (or add fixtures).
   - Update tests to reference files in `tests/fixtures/` (commit those from a trusted generation environment), or reuse the three sample `.dawg` files already present in repo root where they match needed types.
2. Make integer reads endianness-explicit.
   - Change `struct.unpack("I", ...)` to `struct.unpack("=I", ...)` in `Dictionary` methods (`has_value`, `value`, `follow_char`). Add benchmarks; ensure compatibility with existing `.dawg` files.
3. Add context manager support and iterator-first APIs.
   - Implement `__enter__/__exit__` for `Dictionary`, `Guide`, and the DAWG classes that own them; add iterator-based value accessors for `BytesDAWG`/`RecordDAWG`.
4. Add a minimal CP smoke test script.
   - Load a small `.dawg` fixture from the device filesystem; run `contains`, `find`, `keys`, `iteritems` on device and capture `gc.mem_free()` before/after to document footprint.
5. Optional: micro-optimizations after profiling.
   - Only if needed: pre-bind struct unpackers, introduce a tiny LRU cache for hot unit indices, and validate RAM trade-offs.

## Known limitations / considerations

- Building `.dawg` files on-device is out of scope; they must be pre-generated on a host and bundled.
- The completion logic may traverse many nodes and allocate temporary `bytearray` for the key; prefer iterator APIs for large outputs on CP.
- File handle limits on microcontrollers are low; the current design shares a single file handle which is good. Always call `close()`.

## Appendix: Quick code references

- Loading dictionary and guide from a single file:

```python
# circuit_dawg/dawgs.py
self.dct = wrapper.Dictionary()
self.guide = wrapper.Guide()
fp = open(path, "rb")
self.dct.read(fp, path)
self.guide.read(fp, path, 4 + self.dct.fp.base_size * 4)
```

- Unit decoding helpers:

```python
# circuit_dawg/units.py
HAS_LEAF_BIT = 1 << 8
EXTENSION_BIT = 1 << 9
IS_LEAF_BIT = 1 << 31

def has_leaf(base):
    return bool(base & HAS_LEAF_BIT)

def value(base):
    return base & (~IS_LEAF_BIT & 0xFFFFFFFF)

def label(base):
    return base & (IS_LEAF_BIT | 0xFF)

def offset(base):
    return ((base >> 10) << ((base & EXTENSION_BIT) >> 6)) & 0xFFFFFFFF
```

- FilePointer behavior:

```python
# circuit_dawg/wrapper.py
self.base_size = struct.unpack("=I", fp.read(4))[0]
self.skip = skip + 4

def seek(self, pos):
    return self.fp.seek(self.skip + pos)
```