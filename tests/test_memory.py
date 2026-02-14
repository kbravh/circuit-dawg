import os
import tracemalloc

import pytest

from circuit_dawg import DAWG, BytesDAWG, CompletionDAWG

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def measure_peak_memory(func):
    """Run func and return its peak memory usage in bytes."""
    tracemalloc.start()
    tracemalloc.reset_peak()
    func()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def measure_memory_delta(func):
    """Run func and return net memory change in bytes."""
    tracemalloc.start()
    snap_before = tracemalloc.take_snapshot()
    func()
    snap_after = tracemalloc.take_snapshot()
    tracemalloc.stop()

    stats = snap_after.compare_to(snap_before, "lineno")
    return sum(stat.size_diff for stat in stats)


# ---------------------------------------------------------------------------
# Load tests — measure peak memory when loading each DAWG type
# ---------------------------------------------------------------------------


@pytest.mark.memory
class TestLoadMemory:
    def test_dawg_load_peak(self):
        peak = measure_peak_memory(
            lambda: DAWG().load(os.path.join(FIXTURES_DIR, "dawg.dawg"))
        )
        # CPython uses ~2-4x more memory than MicroPython.
        # Budget: 100 KB should be generous for small test fixtures.
        assert peak < 100_000, f"DAWG load peak: {peak:,} bytes"

    def test_completion_dawg_load_peak(self):
        peak = measure_peak_memory(
            lambda: CompletionDAWG().load(os.path.join(FIXTURES_DIR, "completion.dawg"))
        )
        assert peak < 100_000, f"CompletionDAWG load peak: {peak:,} bytes"

    def test_bytes_dawg_load_peak(self):
        peak = measure_peak_memory(
            lambda: BytesDAWG().load(os.path.join(FIXTURES_DIR, "bytes.dawg"))
        )
        assert peak < 100_000, f"BytesDAWG load peak: {peak:,} bytes"


# ---------------------------------------------------------------------------
# Lookup tests — measure memory delta for contains/get operations
# ---------------------------------------------------------------------------


@pytest.mark.memory
class TestLookupMemory:
    def test_dawg_contains_memory(self):
        d = DAWG().load(os.path.join(FIXTURES_DIR, "dawg.dawg"))
        delta = measure_memory_delta(lambda: "foo" in d)
        # Lookups should allocate very little — 10 KB budget is generous.
        assert delta < 10_000, f"DAWG __contains__ delta: {delta:,} bytes"
        d.close()

    def test_bytes_dawg_get_memory(self):
        d = BytesDAWG().load(os.path.join(FIXTURES_DIR, "bytes.dawg"))
        delta = measure_memory_delta(lambda: d.get("foo"))
        assert delta < 10_000, f"BytesDAWG get() delta: {delta:,} bytes"
        d.close()


# ---------------------------------------------------------------------------
# Completion tests — measure memory delta for keys/iterkeys
# ---------------------------------------------------------------------------


@pytest.mark.memory
class TestCompletionMemory:
    def test_completion_keys_memory(self):
        d = CompletionDAWG().load(os.path.join(FIXTURES_DIR, "completion.dawg"))
        delta = measure_memory_delta(lambda: d.keys())
        # Completions accumulate results — allow 50 KB for small fixture.
        assert delta < 50_000, f"CompletionDAWG keys() delta: {delta:,} bytes"
        d.close()

    def test_completion_iterkeys_memory(self):
        d = CompletionDAWG().load(os.path.join(FIXTURES_DIR, "completion.dawg"))
        delta = measure_memory_delta(lambda: list(d.iterkeys()))
        assert delta < 50_000, f"CompletionDAWG iterkeys() delta: {delta:,} bytes"
        d.close()

    def test_bytes_dawg_keys_memory(self):
        d = BytesDAWG().load(os.path.join(FIXTURES_DIR, "bytes.dawg"))
        delta = measure_memory_delta(lambda: d.keys())
        assert delta < 50_000, f"BytesDAWG keys() delta: {delta:,} bytes"
        d.close()


# ---------------------------------------------------------------------------
# Cleanup tests — verify close() and context managers release resources
# ---------------------------------------------------------------------------


@pytest.mark.memory
class TestCleanupMemory:
    def test_dawg_close_releases_resources(self):
        d = DAWG().load(os.path.join(FIXTURES_DIR, "dawg.dawg"))
        d.close()
        assert d.dct is None

    def test_completion_dawg_close_releases_resources(self):
        d = CompletionDAWG().load(os.path.join(FIXTURES_DIR, "completion.dawg"))
        d.close()
        assert d.dct is None
        assert d.guide is None

    def test_bytes_dawg_close_releases_resources(self):
        d = BytesDAWG().load(os.path.join(FIXTURES_DIR, "bytes.dawg"))
        d.close()
        assert d.dct is None
        assert d.guide is None

    def test_context_manager_releases_resources(self):
        with CompletionDAWG().load(os.path.join(FIXTURES_DIR, "completion.dawg")) as d:
            _ = d.keys()
        assert d.dct is None
        assert d.guide is None
