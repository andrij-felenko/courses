uint8_t gf256_mul_ct(uint8_t a, uint8_t b, uint16_t poly) {
    uint8_t res = 0;
    for (int i = 0; i < 8; i++) {
        uint8_t mask = (uint8_t)(-(b & 1));
        res ^= (a & mask);
        uint8_t carry = (uint8_t)(-(a >> 7));
        a = (a << 1) ^ ((poly & 0xFF) & carry);
        b >>= 1;
    }
    return res;
}
