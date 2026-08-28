typedef enum {
    TELEM_OK = 0,
    TELEM_SHORT,        /* байтів менше, ніж вимагає формат */
    TELEM_MAGIC_BAD,
    TELEM_VER_BAD,
    TELEM_LEN_BAD,
    TELEM_CRC_BAD
} telem_err_t;

static telem_err_t telem_decode(const uint8_t *buf, size_t n, telem_t *out)
{
    if (n < TELEM_SIZE) return TELEM_SHORT;   /* до першого читання */

    rd_t r;
    rd_init(&r, buf, TELEM_SIZE);   /* читаємо рівно своє, а не «скільки прийшло» */

    uint16_t magic = rd_u16(&r);
    uint8_t  ver   = rd_u8 (&r);
    uint8_t  flags = rd_u8 (&r);
    uint16_t len   = rd_u16(&r);
    (void)rd_u16(&r);               /* rsv — читаємо, щоб просунути курсор */

    if (magic != TELEM_MAGIC) return TELEM_MAGIC_BAD;
    if (ver   != TELEM_VER)   return TELEM_VER_BAD;
    if (len   != TELEM_SIZE)  return TELEM_LEN_BAD;

    uint16_t want = (uint16_t)(((uint32_t)buf[OFF_CRC] << 8) | buf[OFF_CRC + 1]);
    if (crc16(buf, OFF_CRC) != want) return TELEM_CRC_BAD;

    out->time_us = rd_u64(&r);
    out->lat_e7  = rd_i32(&r);
    out->lon_e7  = rd_i32(&r);
    out->alt_mm  = rd_i32(&r);
    out->mv      = rd_u16(&r);
    out->flags   = flags;

    return r.bad ? TELEM_SHORT : TELEM_OK;
}
