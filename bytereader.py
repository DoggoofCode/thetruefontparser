from typing_extensions import Literal


class ComplexBytes:
    def __init__(self, information: bytes):
        self.data = information

    def text(self, boudary_markers=False):
        data = self.data.decode()
        if boudary_markers:
            data = f"'{data}'"
        return data

    def int(self, little_endian):
        return int.from_bytes(self.data, signed=True, byteorder=little_endian)

    def uint(self, little_endian):
        return int.from_bytes(self.data, signed=False, byteorder=little_endian)

    def bin(self, little_endian):
        return ' '.join(format(byte, '08b') for byte in self.data)  

    def fword(self, little_endian):
        if len(self.data) != 2:
            raise Exception("In correct size")
        return self.int(little_endian)

    def hex(self, little_endian=True):
        hex_info = self.data.hex()
        if little_endian:
            hex_info = hex_info[::-1]
        return f"0x{hex_info}"

    def __repr__(self):
        return f"{self.data}"

    def __getitem__(self, item):
        return self.data[item]


class ByteReader:
    head = 0
    def __init__(self, bytes_or_path: Literal["path", "bytes"], info: str | bytes, ) -> None:
        if bytes_or_path == "path":
            with open(info, "rb") as file:
                self.file_bytes: bytes = file.read()
        elif bytes_or_path == "bytes":
            self.file_bytes = info

    def move(self, moved_bytes: int):
        self.head += moved_bytes

    def read(self, read_bytes: int):
        self.head += read_bytes
        return ComplexBytes(self.file_bytes[self.head-read_bytes:self.head])

    def shift(self, length:int):
        self.head += length

    def sread(self, read_bytes: int):
        return ComplexBytes(self.file_bytes[self.head:self.head+read_bytes])

    def extract_reader(self, position: int, length:int):
        return ByteReader("bytes", self.file_bytes[position: position + length])

    def read_pos(self, position: int, length:int) -> ComplexBytes:
        return ComplexBytes(self.file_bytes[position: position+length])
