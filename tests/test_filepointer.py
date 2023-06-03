import pytest
import io
from circuit_dawg import FilePointer


def test_seek_and_read():
    test_io = io.BytesIO(b"\x00\x00\x00\x00Hello World!")
    fp = FilePointer(test_io)

    # The first seek should skip the first 4 bytes
    fp.seek(0)
    assert fp.read(5) == b"Hello"

    # Subsequent seeks should be offset by 4
    fp.seek(6)
    assert fp.read(5) == b"World"


def test_close():
    test_io = io.BytesIO(b"\x00\x00\x00\x00Hello World!")
    fp = FilePointer(test_io)

    # Close should work without raising an exception
    try:
        fp.close()
    except Exception:
        pytest.fail("Unexpected Exception raised")


def test_destructor():
    test_io = io.BytesIO(b"\x00\x00\x00\x00Hello World!")
    fp = FilePointer(test_io)

    # Delete should work without raising an exception
    try:
        del fp
    except Exception:
        pytest.fail("Unexpected Exception raised")


# Add more tests as necessary
