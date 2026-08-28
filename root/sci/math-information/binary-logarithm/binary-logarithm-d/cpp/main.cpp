#include <bit>
#include <cstdint>

// ⌊log₂n⌋ — позиція старшого одиничного біта; для n == 0 не визначено
constexpr int floor_log2(std::uint64_t n) {
    return 63 - std::countl_zero(n);      // countl_zero(0) == 64 → дасть −1
}

// ⌈log₂n⌉ — скільки бітів, щоб пронумерувати n значень
constexpr int ceil_log2(std::uint64_t n) {
    return std::bit_width(n - 1);         // n == 1 → bit_width(0) == 0
}
