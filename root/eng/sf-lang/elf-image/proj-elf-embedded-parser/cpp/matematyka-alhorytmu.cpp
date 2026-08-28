#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>

namespace dwarf {

struct LebResult {
    std::uint64_t value;
    std::size_t bytes_consumed;
};

[[nodiscard]] constexpr std::optional<LebResult> decode_uleb128(std::span<const std::uint8_t> data) noexcept {
    std::uint64_t result = 0;
    std::uint32_t shift = 0;
    std::size_t count = 0;

    for (const auto byte : data) {
        ++count;
        result |= static_cast<std::uint64_t>(byte & 0x7FU) << shift;
        if ((byte & 0x80U) == 0U) {
            return LebResult{result, count};
        }
        shift += 7U;
        if (shift >= 64U) {
            return std::nullopt; // Помилка: перевищено розрядність 64 біти
        }
    }

    return std::nullopt; // Неповний потік байтів
}

} // namespace dwarf
