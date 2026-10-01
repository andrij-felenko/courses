#pragma once

#include "stm32f4xx_hal.h"
#include <cstdint>
#include <array>
#include <span>
#include <cstddef>

namespace Sensors {

/**
 * @brief Діапазони вимірювання прискорення ADXL345.
 */
enum class Range : uint8_t {
    Range_2g  = 0x00,
    Range_4g  = 0x01,
    Range_8g  = 0x02,
    Range_16g = 0x03
};

/**
 * @brief Частота вихідних даних (Output Data Rate - ODR).
 */
enum class DataRate : uint8_t {
    Rate_12_5Hz = 0x07,
    Rate_25Hz   = 0x08,
    Rate_50Hz   = 0x09,
    Rate_100Hz  = 0x0A,
    Rate_200Hz  = 0x0B,
    Rate_400Hz  = 0x0C,
    Rate_800Hz  = 0x0D,
    Rate_1600Hz = 0x0E,
    Rate_3200Hz = 0x0F
};

/**
 * @brief Режими роботи буфера FIFO ADXL345.
 */
enum class FifoMode : uint8_t {
    Bypass  = 0x00,
    Fifo    = 0x40,
    Stream  = 0x80,
    Trigger = 0xC0
};

/**
 * @brief Структура для збереження 3-осьового відліку прискорення.
 */
struct AccelSample {
    int16_t x{0};
    int16_t y{0};
    int16_t z{0};

    // Масштабний коефіцієнт для Full Resolution режиму (~3.9 mg/LSB)
    static constexpr float FullResScaleG = 0.00390625f; // 1.0 / 256.0 g/LSB
    static constexpr float GravityAccel = 9.80665f;     // m/s^2

    [[nodiscard]] constexpr float xG() const noexcept { return static_cast<float>(x) * FullResScaleG; }
    [[nodiscard]] constexpr float yG() const noexcept { return static_cast<float>(y) * FullResScaleG; }
    [[nodiscard]] constexpr float zG() const noexcept { return static_cast<float>(z) * FullResScaleG; }

    [[nodiscard]] constexpr float xMs2() const noexcept { return xG() * GravityAccel; }
    [[nodiscard]] constexpr float yMs2() const noexcept { return yG() * GravityAccel; }
    [[nodiscard]] constexpr float zMs2() const noexcept { return zG() * GravityAccel; }
};

/**
 * @brief Клас RAII-обгортки для керування виводом Chip Select (CS).
 */
class CsPinGuard {
public:
    CsPinGuard(GPIO_TypeDef* port, uint16_t pin) noexcept
        : port_(port), pin_(pin) {
        if (port_) {
            HAL_GPIO_WritePin(port_, pin_, GPIO_PIN_RESET);
        }
    }

    ~CsPinGuard() noexcept {
        if (port_) {
            HAL_GPIO_WritePin(port_, pin_, GPIO_PIN_SET);
        }
    }

    CsPinGuard(const CsPinGuard&) = delete;
    CsPinGuard& operator=(const CsPinGuard&) = delete;
    CsPinGuard(CsPinGuard&&) = delete;
    CsPinGuard& operator=(CsPinGuard&&) = delete;

private:
    GPIO_TypeDef* port_;
    uint16_t pin_;
};

/**
 * @brief Драйвер акселерометра ADXL345 із підтримкою SPI DMA та переривань EXTI.
 */
class Adxl345DmaDriver {
public:
    static constexpr uint8_t ExpectedDevId = 0xE5;
    static constexpr std::size_t MaxFifoDepth = 32;
    static constexpr std::size_t SampleSizeBytes = 6;
    // Розмір DMA буфера: 1 байт команди + (32 кадрів * 6 байтів) = 193 байти
    static constexpr std::size_t DmaBufferSize = 1 + (MaxFifoDepth * SampleSizeBytes);

    Adxl345DmaDriver(SPI_HandleTypeDef* hspi,
                     GPIO_TypeDef* csPort,
                     uint16_t csPin,
                     uint16_t int1Pin) noexcept;

    /**
     * @brief Етап 1: Конфігурування регістрів акселерометра та перевірка DEVID.
     */
    [[nodiscard]] bool configure(Range range = Range::Range_16g,
                                 DataRate rate = DataRate::Rate_100Hz,
                                 uint8_t watermark = 16);

    /**
     * @brief Етап 2: Увімкнення режиму вимірювання (Power Mode).
     */
    [[nodiscard]] bool start();

    /**
     * @brief Зупинка вимірювань (перехід у Standby).
     */
    [[nodiscard]] bool stop();

    /**
     * @brief Обробник переривання GPIO EXTI (викликається з HAL_GPIO_EXTI_Callback).
     */
    void onGpioExti(uint16_t gpioPin) noexcept;

    /**
     * @brief Зворотний виклик завершення SPI DMA (викликається з HAL_SPI_TxRxCpltCallback).
     */
    void onSpiTxRxCplt() noexcept;

    /**
     * @brief Перевірка наявності нових даних від DMA.
     */
    [[nodiscard]] bool hasNewData() const noexcept { return dataReady_; }

    /**
     * @brief Отримання зчитованого пакету вибірок у вигляді std::span.
     */
    [[nodiscard]] std::span<const AccelSample> getSamples() noexcept;

    /**
     * @brief Скидання прапорця готовності даних.
     */
    void clearDataReady() noexcept { dataReady_ = false; }

    /**
     * @brief Перевірка, чи активна в даний момент транзакція DMA.
     */
    [[nodiscard]] bool isBusy() const noexcept { return transferActive_; }

private:
    enum Register : uint8_t {
        RegDevId      = 0x00,
        RegBwRate     = 0x2C,
        RegPowerCtl   = 0x2D,
        RegIntEnable  = 0x2E,
        RegIntMap     = 0x2F,
        RegIntSource  = 0x30,
        RegDataFormat = 0x31,
        RegDataX0     = 0x32,
        RegFifoCtl    = 0x38,
        RegFifoStatus = 0x39
    };

    static constexpr uint8_t SpiReadBit  = 0x80;
    static constexpr uint8_t SpiBurstBit = 0x40;

    void selectCs() noexcept;
    void deselectCs() noexcept;

    bool writeRegister(uint8_t reg, uint8_t value);
    uint8_t readRegister(uint8_t reg);

    SPI_HandleTypeDef* hspi_;
    GPIO_TypeDef* csPort_;
    uint16_t csPin_;
    uint16_t int1Pin_;

    uint8_t watermarkLevel_{16};
    volatile bool transferActive_{false};
    volatile bool dataReady_{false};

    std::size_t currentSampleCount_{0};

    // Буфери DMA (TX та RX) з вирівнюванням для DMA контролера
    alignas(4) std::array<uint8_t, DmaBufferSize> txBuffer_{};
    alignas(4) std::array<uint8_t, DmaBufferSize> rxBuffer_{};

    // Масив зчитованих та розпарсених структур AccelSample
    std::array<AccelSample, MaxFifoDepth> samples_{};
};

} // namespace Sensors
