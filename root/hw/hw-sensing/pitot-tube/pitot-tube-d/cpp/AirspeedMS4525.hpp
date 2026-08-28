// AirspeedMS4525.hpp — Сучасний типізований C++20 драйвер вимірювання швидкості
#pragma once

#include <cstdint>
#include <concepts>
#include <span>
#include <expected>
#include <cmath>
#include <algorithm>

namespace Sensing {

enum class AirspeedError : uint8_t {
    BusError,
    StaleData,
    SensorFault,
    InvalidConfiguration,
    CalibrationFailed
};

struct AirspeedSample {
    float indicated_airspeed_mps{0.0f};  // IAS (м/с)
    float true_airspeed_mps{0.0f};       // TAS (м/с)
    float dynamic_pressure_pa{0.0f};     // Фільтрований перепад тиску (Па)
    float raw_pressure_pa{0.0f};         // Миттєвий тиск без згладжування (Па)
    float sensor_temp_c{0.0f};           // Температура кристала (°C)
    float air_density_kgm3{1.225f};      // Дійсна густина повітря (кг/м³)
};

template <typename I2cDriver>
concept I2cMaster = requires(I2cDriver driver, uint8_t addr, std::span<uint8_t> buffer) {
    { driver.read(addr, buffer) } -> std::same_as<bool>;
};

template <I2cMaster Bus>
class AirspeedSensor {
public:
    static constexpr float RHO_SEA_LEVEL = 1.2250f;      // кг/м³ (ISA)
    static constexpr float GAS_CONST_AIR = 287.058f;     // Дж/(кг·К)
    static constexpr float PSI_TO_PASCAL = 6894.757f;
    static constexpr uint8_t DEFAULT_ADDR = 0x28;

    explicit constexpr AirspeedSensor(Bus& bus, 
                                     uint8_t i2c_address = DEFAULT_ADDR, 
                                     float psi_span = 1.0f,
                                     float lpf_alpha = 0.20f) noexcept
        : bus_(bus), 
          address_(i2c_address), 
          psi_span_(psi_span), 
          lpf_alpha_(std::clamp(lpf_alpha, 0.01f, 1.0f)) {}

    [[nodiscard]] std::expected<void, AirspeedError> calibrateZero(size_t sample_count = 100) {
        float accumulated_pressure = 0.0f;
        size_t valid_readings = 0;
        uint8_t buffer[4]{};

        for (size_t i = 0; i < sample_count; ++i) {
            if (!bus_.read(address_, buffer)) {
                return std::unexpected(AirspeedError::BusError);
            }
            const uint8_t status = (buffer[0] >> 6) & 0x03;
            if (status == 0x00 || status == 0x02) {
                const auto raw_p = static_cast<uint16_t>(((buffer[0] & 0x3F) << 8) | buffer[1]);
                const float p_psi = ((static_cast<float>(raw_p) - COUNT_MIN) * (2.0f * psi_span_) / COUNT_SPAN) - psi_span_;
                accumulated_pressure += (p_psi * PSI_TO_PASCAL);
                ++valid_readings;
            }
        }

        if (valid_readings < (sample_count / 2)) {
            return std::unexpected(AirspeedError::CalibrationFailed);
        }

        zero_offset_pa_ = accumulated_pressure / static_cast<float>(valid_readings);
        filtered_pressure_pa_ = 0.0f;
        return {};
    }

    [[nodiscard]] std::expected<AirspeedSample, AirspeedError> update(
        float ambient_static_pa = 101325.0f, 
        float ambient_temperature_c = 15.0f) noexcept 
    {
        uint8_t buffer[4]{};
        if (!bus_.read(address_, buffer)) {
            return std::unexpected(AirspeedError::BusError);
        }

        const uint8_t status_bits = (buffer[0] >> 6) & 0x03;
        if (status_bits == 0x03) return std::unexpected(AirspeedError::SensorFault);
        if (status_bits == 0x02) return std::unexpected(AirspeedError::StaleData);

        // 1. Декодування пакетів
        const auto raw_press = static_cast<uint16_t>(((buffer[0] & 0x3F) << 8) | buffer[1]);
        const auto raw_temp  = static_cast<uint16_t>((buffer[2] << 3) | (buffer[3] >> 5));

        // 2. Фізичні величини
        const float p_psi = ((static_cast<float>(raw_press) - COUNT_MIN) * (2.0f * psi_span_) / COUNT_SPAN) - psi_span_;
        const float instant_p_pa = (p_psi * PSI_TO_PASCAL) - zero_offset_pa_;
        const float sensor_temp_c = ((static_cast<float>(raw_temp) * 200.0f) / 2047.0f) - 50.0f;

        // 3. Відсікання від'ємного шуму та фільтрація
        const float non_negative_p = std::max(0.0f, instant_p_pa);
        filtered_pressure_pa_ += lpf_alpha_ * (non_negative_p - filtered_pressure_pa_);

        // 4. Густина повітря
        const float static_p = (ambient_static_pa > 30000.0f) ? ambient_static_pa : 101325.0f;
        const float temp_k = (ambient_temperature_c > -100.0f) ? (ambient_temperature_c + 273.15f) : (sensor_temp_c + 273.15f);
        const float actual_density = static_p / (GAS_CONST_AIR * temp_k);

        // 5. Розрахунок швидкостей
        AirspeedSample sample{
            .indicated_airspeed_mps = std::sqrt((2.0f * filtered_pressure_pa_) / RHO_SEA_LEVEL),
            .true_airspeed_mps = (actual_density > 0.1f) 
                                 ? std::sqrt((2.0f * filtered_pressure_pa_) / actual_density) 
                                 : std::sqrt((2.0f * filtered_pressure_pa_) / RHO_SEA_LEVEL),
            .dynamic_pressure_pa = filtered_pressure_pa_,
            .raw_pressure_pa = instant_p_pa,
            .sensor_temp_c = sensor_temp_c,
            .air_density_kgm3 = actual_density
        };

        return sample;
    }

    void setZeroOffset(float offset_pa) noexcept { zero_offset_pa_ = offset_pa; }
    [[nodiscard]] float zeroOffset() const noexcept { return zero_offset_pa_; }

private:
    static constexpr float COUNT_MIN = 1638.0f;   // 10% від 16383
    static constexpr float COUNT_MAX = 14745.0f;  // 90% від 16383
    static constexpr float COUNT_SPAN = COUNT_MAX - COUNT_MIN;

    Bus& bus_;
    uint8_t address_;
    float psi_span_;
    float lpf_alpha_;
    float zero_offset_pa_{0.0f};
    float filtered_pressure_pa_{0.0f};
};

} // namespace Sensing
