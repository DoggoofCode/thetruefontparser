from bytereader import ByteReader
from rich import print
from typing import Literal

def extract_glyph(reader: ByteReader, little_endian: Literal["big", "little"]):
    glyph_data = {
        "Number of Contours": reader.read(2).int(little_endian),
        "xMin": reader.read(2).fword(little_endian),
        "yMin": reader.read(2).fword(little_endian),
        "xMax": reader.read(2).fword(little_endian),
        "yMax": reader.read(2).fword(little_endian)
    }
    end_points_of_contours = []
    for _ in range(glyph_data["Number of Contours"]):
        end_points_of_contours.append(reader.read(2).uint(little_endian))
    glyph_data["End Points of Contours"] = end_points_of_contours
    if glyph_data["Number of Contours"] != 0:
        glyph_data["Number of Points"] = glyph_data["End Points of Contours"][-1] + 1

    # skip goofy ah instructions
    reader.shift(reader.read(2).uint(little_endian))

     

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
