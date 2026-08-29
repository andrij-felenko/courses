// bsp/bsp_bme280.hpp — драйвер давача мікроклімату.
// Залежить лише від hal::II2cBus. Вендорного stm32f4xx_hal.h тут бути не може:
// одне таке включення привʼязує драйвер до одного чипа назавжди.
#pragma once

#include <cstdint>
#include <expected>
#include <optional>

#include "hal/hal_i2c.hpp"

namespace bsp {

struct SensorReading {
    float temperature_c{0.0F};
    float humidity_percent{0.0F};
    float pressure_hpa{0.0F};
};

enum class Bme280Error : std::uint8_t {
    Bus,              // Шина не відповіла
    WrongChipId,      // На адресі сидить не BME280
    BadCalibration,   // Сторінка калібрування порожня або побита
    NotReady,         // Чип не завершив перенесення NVM за відведені спроби
};

class Bme280 {
public:
    static constexpr std::uint8_t kPrimaryAddress = 0x76;    // SDO до землі
    static constexpr std::uint8_t kSecondaryAddress = 0x77;  // SDO до живлення

    explicit Bme280(hal::II2cBus& bus, std::uint8_t address = kPrimaryAddress) noexcept
        : bus_(bus), address_(address)
    {
    }

    // Перевірити ідентифікатор, зчитати калібрування, перевести чип у робочий режим.
    // Той самий виклик піднімає давач після скидання живлення.
    std::expected<void, Bme280Error> initialize();

    // std::nullopt означає «даних немає»: помилка шини або вибірки ще не було.
    // Сміттєві байти буфера в математику не потрапляють ніколи.
    std::optional<SensorReading> read();

    std::optional<hal::I2cError> last_bus_error() const noexcept { return last_bus_error_; }

private:
    // Коефіцієнти компенсації з довідки Bosch: імена збережено навмисно,
    // щоб формули читалися поруч із першоджерелом.
    struct Calibration {
        std::uint16_t t1{0};
        std::int16_t t2{0}, t3{0};
        std::uint16_t p1{0};
        std::int16_t p2{0}, p3{0}, p4{0}, p5{0}, p6{0}, p7{0}, p8{0}, p9{0};
        std::uint8_t h1{0}, h3{0};
        std::int16_t h2{0}, h4{0}, h5{0};
        std::int8_t h6{0};
    };

    std::expected<void, Bme280Error> load_calibration();
    std::expected<void, Bme280Error> configure_chip();

    float compensate_temperature(std::int32_t adc_t);
    float compensate_pressure(std::int32_t adc_p) const;
    float compensate_humidity(std::int32_t adc_h) const;

    hal::II2cBus& bus_;
    std::uint8_t address_;
    std::optional<hal::I2cError> last_bus_error_{};
    Calibration calib_{};
    float t_fine_{0.0F};  // Спільна проміжна величина для тиску й вологості
};

}  // namespace bsp
