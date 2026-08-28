static const uint8_t POPCOUNT_TABLE_256[256] = {
    0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4,
    /* ... 256 попередньо обчислених значень ... */
};

int popcount_lut(uint64_t x) {
    return POPCOUNT_TABLE_256[x & 0xFF] +
           POPCOUNT_TABLE_256[(x >> 8) & 0xFF] +
           POPCOUNT_TABLE_256[(x >> 16) & 0xFF] +
           POPCOUNT_TABLE_256[(x >> 24) & 0xFF] +
           POPCOUNT_TABLE_256[(x >> 32) & 0xFF] +
           POPCOUNT_TABLE_256[(x >> 40) & 0xFF] +
           POPCOUNT_TABLE_256[(x >> 48) & 0xFF] +
           POPCOUNT_TABLE_256[(x >> 56) & 0xFF];
}
