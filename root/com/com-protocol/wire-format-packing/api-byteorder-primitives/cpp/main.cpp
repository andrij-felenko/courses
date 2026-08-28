#include <bit>
#include <cstdint>
#include <cstring>

// Записати double у буфер як 8 байтів big-endian — без приведення покажчиків.
void put_f64_be(std::uint8_t *b, double v)
{
    std::uint64_t bits = std::bit_cast<std::uint64_t>(v);   // C++20
    if constexpr (std::endian::native == std::endian::little)
        bits = std::byteswap(bits);                          // C++23
    std::memcpy(b, &bits, sizeof bits);
}
