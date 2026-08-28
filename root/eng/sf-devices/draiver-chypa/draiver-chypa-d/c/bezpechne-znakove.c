int32_t unpack_signed_20bit_be(const uint8_t *raw_3bytes) {
    /* 1. Беззнакове збирання 20 бітів Big-Endian */
    uint32_t u20 = (((uint32_t)raw_3bytes[0]) << 12) |
                   (((uint32_t)raw_3bytes[1]) << 4)  |
                   (((uint32_t)raw_3bytes[2]) >> 4);

    /* 2. Зсув 20-бітного значення у найстарші розряди 32-бітного слова */
    uint32_t shifted = u20 << 12;

    /* 3. Арифметичний зсув знакового типу розмножує 31-й біт на старші 12 розрядів */
    int32_t signed_result = ((int32_t)shifted) >> 12;

    return signed_result;
}
