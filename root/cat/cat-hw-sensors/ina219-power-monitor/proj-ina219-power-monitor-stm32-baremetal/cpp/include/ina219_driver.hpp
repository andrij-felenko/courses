#pragma once

#include <cstdint>
#include <cstddef>
#include <cmath>

#if __has_include("stm32f4xx_hal.h")
#include "stm32f4xx_hal.h"
#elif __has_include("stm32_hal.h")
#include "stm32_hal.h"
#else
// Автономні визначення типів STM32 HAL для безпечної компіляції
typedef enum {
    HAL_OK = 0x00U,
    HAL_ERROR = 0x01U,
    HAL_BUSY = 0x02U,
    HAL_TIMEOUT = 0x03U
} HAL_StatusTypeDef;

typedef struct {
    uint32_t State;
    uint32_t ErrorCode;
} I2C_HandleTypeDef;

typedef struct {
    uint32_t State;
} UART_HandleTypeDef;

#ifndef I2C_MEMADD_SIZE_8BIT
#define I2C_MEMADD_SIZE_8BIT 0x00000001U
#endif

#endif

namespace ina219 {

/// Стандартна 7-бітна адреса I2C для пристрою INA219 (A0=GND, A1=GND)
inline constexpr uint8_t kDefaultI2cAddress = 0x40;

/**
 * @brief Перелічення регістрів монітора живлення INA219
 */
enum class Ina219Register : uint8_t {
    Config       = 0x00,
    ShuntVoltage = 0x01,
    BusVoltage   = 0x02,
    Power        = 0x03,
    Current      = 0x04,
    Calibration  = 0x05
};

/**
 * @brief Діапазон вимірюваної напруги шини (Bus Voltage Range)
 */
enum class Ina219BusVoltageRange : uint16_t {
    Range_16V = 0x0000, // 0 - 16V FSR
    Range_32V = 0x2000  // 0 - 32V FSR (за замовчуванням)
};

/**
 * @brief Коефіцієнт підсилення підсилювача Shunt PGA (PGA Gain)
 */
enum class Ina219PgaGain : uint16_t {
    Gain_1_40mV  = 0x0000, // ±40 mV діапазон
    Gain_2_80mV  = 0x0800, // ±80 mV діапазон
    Gain_4_160mV = 0x1000, // ±160 mV діапазон
    Gain_8_320mV = 0x1800  // ±320 mV діапазон (за замовчуванням)
};

/**
 * @brief Налаштування роздільної здатності та усереднення вибірок АЦП
 */
enum class Ina219AdcResolution : uint16_t {
    Res_9bit_84us    = 0x0000,
    Res_10bit_148us  = 0x0080,
    Res_11bit_276us  = 0x0100,
    Res_12bit_532us  = 0x0180, // 12-біт, 1 вибірка (за замовчуванням)
    Samples_2_1ms    = 0x0480, // 2 вибірки
    Samples_4_2ms    = 0x0500, // 4 вибірки
    Samples_8_4ms    = 0x0580, // 8 вибірок
    Samples_16_8ms   = 0x0600, // 16 вибірок
    Samples_32_17ms  = 0x0680, // 32 вибірки
    Samples_64_34ms  = 0x0700, // 64 вибірки
    Samples_128_68ms = 0x0780  // 128 вибірок
};

/**
 * @brief Режими роботи INA219 (Operating Mode)
 */
enum class Ina219Mode : uint16_t {
    PowerDown              = 0x0000,
    ShuntVoltageTriggered  = 0x0001,
    BusVoltageTriggered    = 0x0002,
    ShuntAndBusTriggered   = 0x0003,
    AdcOff                 = 0x0004,
    ShuntVoltageContinuous = 0x0005,
    BusVoltageContinuous   = 0x0006,
    ShuntAndBusContinuous  = 0x0007  // Неперервні вимірювання (за замовчуванням)
};

// Конфігураційні бітові маски INA219
inline constexpr uint16_t kConfigResetMask        = 0x8000;
inline constexpr uint16_t kBusVoltageCnvrMask     = 0x0002; // Прапорець готовності конверсії (CNVR)
inline constexpr uint16_t kBusVoltageOvfMask      = 0x0001; // Прапорець математичного переповнення (OVF)

/**
 * @brief RAII-обгортка для безпечної роботи з шиною I2C STM32.
 * Автоматизує захоплення/звільнення периферії та забезпечує скидання шини при таймаутах.
 */
class I2cBusGuard {
public:
    explicit I2cBusGuard(I2C_HandleTypeDef* hi2c, uint16_t dev_addr, uint32_t timeout_ms = 100);
    ~I2cBusGuard();

    I2cBusGuard(const I2cBusGuard&) = delete;
    I2cBusGuard& operator=(const I2cBusGuard&) = delete;

    I2cBusGuard(I2cBusGuard&& other) noexcept;
    I2cBusGuard& operator=(I2cBusGuard&& other) noexcept;

    HAL_StatusTypeDef writeRegister(uint8_t reg_addr, uint16_t value);
    HAL_StatusTypeDef readRegister(uint8_t reg_addr, uint16_t& value);

    [[nodiscard]] bool hasError() const noexcept { return last_status_ != HAL_OK; }
    [[nodiscard]] HAL_StatusTypeDef getStatus() const noexcept { return last_status_; }

private:
    void recoverBus();

    I2C_HandleTypeDef* hi2c_{nullptr};
    uint16_t dev_addr_{0};
    uint32_t timeout_ms_{100};
    HAL_StatusTypeDef last_status_{HAL_OK};
    bool active_{true};
};

/**
 * @brief Клас-драйвер монітора струму й напруги INA219
 */
class Ina219Driver {
public:
    /**
     * @brief Конструктор класу Ina219Driver
     * @param hi2c Вказівник на інтерфейсний хендл STM32 I2C
     * @param i2c_addr 7-бітна I2C адреса сенсора
     */
    explicit Ina219Driver(I2C_HandleTypeDef* hi2c, uint8_t i2c_addr = kDefaultI2cAddress);

    /**
     * @brief Ініціалізація драйвера з калібруванням під конкретне навантаження
     * @param r_shunt_ohms Опір вимірювального шунта (Ом)
     * @param max_current_A Очікуваний максимальний струм (А)
     */
    HAL_StatusTypeDef init(float r_shunt_ohms = 0.1f, float max_current_A = 3.2f);

    /**
     * @brief Апаратне/програмне скидання налаштувань INA219 (Reset)
     */
    HAL_StatusTypeDef reset();

    /**
     * @brief Конфігурування режимів вимірювання, діапазону та усереднення АЦП
     */
    HAL_StatusTypeDef configure(
        Ina219BusVoltageRange bus_range = Ina219BusVoltageRange::Range_32V,
        Ina219PgaGain gain = Ina219PgaGain::Gain_8_320mV,
        Ina219AdcResolution bus_adc = Ina219AdcResolution::Res_12bit_532us,
        Ina219AdcResolution shunt_adc = Ina219AdcResolution::Res_12bit_532us,
        Ina219Mode mode = Ina219Mode::ShuntAndBusContinuous
    );

    /**
     * @brief Калібрування сенсора: розрахунок Current LSB, Power LSB та запис в Calibration Register
     */
    HAL_StatusTypeDef calibrate(float r_shunt_ohms, float max_current_A);

    /**
     * @brief Зчитування падіння напруги на шунті (в мілівольтах)
     */
    HAL_StatusTypeDef readShuntVoltage(float& voltage_mV);

    /**
     * @brief Зчитування напруги шини живлення (у вольтах)
     */
    HAL_StatusTypeDef readBusVoltage(float& voltage_V);

    /**
     * @brief Зчитування струму навантаження (в міліамперах)
     */
    HAL_StatusTypeDef readCurrent(float& current_mA);

    /**
     * @brief Зчитування споживаної потужності (в міліватах)
     */
    HAL_StatusTypeDef readPower(float& power_mW);

    /**
     * @brief Комплексне неблокуюче зчитування всіх вимірюваних параметрів живлення
     */
    HAL_StatusTypeDef readAll(float& bus_voltage_V, float& shunt_voltage_mV, float& current_mA, float& power_mW);

    /**
     * @brief Неблокуюча перевірка прапорця готовності конверсії АЦП (CNVR)
     */
    HAL_StatusTypeDef checkConversionReady(bool& is_ready);

    /**
     * @brief Неблокуюча перевірка прапорця математичного переповнення (OVF)
     */
    HAL_StatusTypeDef checkOverflow(bool& is_overflow);

    // Інформаційні геттери інкапсульованих параметрів
    [[nodiscard]] float getCurrentLsb() const noexcept { return current_lsb_A_; }
    [[nodiscard]] float getPowerLsb() const noexcept { return power_lsb_W_; }
    [[nodiscard]] uint16_t getCalibrationValue() const noexcept { return cal_reg_val_; }

private:
    HAL_StatusTypeDef writeRegister(Ina219Register reg, uint16_t value);
    HAL_StatusTypeDef readRegister(Ina219Register reg, uint16_t& value);
    void calculateLsbAndCal();

    I2C_HandleTypeDef* hi2c_{nullptr};
    uint16_t i2c_addr_shifted_{0}; // 8-бітна адреса для STM32 HAL (i2c_addr << 1)
    float r_shunt_ohms_{0.1f};
    float max_current_A_{3.2f};
    float current_lsb_A_{0.0f};
    float power_lsb_W_{0.0f};
    uint16_t config_reg_val_{0x399F};
    uint16_t cal_reg_val_{0};
};

} // namespace ina219
