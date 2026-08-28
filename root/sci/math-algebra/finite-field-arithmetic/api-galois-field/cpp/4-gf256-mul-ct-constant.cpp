namespace galois {
    [[nodiscard]] constexpr uint8_t multiply_constant_time(uint8_t a, uint8_t b, uint16_t poly) noexcept {
        uint8_t res = 0;
        for (int i = 0; i < 8; ++i) {
            uint8_t mask = static_cast<uint8_t>(0) - (b & 1);
            res ^= (a & mask);
            uint8_t carry = static_cast<uint8_t>(0) - ((a >> 7) & 1);
            a = static_cast<uint8_t>(a << 1) ^ ((poly & 0xFF) & carry);
            b >>= 1;
        }
        return res;
    }
}
