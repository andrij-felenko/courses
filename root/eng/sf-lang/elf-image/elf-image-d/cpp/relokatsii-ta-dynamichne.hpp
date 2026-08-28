#include <cstdint>

namespace elf {

struct RelocationEntry {
    std::uint32_t offset;
    std::uint32_t info;

    [[nodiscard]] constexpr std::uint32_t symbol_index() const noexcept {
        return info >> 8;
    }
    [[nodiscard]] constexpr std::uint8_t type() const noexcept {
        return static_cast<std::uint8_t>(info & 0xFFU);
    }
};

struct RelocationAddendEntry {
    std::uint32_t offset;
    std::uint32_t info;
    std::int32_t  addend;

    [[nodiscard]] constexpr std::uint32_t symbol_index() const noexcept {
        return info >> 8;
    }
    [[nodiscard]] constexpr std::uint8_t type() const noexcept {
        return static_cast<std::uint8_t>(info & 0xFFU);
    }
};

} // namespace elf
