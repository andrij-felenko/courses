/**
 * @file Bmp280Driver.hpp
 * @brief Сучасний типобезпечний C++20 драйвер BMP280 з нульовим динамічним виділенням пам'яті.
 */

#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <optional>
#include <array>
#include "Units.hpp"

namespace sf::devices {

/**
 * @brief Коди помилок драйвера пристрою.
 */
enum class DriverError : uint8_t {
    None = 0,
    InvalidDeviceAddress,
    InvalidChipId,
    BusTimeout,
    BusNack,
    CrcMismatch,
    Busy,
    BusLocked,
    CalibrationCorrupted,
    Overflow
};

/**
 * @brief Концепт апаратної шини (I2C / SPI), що підтримує транзакції та DMA.
 */
template <typename T>
concept BusDevice = requires(T bus, uint8_t addr, uint8_t reg, std::span<uint8_t> rx, std::span<const uint8_t> tx) {
    { bus.read(addr, reg, rx) } -> std::same_as<DriverError>;
    { bus.write(addr, reg, tx) } -> std::same_as<DriverError>;
    { bus.readDmaAsync(addr, reg, rx) } -> std::same_as<DriverError>;
    { bus.resetBus() } -> std::same_as<void>;
    { bus.delayMs(uint32_t{}) } -> std::same_as<void>;
};

/**
 * @brief Режими передискретизації АЦП.
 */
enum class OverSampling : uint8_t {
    Skipped = 0x00,
    X1      = 0x01,
    X2      = 0x02,
    X4      = 0x03,
    X8      = 0x04,
    X16     = 0x05
};

/**
 * @brief Режим живлення та вимірювання чипа.
 */
enum class SensorMode : uint8_t {
    Sleep  = 0x00,
    Forced = 0x01,
    Normal = 0x03
};

/**
 * @brief Коефіцієнт IIR фільтрації нелінійностей.
 */
enum class IirFilter : uint8_t {
    Off = 0x00,
    X2  = 0x01,
    X4  = 0x02,
    X8  = 0x03,
    X16 = 0x04
};

/**
 * @brief Структура вибірки фізичних величин з міткою часу.
 */
struct SensorSample {
    units::Celsius temperature;
    units::Pascals pressure;
    uint32_t       timestampUs{0};
    bool           isValid{false};
};

/**
 * @brief Калібрувальні коефіцієнти NVM.
 */
struct CalibrationData {
    uint16_t dig_T1{0};
    int16_t  dig_T2{0};
    int16_t  dig_T3{0};
    uint16_t dig_P1{0};
    int16_t  dig_P2{0};
    int16_t  dig_P3{0};
    int16_t  dig_P4{0};
    int16_t  dig_P5{0};
    int16_t  dig_P6{0};
    int16_t  dig_P7{0};
    int16_t  dig_P8{0};
    int16_t  dig_P9{0};
};

/**
 * @brief Шаблонний C++20 драйвер BMP280.
 * @tparam BusImpl Реалізація шини, яка відповідає концепту BusDevice.
 */
template <BusDevice BusImpl>
class Bmp280Driver {
public:
    static constexpr uint8_t DefaultI2cAddress = 0x76;
    static constexpr uint8_t ChipIdExpected    = 0x58;
    static constexpr size_t  BurstReadSize     = 6;

    explicit Bmp280Driver(BusImpl& bus, uint8_t devAddr = DefaultI2cAddress) noexcept
        : bus_(bus), devAddr_(devAddr) {}

    [[nodiscard]] DriverError initialize() noexcept;
    [[nodiscard]] DriverError configure(OverSampling osrT, OverSampling osrP, SensorMode mode, IirFilter filter) noexcept;

    [[nodiscard]] std::optional<SensorSample> readSynchronous() noexcept;
    [[nodiscard]] DriverError startDmaRead() noexcept;
    void onDmaComplete() noexcept;

    [[nodiscard]] std::optional<SensorSample> lastSample() const noexcept {
        if (!lastSample_.isValid) return std::nullopt;
        return lastSample_;
    }

    [[nodiscard]] DriverError recover() noexcept;
    [[nodiscard]] uint32_t errorCount() const noexcept { return errorCount_; }

private:
    [[nodiscard]] DriverError readCalibrationTable() noexcept;
    [[nodiscard]] SensorSample compensate(std::span<const uint8_t, BurstReadSize> raw) noexcept;

    BusImpl& bus_;
    uint8_t devAddr_;
    CalibrationData calib_{};
    int32_t tFine_{0};
    std::array<uint8_t, BurstReadSize> dmaBuffer_{};
    SensorSample lastSample_{};
    uint32_t errorCount_{0};
    bool isBusyDma_{false};
};

} // namespace sf::devices

#include "Bmp280Driver.tpp"
