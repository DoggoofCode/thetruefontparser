from bytereader import ByteReader, GlyphData, bitStr
from rich import print
from typing import Literal


def parse_flag(flag_bytes:bitStr):
    flag_bytes = flag_bytes.reverse()
    return {
        "on curve": flag_bytes.is_high(0),
        "x short vector": flag_bytes.is_high(1),
        "y short vector": flag_bytes.is_high(2),
        "repeat": flag_bytes.is_high(3),
        "x is same": flag_bytes.is_high(4),
        "y is same": flag_bytes.is_high(5),
    }


def extract_glyph(reader: ByteReader, little_endian: Literal["big", "little"]):
    glyph_data = GlyphData()
    glyph_data.number_of_contours = reader.read(2).int(little_endian)
    glyph_data.x_min = reader.read(2).fword(little_endian)
    glyph_data.y_min = reader.read(2).fword(little_endian)
    glyph_data.x_max = reader.read(2).fword(little_endian)
    glyph_data.y_max = reader.read(2).fword(little_endian)

    for _ in range(glyph_data.number_of_contours):
        glyph_data.end_point_of_contours.append(reader.read(2).uint(little_endian))

    # skip goofy ah instructions
    reader.shift(reader.read(2).uint(little_endian))

    max_points = glyph_data.number_of_points
    while len(glyph_data.flags) < max_points:
        flg = parse_flag(reader.read(1).bin(little_endian))
        glyph_data.flags.append(flg)
        if flg["repeat"]:
            repeat_amount = reader.read(1).uint(little_endian)
            for _ in range(repeat_amount):
                glyph_data.flags.append(flg)

    print(glyph_data)

def main() -> dict:
    little_endian: Literal["big", "little"] = "big"
    reader = ByteReader("path", "fonts/font.ttf")
    data = {}

    # Get the amount of tables
    reader.shift(4)
    data["Number Of Tables"] = reader.read(2).uint(little_endian)
    reader.shift(6)

    # Get the locations of each table
    data["tables"] = {}
    for tlb_index in range(data["Number Of Tables"]):
        table_data = {
            "tag": reader.read(4).text(),
            "check_sum": reader.read(4).uint(little_endian),
            "offset": reader.read(4).uint(little_endian),
            "length": reader.read(4).uint(little_endian),
        }

        data["tables"][table_data["tag"]] = table_data

    # Test Extract First Letter
    glyf_reader = reader.extract_reader(data["tables"]["glyf"]["offset"], data["tables"]["glyf"]["length"])
    extract_glyph(glyf_reader, little_endian)

    return data


if __name__ == '__main__':
    data_recieved = main()
    # print(data_recieved)
