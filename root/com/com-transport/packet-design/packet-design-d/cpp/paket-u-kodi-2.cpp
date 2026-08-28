// Зібрати кадр у буфер out; повертає його повну довжину в байтах.
size_t build(uint8_t *out, uint8_t id, const uint8_t *data, uint8_t len) {
    out[0] = SYNC;
    out[1] = (uint8_t)(len + 1);   // LEN = ID + дані
    out[2] = id;
    for (uint8_t i = 0; i < len; i++)
        out[3 + i] = data[i];
    out[3 + len] = crc8(&out[1], (size_t)len + 2);  // CRC по LEN..дані
    return (size_t)len + 4;        // SYNC+LEN+ID+дані+CRC
}
