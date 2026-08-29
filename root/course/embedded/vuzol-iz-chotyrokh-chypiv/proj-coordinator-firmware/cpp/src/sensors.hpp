#pragma once

// Два чипи на шині I2C: барометричний BME280 і термокомпенсований
// годинник DS3231. Обидва повертають std::expected — виклику доводиться
// подивитися на результат, мовчки прийняти нулі не вийде.

#include <cstdint>
#include <expected>

#include "i2c.hpp"

namespace node {

enum class SensorError : std::uint8_t {
    Bus,            // шина не відповіла
    WrongId,        // на адресі сидить не той чип
    NotCalibrated,  // калібрування не прочитане
    AdcInvalid,     // сирий відлік — значення після скидання або за межею
    BadTime,        // BCD-регістри годинника побиті
};

template <typename T>
using SensorResult = std::expected<T, SensorError>;

// ── BME280 ───────────────────────────────────────────────────────────────
class Bme280 {
public:
    struct Sample {
        std::int32_t  temperatureC100;  // °C × 100
        std::uint32_t pressurePa100;    // Па × 100
        std::uint32_t humidityRh1024;   // %RH × 1024
    };

    explicit Bme280(I2cMaster& bus) noexcept : bus_{bus} {}

    SensorResult<void> begin() noexcept;

    // Вимірювання розділене надвоє: запуск і забір. Між ними ~10 мс, і ці
    // 10 мс головний цикл займається чим завгодно, а не чекає в while.
    SensorResult<void> startMeasurement() noexcept;
    SensorResult<bool> ready() noexcept;
    SensorResult<Sample> read() noexcept;

private:
    struct Calibration {
        std::uint16_t t1{}; std::int16_t t2{}, t3{};
        std::uint16_t p1{}; std::int16_t p2{}, p3{}, p4{}, p5{}, p6{}, p7{}, p8{}, p9{};
        std::uint8_t  h1{}; std::int16_t h2{}; std::uint8_t h3{};
        std::int16_t  h4{}, h5{}; std::int8_t h6{};
    };

    SensorResult<void> loadCalibration() noexcept;
    std::int32_t  compensateTemperature(std::int32_t adc) noexcept;
    std::uint32_t compensatePressure(std::int32_t adc) const noexcept;
    std::uint32_t compensateHumidity(std::int32_t adc) const noexcept;

    static constexpr std::uint8_t kAddress = 0x76;

    I2cMaster&   bus_;
    Calibration  cal_{};
    std::int32_t tFine_{0};
    bool         calibrated_{false};
};

// ── DS3231 ───────────────────────────────────────────────────────────────
class Ds3231 {
public:
    struct Time {
        std::uint32_t unix;
        bool oscillatorValid;   // false — генератор колись зупинявся
    };

    explicit Ds3231(I2cMaster& bus) noexcept : bus_{bus} {}

    // Налаштовує меандр 1 Гц на INT/SQW — саме він будить вузол зі сну.
    SensorResult<void> begin() noexcept;
    SensorResult<Time> now() noexcept;

private:
    static constexpr std::uint8_t kAddress = 0x68;

    I2cMaster& bus_;
};

}  // namespace node
