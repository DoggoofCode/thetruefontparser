from absl.flags import flag_dict_to_args
from typing_extensions import Literal

class bitStr(str):
    def reverse(self):
        return bitStr(self[::-1])

    def is_high(self, idx):
        char = self[idx]
        if char == "1":
            return True
        else:
            return False

    def is_low(self, idx):
        char = self[idx]
        if char == "1":
            return True
        else:
            return False
class GlyphData:
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    number_of_contours: int
    end_point_of_contours: list[int] = []
    flags: list = []
    # Gobal X position, Gobal Y position, On curve
    raw_x: list[int] = [0]
    raw_y: list[int] = [0]

    @property
    def coordinates(self):
        on_curve = []
        for flg in self.flags:
            on_curve.append(flg['on curve'])
        return list(zip(self.raw_x, self.raw_y, on_curve))

    @property
    def number_of_points(self):
        if len(self.end_point_of_contours) != 0:
            return self.end_point_of_contours[-1] + 1
        else:
            return 0

    def flag_def(self, index, type: Literal["x", "y"]) -> str:
        flg = index
        if flg[f"{type} short vector"]:
            return "positive" if flg[f"{type} is same"] else "negative"
        else:
            return "same" if flg[f"{type} is same"] else "16b"

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

    def bin(self, ):
        return bitStr(' '.join(format(byte, '08b') for byte in self.data))

    def fword(self, little_endian):
        if len(self.data) != 2:
            raise Exception("In correct size")
        return self.int(little_endian)

    def hex(self, little_endian=True):
        hex_info = self.data.hex()
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

def lsClassObjects(obj):
    attributes = dir(obj)
    filtered_attributes = {attr: getattr(obj, attr) for attr in attributes if not attr.startswith('__')}
    return filtered_attributes