enum {
    PROTO_VER_2 = 2,
    MSG_STATUS  = 2,
    OFF_MSGID   = OFF_RSV,                 /* колишній резерв */
    HDR_SIZE    = OFF_TIME + 8,            /* 16 */
    STATUS_MIN  = HDR_SIZE + 1 + 0 + 4 + 2 /* порожнє ім'я: 23 байти */
};

static size_t status_encode(uint8_t *buf, size_t cap, uint64_t time_us,
                            uint8_t flags, const char *name, size_t name_len,
                            float vbat_v)
{
    if (name_len > 255) return 0;              /* межа ДО арифметики */
    size_t total = STATUS_MIN + name_len;      /* ≤ 278 — переповнення неможливе */
    if (total > cap) return 0;

    wr_t w;
    wr_init(&w, buf, cap);
    wr_u16(&w, TELEM_MAGIC);
    wr_u8 (&w, PROTO_VER_2);
    wr_u8 (&w, flags);
    wr_u16(&w, (uint16_t)total);
    wr_u16(&w, MSG_STATUS);
    wr_u64(&w, time_us);
    wr_str(&w, name, name_len);
    wr_f32(&w, vbat_v);

    if (w.bad) return 0;
    wr_u16(&w, crc16(buf, total - 2));
    return w.bad ? 0 : total;
}

static bool status_decode(const uint8_t *buf, size_t n,
                          const uint8_t **name, size_t *name_len, float *vbat_v)
{
    if (n < STATUS_MIN) return false;
    size_t len = ((size_t)buf[OFF_LEN] << 8) | buf[OFF_LEN + 1];
    if (len < STATUS_MIN || len > n) return false;   /* ← ключовий рядок */

    uint16_t want = (uint16_t)(((uint32_t)buf[len - 2] << 8) | buf[len - 1]);
    if (crc16(buf, len - 2) != want) return false;

    rd_t r;
    rd_init(&r, buf, len - 2);              /* хвіст із сумою читати нічим */
    if (!rd_take(&r, HDR_SIZE)) return false;   /* заголовок уже перевірено вище */

    if (!rd_str(&r, name, name_len)) return false;
    *vbat_v = rd_f32(&r);
    return !r.bad;
}
