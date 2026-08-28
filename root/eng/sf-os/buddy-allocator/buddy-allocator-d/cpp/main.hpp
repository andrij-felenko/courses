// Еквівалентні операції мовою C++20 з використанням типізованих зміщень
#include <cstdint>
#include <concepts>
#include <bit>

[[nodiscard]] constexpr uintptr_t buddy_find_twin(uintptr_t offset, uint8_t order) noexcept {
    return offset ^ (1ULL << order);
}

[[nodiscard]] constexpr uintptr_t buddy_find_parent(uintptr_t offset, uint8_t order) noexcept {
    return offset & ~(1ULL << order);
}

[[nodiscard]] constexpr uint8_t size_to_order(size_t bytes, size_t min_block_size) noexcept {
    if (bytes <= min_block_size) return static_cast<uint8_t>(std::countr_zero(min_block_size));
    return static_cast<uint8_t>(std::bit_width(bytes - 1));
}
