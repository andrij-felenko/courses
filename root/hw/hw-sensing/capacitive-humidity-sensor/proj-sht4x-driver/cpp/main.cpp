#include <cstdint>
#include <cmath>
#include <algorithm>
#include <span>
#include <concepts>
#include <expected>
#include <chrono>

namespace sht4x {

enum class Error : int8_t {
    I2cTransport = -1,
    CrcTemperature = -2,
    CrcHumidity = -3,
    InvalidParameter = -4,
    Timeout = -5
};

enum class Precision : uint8_t {
    High = 0xFD,
    Medium = 0xF6,
    Low = 0xE0
};

enum class HeaterMode : uint8_t {
    HighPower1s   = 0x39, // 200 mW, 1.0 s
    HighPower01s  = 0x32, // 200 mW, 0.1 s
    MedPower1s    = 0x2F, // 110 mW, 1.0 s
    MedPower01s   = 0x24, // 110 mW, 0.1 s
    LowPower1s    = 0x1E, //  20 mW, 1.0 s
    LowPower01s   = 0x15  //  20 mW, 0.1 s
};

struct Metrics {
    float temperature_c;     // °C
    float relative_humidity; // % RH [0..100]
    float dew_point_c;       // °C
    float absolute_hum_gm3;  // г/м³
};

// Концепт апаратної шини I2C
template <typename T>
concept I2cBus = requires(T bus, uint8_t addr, std::span<const uint8_t> wr, std::span<uint8_t> rd) {
    { bus.write(addr, wr) } -> std::same_as<bool>;
    { bus.read(addr, rd) } -> std::same_as<bool>;
    { bus.delay_ms(uint32_t{}) } -> std::same_as<void>;
};

template <I2cBus Bus>
class Sht4xDriver {
public:
    static constexpr uint8_t DefaultAddress = 0x44;

    explicit constexpr Sht4xDriver(Bus& bus, uint8_t address = DefaultAddress) noexcept
        : m_bus(bus), m_address(address) {}

    std::expected<Metrics, Error> sample(Precision prec = Precision::High) {
        return execute_measurement(static_cast<uint8_t>(prec), duration_for_precision(prec));
    }

    std::expected<Metrics, Error> trigger_heater(HeaterMode mode) {
        return execute_measurement(static_cast<uint8_t>(mode), duration_for_heater(mode));
    }

    std::expected<void, Error> reset() {
        constexpr uint8_t cmd = 0x94;
        if (!m_bus.write(m_address, std::span<const uint8_t, 1>{&cmd, 1})) {
            return std::unexpected(Error::I2cTransport);
        }
        m_bus.delay_ms(1);
        return {};
    }

private:
    Bus& m_bus;
    uint8_t m_address;

    static constexpr uint8_t calculate_crc8(std::span<const uint8_t> data) noexcept {
        uint8_t crc = 0xFF;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                crc = (crc & 0x80) ? static_cast<uint8_t>((crc << 1) ^ 0x31) 
                                   : static_cast<uint8_t>(crc << 1);
            }
        }
        return crc;
    }

    static constexpr uint32_t duration_for_precision(Precision p) noexcept {
        switch (p) {
            case Precision::Low:    return 2;
            case Precision::Medium: return 5;
            case Precision::High:
            default:                return 10;
        }
    }

    static constexpr uint32_t duration_for_heater(HeaterMode h) noexcept {
        switch (h) {
            case HeaterMode::HighPower1s:
            case HeaterMode::MedPower1s:
            case HeaterMode::LowPower1s:  return 1100;
            default:                      return 120;
        }
    }

    std::expected<Metrics, Error> execute_measurement(uint8_t cmd, uint32_t delay_ms) {
        if (!m_bus.write(m_address, std::span<const uint8_t, 1>{&cmd, 1})) {
            return std::unexpected(Error::I2cTransport);
        }

        m_bus.delay_ms(delay_ms);

        std::array<uint8_t, 6> raw_buf{};
        if (!m_bus.read(m_address, std::span<uint8_t, 6>{raw_buf})) {
            return std::unexpected(Error::I2cTransport);
        }

        if (calculate_crc8(std::span<const uint8_t>{raw_buf.data(), 2}) != raw_buf[2]) {
            return std::unexpected(Error::CrcTemperature);
        }
        if (calculate_crc8(std::span<const uint8_t>{raw_buf.data() + 3, 2}) != raw_buf[5]) {
            return std::unexpected(Error::CrcHumidity);
        }

        const uint16_t raw_t = (static_cast<uint16_t>(raw_buf[0]) << 8) | raw_buf[1];
        const uint16_t raw_rh = (static_cast<uint16_t>(raw_buf[3]) << 8) | raw_buf[4];

        const float temp = -45.0f + 175.0f * (static_cast<float>(raw_t) / 65535.0f);
        const float rh_raw = -6.0f + 125.0f * (static_cast<float>(raw_rh) / 65535.0f);
        const float rh = std::clamp(rh_raw, 0.0f, 100.0f);

        return compute_metrics(temp, rh);
    }

    static Metrics compute_metrics(float temp_c, float rh_pct) noexcept {
        constexpr float b = 17.62f;
        constexpr float c = 243.12f;

        const float rh_safe = std::max(rh_pct, 0.1f);
        const float gamma = std::log(rh_safe / 100.0f) + (b * temp_c) / (c + temp_c);
        const float dew_point = (c * gamma) / (b - gamma);

        const float p_sat = 6.112f * std::exp((b * temp_c) / (c + temp_c));
        const float p_actual = (rh_safe / 100.0f) * p_sat;
        const float abs_hum = 216.7f * p_actual / (temp_c + 273.15f);

        return Metrics{
            .temperature_c = temp_c,
            .relative_humidity = rh_pct,
            .dew_point_c = dew_point,
            .absolute_hum_gm3 = abs_hum
        };
    }
};

} // namespace sht4x
