# wire types
WT_VARINT, WT_I64, WT_LEN, WT_I32 = 0, 1, 2, 5

# Записати тег поля (номер + тип); повертає bytes.
def tag_encode(field_num: int, wire_type: int) -> bytes:
    tag = (field_num << 3) | (wire_type & 0x07)
    return varint_encode_u32(tag)                  # тег — теж varint

# Розібрати тег: (номер, тип, число з'їдених байтів); (None, None, 0) при помилці.
def tag_decode(buf: bytes):
    tag, n = varint_decode_u32(buf)
    if n == 0:                                     # обірваний/зіпсований тег
        return None, None, 0
    wire_type = tag & 0x07                          # три молодші біти — тип
    field_num = tag >> 3                            # решта — номер поля
    return field_num, wire_type, n
