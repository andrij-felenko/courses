#pragma once

/*
 * Цілочисельна компенсація BMP280: чиста математика без шини.
 * Саме цю частину переносять між платформами й перевіряють еталоном.
 */

#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

namespace bmp280 {

enum class Error {
    bus,                  // транзакція I2C/SPI не відбулася
    wrong_chip,           // на адресі сидить не BMP280
    bad_calibration,      // байти OTP не схожі на дані
    timeout,              // датчик не звільнив статус
    no_measurement,       // у регістрах ще стоїть 0x80000
    degenerate_calibration// var1 == 0: ділення на нуль у поліномі
};

inline constexpr std::size_t calibration_bytes = 24;
inline constexpr std::size_t frame_bytes       = 6;

// Значення 20-бітного поля після скидання.
inline constexpr std::int32_t raw_reset_value = 0x80000;

// Заводські коефіцієнти з OTP-пам'яті кристала (0x88..0x9F).
struct Calibration {
    std::uint16_t dig_T1{};
    std::int16_t  dig_T2{};
    std::int16_t  dig_T3{};
    std::uint16_t dig_P1{};
    std::int16_t  dig_P2{};
    std::int16_t  dig_P3{};
    std::int16_t  dig_P4{};
    std::int16_t  dig_P5{};
    std::int16_t  dig_P6{};
    std::int16_t  dig_P7{};
    std::int16_t  dig_P8{};
    std::int16_t  dig_P9{};
};

// Розпакована пара 20-бітних відліків АЦП.
struct RawSample {
    std::int32_t pressure{};
    std::int32_t temperature{};
};

struct Measurement {
    std::int32_t  temperature_centi_c{}; // 2508 = 25.08 °C
    std::uint32_t pressure_q24_8{};      // Паскалі у форматі Q24.8
    std::int32_t  t_fine{};

    [[nodiscard]] constexpr std::uint32_t pressure_pa() const noexcept {
        return pressure_q24_8 >> 8;
    }
};

[[nodiscard]] std::expected<Calibration, Error>
parse_calibration(std::span<const std::uint8_t, calibration_bytes> raw) noexcept;

[[nodiscard]] std::expected<RawSample, Error>
unpack_frame(std::span<const std::uint8_t, frame_bytes> raw) noexcept;

// Тримає калібрування й t_fine між двома етапами компенсації.
class Compensator {
public:
    explicit constexpr Compensator(const Calibration& calib) noexcept
        : calib_{calib} {}

    // Соті градуса Цельсія; побічно оновлює t_fine.
    std::int32_t temperature(std::int32_t adc_t) noexcept;

    // Вимагає вже порахованої t_fine — тому лише після temperature().
    [[nodiscard]] std::expected<std::uint32_t, Error>
    pressure_q24_8(std::int32_t adc_p) const noexcept;

    // Обидва етапи в правильному порядку.
    [[nodiscard]] std::expected<Measurement, Error> apply(RawSample sample) noexcept;

    [[nodiscard]] constexpr std::int32_t t_fine() const noexcept { return t_fine_; }
    [[nodiscard]] constexpr const Calibration& calibration() const noexcept { return calib_; }

private:
    Calibration  calib_{};
    std::int32_t t_fine_{0};
};

} // namespace bmp280
