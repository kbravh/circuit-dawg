import struct

from . import units
from os import path


class FilePointer:
    """
    FilePointer class to allow for skipping the first 4 bytes of
    the file (which is the root index of the DAWG).
    """

    def __init__(self, fp, skip=0):
        self.fp = fp
        self.fp.seek(0 + skip)
        self.base_size = struct.unpack(str("=I"), fp.read(4))[0]
        self.skip = (
            skip + 4
        )  # The first # bytes that belong to other models and the base_size

    def read(self, size):
        return self.fp.read(size)

    def seek(self, pos):
        # Adjust the seek position to skip the irrelevant bytes
        adjusted_pos = self.skip + pos
        return self.fp.seek(adjusted_pos)

    def close(self):
        if self.fp:
          self.fp.close()

    def __del__(self):
        if self.fp:
            self.fp.close()


class Dictionary:
    """
    Dictionary class for retrieval and binary I/O.
    """

    def __init__(self):
        self.fp = None
        self.file_path = None

    ROOT = 0
    "Root index"

    def has_value(self, index):
        "Checks if a given index is related to the end of a key."
        self.fp.seek(index * 4)
        base = struct.unpack("I", self.fp.read(4))[0]
        return units.has_leaf(base)

    def value(self, index):
        self.fp.seek(index * 4)
        base = struct.unpack("I", self.fp.read(4))[0]
        offset = units.offset(base)
        value_index = (index ^ offset) & units.PRECISION_MASK
        self.fp.seek(value_index * 4)
        return units.value(struct.unpack("I", self.fp.read(4))[0])

    def read(self, fp, path):
        self.fp = FilePointer(fp)
        self.file_path = path

    def contains(self, key):
        "Exact matching."
        index = self.follow_bytes(key, self.ROOT)
        if index is None:
            return False
        return self.has_value(index)

    def find(self, key):
        "Exact matching (returns value)"
        index = self.follow_bytes(key, self.ROOT)
        if index is None:
            return -1
        if not self.has_value(index):
            return -1
        return self.value(index)

    def follow_char(self, label, index):
        "Follows a transition"
        self.fp.seek(index * 4)
        base = struct.unpack("I", self.fp.read(4))[0]
        offset = units.offset(base)
        next_index = (index ^ offset ^ label) & units.PRECISION_MASK
        self.fp.seek(next_index * 4)

        if units.label(struct.unpack("I", self.fp.read(4))[0]) != label:
            return None

        return next_index

    def follow_bytes(self, s, index):
        "Follows transitions."
        for ch in s:
            index = self.follow_char(ch, index)
            if index is None:
                return None

        return index

    @classmethod
    def load(cls, path):
        dawg = cls()
        dawg.file_path = path
        fp = open(path, "rb")
        dawg.read(fp, path)
        return dawg

    def close(self):
        if self.fp is not None:
            self.fp.close()
            self.fp = None
            self.file_path = None


class Guide:
    ROOT = 0

    def __init__(self):
        self.fp = None
        self.file_path = None

    def child(self, index):
        self.fp.seek(index * 2)
        return struct.unpack("B", self.fp.read(1))[0]

    def sibling(self, index):
        self.fp.seek(index * 2 + 1)
        return struct.unpack("B", self.fp.read(1))[0]

    def read(self, fp, path, skip=0):
        self.fp = FilePointer(fp, skip=skip)
        self.file_path = path

    def close(self):
        if self.fp is not None:
            self.fp.close()
            self.fp = None
            self.file_path = None

    def size(self):
        return self.fp.base_size * 2


class Completer:
    def __init__(self, dic=None, guide=None):
        self._dic = dic
        self._guide = guide

    def value(self):
        return self._dic.value(self._last_index)

    def start(self, index, prefix=b""):
        self.key = bytearray(prefix)

        if self._guide.size():
            self._index_stack = [index]
            self._last_index = self._dic.ROOT
        else:
            self._index_stack = []

    def next(self):
        "Gets the next key"

        if not self._index_stack:
            return False

        index = self._index_stack[-1]

        if self._last_index != self._dic.ROOT:
            child_label = self._guide.child(index)  # UCharType

            if child_label:
                # Follows a transition to the first child.
                index = self._follow(child_label, index)
                if index is None:
                    return False
            else:
                while True:
                    sibling_label = self._guide.sibling(index)
                    # Moves to the previous node.
                    if len(self.key) > 0:
                        self.key.pop()
                        # self.key[-1] = 0

                    self._index_stack.pop()
                    if not self._index_stack:
                        return False

                    index = self._index_stack[-1]
                    if sibling_label:
                        # Follows a transition to the next sibling.
                        index = self._follow(sibling_label, index)
                        if index is None:
                            return False
                        break

        return self._find_terminal(index)

    def _follow(self, label, index):
        next_index = self._dic.follow_char(label, index)
        if next_index is None:
            return None

        self.key.append(label)
        self._index_stack.append(next_index)
        return next_index

    def _find_terminal(self, index):
        while not self._dic.has_value(index):
            label = self._guide.child(index)

            index = self._dic.follow_char(label, index)
            if index is None:
                return False

            self.key.append(label)
            self._index_stack.append(index)

        self._last_index = index
        return True
