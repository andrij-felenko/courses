// bsp/bme280.hpp — давач мікроклімату BME280.
// Драйвер приймає hal::I2cDevice — мікросхему на абстрактній шині, а не
// контролер I2C1. Тій самій мікросхемі байдуже, чи по той бік апаратний
// контролер STM32, програмна шина на ніжках, чи імітація в модульному тесті.
//
// Купи немає й тут: об'єкт створюється фабрикою за значенням, калібрувальна
// таблиця лежить усередині нього, а std::optional каже, чи вдалося взагалі
// підняти давач.
#pragma once

#include "hal/i2c_device.hpp"

#include <cstdint>
#include <expected>
#include <optional>

namespace bsp {

// Фізичні величини, а не коди АЦП.
struct Environment {
    float temperature_c{0.0F};
    float humidity_rh{0.0F};
    float pressure_hpa{0.0F};
};

class IEnvironmentSensor {
public:
    virtual ~IEnvironmentSensor() = default;

    [[nodiscard]] virtual std::expected<Environment, hal::I2cError> measure() = 0;
};

class Bme280 final : public IEnvironmentSensor {
public:
    // Звіряє ідентифікатор, скидає мікросхему, вичитує калібрувальну
    // таблицю з її ПЗП і ставить передискретизацію ×1.
    [[nodiscard]] static std::optional<Bme280> create(hal::I2cDevice device);

    // Одне вимірювання в режимі forced: давач прокидається, міряє, засинає.
    // Саме цей режим тримає споживання логера на одиницях мікроампер.
    [[nodiscard]] std::expected<Environment, hal::I2cError> measure() override;

private:
    // Індивідуальні коефіцієнти конкретного примірника мікросхеми.
    struct Calibration {
        std::uint16_t t1{0};
        std::int16_t  t2{0}, t3{0};
        std::uint16_t p1{0};
        std::int16_t  p2{0}, p3{0}, p4{0}, p5{0}, p6{0}, p7{0}, p8{0}, p9{0};
        std::uint8_t  h1{0}, h3{0};
        std::int16_t  h2{0}, h4{0}, h5{0};
        std::int8_t   h6{0};
    };

    explicit Bme280(hal::I2cDevice device, const Calibration& calib) noexcept
        : device_{device}, calib_{calib} {}

    [[nodiscard]] static std::expected<Calibration, hal::I2cError>
    read_calibration(const hal::I2cDevice& device);

    [[nodiscard]] std::expected<void, hal::I2cError> wait_conversion();

    // Цілочислові формули з довідника мікросхеми: на ядрах без блока
    // плаваючої коми числа з комою коштують сотні тактів.
    [[nodiscard]] std::int32_t  compensate_temperature(std::int32_t adc_t);
    [[nodiscard]] std::uint32_t compensate_pressure(std::int32_t adc_p) const;
    [[nodiscard]] std::uint32_t compensate_humidity(std::int32_t adc_h) const;

    hal::I2cDevice device_;
    Calibration    calib_{};
    std::int32_t   t_fine_{0};  // спільний проміжок для тиску й вологості
};

} // namespace bsp
