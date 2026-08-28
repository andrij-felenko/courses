// C++: Ідіоматична обгортка класичного кадру CAN
#include <cstdint>
#include <array>
#include <span>

namespace can {

struct Frame {
    std::uint32_t id{0};                           // 11/29-біт ID та прапорці
    std::uint8_t  dlc{0};                          // Фактичний розмір (0..8)
    std::array<std::uint8_t, 8> data{};            // Фіксований буфер даних

    [[nodiscard]] constexpr std::span<const std::uint8_t> payload() const noexcept {
        return std::span<const std::uint8_t>{data.data(), dlc};
    }
};

} // namespace can
