#include <cstdint>

// Ідіоматичні inline-функції C++ для маніпуляцій r_info
constexpr std::uint32_t get_elf64_r_sym(std::uint64_t info) noexcept {
    return static_cast<std::uint32_t>(info >> 32);
}

constexpr std::uint32_t get_elf64_r_type(std::uint64_t info) noexcept {
    return static_cast<std::uint32_t>(info & 0xffffffffL);
}

constexpr std::uint64_t make_elf64_r_info(std::uint32_t sym, std::uint32_t type) noexcept {
    return (static_cast<std::uint64_t>(sym) << 32) + type;
}
