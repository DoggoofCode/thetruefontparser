from bytereader import ByteReader, GlyphData, bitStr, lsClassObjects
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


def extract_glyph_data(reader: ByteReader, little_endian: Literal["big", "little"]):
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
        flg = parse_flag(reader.read(1).bin())
        glyph_data.flags.append(flg)
        if flg["repeat"]:
            repeat_amount = reader.read(1).uint(little_endian)
            for _ in range(repeat_amount):
                glyph_data.flags.append(flg)

    for idx, flg in enumerate(glyph_data.flags):
        # Ensure Flags
        flag_x = glyph_data.flag_def(flg, "x")

        # X Flags
        last_position = glyph_data.raw_x[-1]
        if flag_x == "positive":
            glyph_data.raw_x.append(last_position + reader.read(1).uint(little_endian))
        elif flag_x == "negative":
            glyph_data.raw_x.append(last_position - reader.read(1).uint(little_endian))
        elif flag_x == "same":
            glyph_data.raw_x.append(last_position)
        elif flag_x == "16b":
            glyph_data.raw_x.append(last_position + reader.read(2).int(little_endian))

    for idx, flg in enumerate(glyph_data.flags):
        # Y Flags
        flag_y = glyph_data.flag_def(flg, "y")
        last_position = glyph_data.raw_y[-1]
        if flag_y == "positive":
            glyph_data.raw_y.append(last_position + reader.read(1).uint(little_endian))
        elif flag_y == "negative":
            glyph_data.raw_y.append(last_position - reader.read(1).uint(little_endian))
        elif flag_y == "same":
            glyph_data.raw_y.append(last_position)
        elif flag_y == "16b":
            glyph_data.raw_y.append(last_position + reader.read(2).int(little_endian))

        return glyph_data
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
    dt = extract_glyph_data(glyf_reader, little_endian)

    return data


if __name__ == '__main__':
    data_recieved = main()
    # print(data_recieved)
