// C++: Обгортка кадру CAN FD
#include <cstdint>
#include <array>
#include <span>

namespace can {

struct FdFrame {
    std::uint32_t id{0};                           // ID та прапорці
    std::uint8_t  len{0};                          // Довжина (0..64)
    std::uint8_t  flags{0};                        // Прапорці BRS / ESI
    std::array<std::uint8_t, 64> data{};           // Розширений буфер

    [[nodiscard]] constexpr bool has_brs() const noexcept {
        return (flags & 0x01) != 0;
    }

    [[nodiscard]] constexpr std::span<const std::uint8_t> payload() const noexcept {
        return std::span<const std::uint8_t>{data.data(), len};
    }
};

} // namespace can
