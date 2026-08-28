// Формати точок у стилі C++20 з constexpr
#include <cstddef>

namespace crypto::config {
    constexpr std::size_t kBls12_381FpBytes        = 48;
    constexpr std::size_t kBls12_381Fp2Bytes       = 96;  // 2 * 48 bytes
    constexpr std::size_t kBls12_381G2Uncompressed = 192; // (x, y) in Fp2
    constexpr std::size_t kBls12_381G2Compressed   = 96;  // x in Fp2 + flags

    constexpr std::size_t kBn254FpBytes            = 32;
    constexpr std::size_t kBn254Fp2Bytes           = 64;
    constexpr std::size_t kBn254G2Uncompressed     = 128;
    constexpr std::size_t kBn254G2Compressed       = 64;
}
