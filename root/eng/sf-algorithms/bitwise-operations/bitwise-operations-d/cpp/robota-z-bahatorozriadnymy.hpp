#include <cstdint>
#include <concepts>

template <std::size_t Offset, std::size_t Width>
struct BitField {
    static constexpr std::uint32_t Mask = ((1U << Width) - 1U) << Offset;

    [[nodiscard]] static constexpr std::uint32_t extract(std::uint32_t reg) noexcept {
        return (reg & Mask) >> Offset;
    }

    [[nodiscard]] static constexpr std::uint32_t insert(std::uint32_t reg, std::uint32_t val) noexcept {
        return (reg & ~Mask) | ((val << Offset) & Mask);
    }
};

// Використання: BitField<4, 4>::extract(reg);
