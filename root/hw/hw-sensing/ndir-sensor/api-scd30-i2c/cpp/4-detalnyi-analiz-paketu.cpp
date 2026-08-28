#include <cstdint>
#include <array>
#include <span>
#include <optional>
#include <bit>

namespace sensirion::scd30 {

struct MeasurementResult {
    float co2_ppm{0.0f};
    float temperature_c{0.0f};
    float relative_humidity_pct{0.0f};
};

/**
 * @brief Безпечний розбір 18-байтового фрейму вимірювання за стандартом C++20.
 */
[[nodiscard]] std::optional<MeasurementResult> unpack_measurement_frame(
    std::span<const uint8_t, 18> rx_buf) noexcept 
{
    // Валідація 6 пар даних і відповідних CRC-8 байтів
    for (size_t i = 0; i < 6; ++i) {
        const auto word_slice = rx_buf.subspan(i * 3, 2);
        const uint8_t expected_crc = rx_buf[i * 3 + 2];
        if (compute_crc8(word_slice) != expected_crc) {
            return std::nullopt;
        }
    }

    const auto extract_float = [](const uint8_t* p) noexcept -> float {
        const uint32_t raw_bits = (static_cast<uint32_t>(p[0]) << 24) |
                                  (static_cast<uint32_t>(p[1]) << 16) |
                                  (static_cast<uint32_t>(p[3]) << 8)  |
                                  (static_cast<uint32_t>(p[4]));
        return std::bit_cast<float>(raw_bits);
    };

    MeasurementResult res{};
    res.co2_ppm = extract_float(&rx_buf[0]);
    res.temperature_c = extract_float(&rx_buf[6]);
    res.relative_humidity_pct = extract_float(&rx_buf[12]);

    return res;
}

} // namespace sensirion::scd30
