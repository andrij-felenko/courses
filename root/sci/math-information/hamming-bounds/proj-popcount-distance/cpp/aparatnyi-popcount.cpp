#include <array>
static std::array<uint8_t, 256> bits_in_byte;   // заповнити одноразово на старті
void popcount_table_init() {
    for (int i = 0; i < 256; i++)
        bits_in_byte[i] = popcount_kernighan(static_cast<uint32_t>(i));
}
int popcount_table(uint32_t x) {
    return bits_in_byte[x & 0xFF] + bits_in_byte[(x >> 8) & 0xFF]
         + bits_in_byte[(x >> 16) & 0xFF] + bits_in_byte[(x >> 24) & 0xFF];
}
