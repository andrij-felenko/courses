#define T10_POLY 0x8BB7

static uint16_t crc_bit(const uint8_t *p, size_t n)
{
    uint16_t crc = 0;                        /* початкове значення — нуль */

    for (size_t i = 0; i < n; i++) {
        crc ^= (uint16_t)p[i] << 8;          /* байт — у СТАРШУ половину */
        for (int b = 0; b < 8; b++)
            crc = (crc & 0x8000) ? (uint16_t)(crc << 1) ^ T10_POLY
                                 : (uint16_t)(crc << 1);
    }
    return crc;                              /* без дзеркалення й без XOR наприкінці */
}
