import pytest
import io
from circuit_dawg.wrapper import FilePointer
import gc


class TestFilePointer:
    @pytest.fixture(autouse=True, scope="function", name="fp")
    def setup(self):
        test_io = io.BytesIO(b"\x00\x01\x00\x00Hello World!")
        return FilePointer(test_io)

    def test_seek_and_read(self, fp):
        # The first seek should skip the first 4 bytes
        fp.seek(0)
        assert fp.read(5) == b"Hello"

        # Subsequent seeks should be offset by 4
        fp.seek(6)
        assert fp.read(5) == b"World"

    def test_base_size(self, fp):
        """
        The base_size should be the first 4 bytes of the file.
        The FilePointer should then adjust the skip to be 4 bytes.
        """
        assert fp.base_size == 256  # 0x0100
        assert fp.skip == 4

    @pytest.mark.parametrize("skip", [(0, 4), (4, 8), (8, 12)])
    def test_seek(self, fp, skip):
        """
        The seek should be adjusted by the skip.
        """
        fp.seek(skip[0])
        assert fp.fp.tell() == skip[1]

    def test_close(self, fp):
        file = fp.fp
        fp.close()
        assert file.closed is True
