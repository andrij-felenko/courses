typedef struct {
    uint16_t ch[16];      // сирі 0..2047
    uint8_t  ch17;        // 0/1
    uint8_t  ch18;        // 0/1
    uint8_t  frame_lost;  // 0/1
    uint8_t  failsafe;    // 0/1
} sbus_data_t;

static void sbus_read_flags(uint8_t flags, sbus_data_t *out) {
    out->ch17       = (flags & 0x01) ? 1 : 0;
    out->ch18       = (flags & 0x02) ? 1 : 0;
    out->frame_lost = (flags & 0x04) ? 1 : 0;
    out->failsafe   = (flags & 0x08) ? 1 : 0;
}
