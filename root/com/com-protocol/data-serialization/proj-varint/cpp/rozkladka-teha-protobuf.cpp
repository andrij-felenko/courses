// wire types
#define WT_VARINT  0
#define WT_I64     1
#define WT_LEN     2
#define WT_I32     5

// Записати тег поля (номер + тип) у buf; повертає число байтів або 0.
size_t tag_encode(uint32_t field_num, uint8_t wire_type,
                  uint8_t *buf, size_t cap) {
    uint32_t tag = (field_num << 3) | (wire_type & 0x07);
    return varint_encode_u32(tag, buf, cap);      // тег — теж varint
}

// Розібрати тег: дістати номер поля й тип. Повертає число з'їдених байтів або 0.
size_t tag_decode(const uint8_t *buf, size_t len,
                  uint32_t *field_num, uint8_t *wire_type) {
    uint32_t tag;
    size_t n = varint_decode_u32(buf, len, &tag);
    if (n == 0) return 0;                          // обірваний/зіпсований тег
    *wire_type = (uint8_t)(tag & 0x07);            // три молодші біти — тип
    *field_num = tag >> 3;                         // решта — номер поля
    return n;
}
