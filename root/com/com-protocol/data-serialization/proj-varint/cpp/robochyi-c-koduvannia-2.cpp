size_t varint_encode_u64(uint64_t value, uint8_t *buf, size_t cap) {
    size_t i = 0;
    while (value >= 0x80) {
        if (i >= cap) return 0;
        buf[i++] = (uint8_t)(value | 0x80);
        value >>= 7;
    }
    if (i >= cap) return 0;
    buf[i++] = (uint8_t)value;
    return i;
}
