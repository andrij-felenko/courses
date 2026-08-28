#include <cstdint>

// x, y < 2²⁴ (вистачає до рівня 24), z < 32, номер джерела < 256
constexpr uint64_t src_z(uint8_t src, uint32_t z)
{
    return (uint64_t(src) << 53) | (uint64_t(z & 31) << 48);
}

constexpr uint64_t row_key(uint8_t src, uint32_t z, uint32_t x, uint32_t y)
{
    return src_z(src, z) | (uint64_t(y & 0xFFFFFF) << 24) | uint64_t(x & 0xFFFFFF);
}
