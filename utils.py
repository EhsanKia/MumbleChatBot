def parse_varint(data):
    barray = bytearray(data[:10])
    byte = barray.pop(0)
    if byte >> 7 == 0:
        varint, rem = byte & 127, 0
    elif byte >> 6 == 2:
        varint, rem = byte & 63, 1
    elif byte >> 5 == 6:
        varint, rem = byte & 31, 2
    elif byte >> 4 == 14:
        varint, rem = byte & 15, 3
    elif byte >> 2 == 60:
        varint, rem = 0, 4
    elif byte >> 2 == 61:
        varint, rem = 0, 8
    elif byte >> 2 == 62:
        varint, data = parse_varint(data[1:])
        return -varint, data
    elif byte >> 2 == 63:
        varint, rem = ~byte | 0xFC, 0

    for i in range(rem):
        varint <<= 8
        varint += barray.pop(0)

    return varint, data[rem+1:]
