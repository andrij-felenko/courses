size_t varint_decode_u64(const uint8_t *buf, size_t len, uint64_t *out) {
    uint64_t result = 0;
    size_t   i = 0;
    int      shift = 0;

    while (i < len) {
        uint8_t b = buf[i++];
        result |= (uint64_t)(b & 0x7F) << shift;
        if ((b & 0x80) == 0) {
            *out = result;
            return i;
        }
        shift += 7;
        if (shift >= 64) return 0;
    }
    return 0;
}
