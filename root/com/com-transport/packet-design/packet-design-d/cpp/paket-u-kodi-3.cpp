// Перевірити кадр довжини n. true — цілий; виходи id/data/len дійсні лише тоді.
bool check(const uint8_t *buf, size_t n,
           uint8_t *id, const uint8_t **data, uint8_t *len) {
    if (n < 4 || buf[0] != SYNC) return false;   // нема SYNC або замало байтів
    uint8_t L = buf[1];                           // LEN = ID + дані
    if ((size_t)L + 3 != n) return false;         // довжина не збігається з кадром
    if (crc8(&buf[1], (size_t)L + 1) != buf[n - 1]) return false;  // CRC не зійшовся
    *id   = buf[2];
    *data = &buf[3];
    *len  = (uint8_t)(L - 1);                      // самі дані, без ID
    return true;
}
