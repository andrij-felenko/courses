#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <array>

struct SensorData {
    int16_t temperature_centi_c;
    uint16_t pressure_deci_hpa;
    uint16_t voltage_mv;
    uint8_t flags;

    [[nodiscard]] constexpr double get_temperature_c() const noexcept {
        return temperature_centi_c * 0.01;
    }

    [[nodiscard]] constexpr double get_pressure_hpa() const noexcept {
        return pressure_deci_hpa * 0.1;
    }
};

enum class UnpackError : uint8_t {
    BufferTooShort,
    InvalidReservedByte
};

class TelemetryCodec {
public:
    static constexpr size_t PayloadSize = 8;

    [[nodiscard]] static constexpr std::expected<SensorData, UnpackError> unpack(
        std::span<const uint8_t> payload) noexcept 
    {
        if (payload.size() < PayloadSize) {
            return std::unexpected(UnpackError::BufferTooShort);
        }

        SensorData data{
            .temperature_centi_c = static_cast<int16_t>(
                static_cast<uint16_t>(payload[0]) | (static_cast<uint16_t>(payload[1]) << 8)
            ),
            .pressure_deci_hpa = static_cast<uint16_t>(
                static_cast<uint16_t>(payload[2]) | (static_cast<uint16_t>(payload[3]) << 8)
            ),
            .voltage_mv = static_cast<uint16_t>(
                static_cast<uint16_t>(payload[4]) | (static_cast<uint16_t>(payload[5]) << 8)
            ),
            .flags = payload[6]
        };

        return data;
    }

    [[nodiscard]] static constexpr std::array<uint8_t, PayloadSize> pack(
        const SensorData& data) noexcept 
    {
        return std::array<uint8_t, PayloadSize>{
            static_cast<uint8_t>(data.temperature_centi_c & 0xFF),
            static_cast<uint8_t>((data.temperature_centi_c >> 8) & 0xFF),
            static_cast<uint8_t>(data.pressure_deci_hpa & 0xFF),
            static_cast<uint8_t>((data.pressure_deci_hpa >> 8) & 0xFF),
            static_cast<uint8_t>(data.voltage_mv & 0xFF),
            static_cast<uint8_t>((data.voltage_mv >> 8) & 0xFF),
            data.flags,
            0x00 // Зарезервований байт вирівнювання
        };
    }
};
