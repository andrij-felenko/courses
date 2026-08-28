#include <bit>
#include <cstdint>

uint32_t val = 0b0000'1111'0000'0000;
int ones = std::popcount(val);           // Апаратний POPCNT -> 4
int leading_zeros = std::countl_zero(val);// Апаратний LZCNT -> 4
bool is_pow2 = std::has_single_bit(16u);  // true

// Безпечне приведення типів без порушення Strict Aliasing
float f = 1.0f;
uint32_t raw_bits = std::bit_cast<uint32_t>(f); // mov замість memcpy
