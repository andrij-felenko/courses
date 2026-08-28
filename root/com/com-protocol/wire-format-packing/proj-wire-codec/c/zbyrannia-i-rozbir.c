typedef struct {
    uint64_t time_us;
    int32_t  lat_e7, lon_e7, alt_mm;
    uint16_t mv;
    uint8_t  flags;
} telem_t;

/* Повертає кількість записаних байтів або 0, якщо не влізло. */
static size_t telem_encode(uint8_t *buf, size_t cap, const telem_t *t)
{
    wr_t w;
    wr_init(&w, buf, cap);

    wr_u16(&w, TELEM_MAGIC);
    wr_u8 (&w, TELEM_VER);
    wr_u8 (&w, t->flags);
    wr_u16(&w, TELEM_SIZE);      /* len — довжина ВСЬОГО повідомлення */
    wr_u16(&w, 0);               /* rsv — завжди нулі */
    wr_u64(&w, t->time_us);
    wr_i32(&w, t->lat_e7);
    wr_i32(&w, t->lon_e7);
    wr_i32(&w, t->alt_mm);
    wr_u16(&w, t->mv);

    if (w.bad) return 0;         /* ← не косметика, див. нижче */

    wr_u16(&w, crc16(buf, OFF_CRC));
    return w.bad ? 0 : TELEM_SIZE;
}
