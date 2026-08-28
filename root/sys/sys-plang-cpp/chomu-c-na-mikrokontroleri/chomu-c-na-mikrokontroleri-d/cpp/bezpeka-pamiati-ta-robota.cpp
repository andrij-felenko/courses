// Обробка буфера мовою C++ через std::span та std::optional
#include <cstdint>
#include <span>
#include <optional>

[[nodiscard]] std::optional<uint16_t> parse_frame_cpp(std::span<const uint8_t> frame) noexcept {
    if (frame.size() < 4) {
        return std::nullopt;
    }
    uint16_t crc = static_cast<uint16_t>((frame[frame.size() - 2] << 8) | frame.back());
    return crc;
}
