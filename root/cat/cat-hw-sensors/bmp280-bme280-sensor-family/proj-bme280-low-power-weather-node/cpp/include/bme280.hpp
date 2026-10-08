#ifndef BME280_HPP
#define BME280_HPP

#include "i2c_bus.hpp"
#include <cstdint>
#include <cstddef>

/**
 * @brief Структура фабричних калібрувальних коефіцієнтів, зчитаних із NVRAM BME280.
 */
struct Bme280CalibData {
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

    uint8_t  dig_H1{0};
    int16_t  dig_H2{0};
    uint8_t  dig_H3{0};
    int16_t  dig_H4{0};
    int16_t  dig_H5{0};
    int8_t   dig_H6{0};
};

/**
 * @brief Контейнер для збереження розрахованих компенсованих показників мікроклімату.
 */
struct Bme280Data {
    double temperature_c{0.0}; // Температура в градусах Цельсія (°C)
    double pressure_pa{0.0};    // Атмосферний тиск у Паскалях (Па)
    double humidity_pct{0.0};   // Відносна вологість у відсотках (%)
};

/**
 * @brief Режими оверсемплінгу (усереднення вимірів) для BME280.
 */
enum class Oversampling : uint8_t {
    Skipped = 0x00,
    X1      = 0x01,
    X2      = 0x02,
    X4      = 0x03,
    X8      = 0x04,
    X16     = 0x05
};

/**
 * @brief C++ RAII-драйвер мікрокліматичного давача Bosch BME280.
 */
class BME280 {
public:
    static constexpr uint8_t I2C_ADDR_PRIMARY   = 0x76; // Стандартна адреса SDO -> GND
    static constexpr uint8_t I2C_ADDR_SECONDARY = 0x77; // Альтернативна адреса SDO -> VDDIO
    static constexpr uint8_t CHIP_ID_EXPECTED   = 0x60; // Chip ID для BME280

    // Картографія регістрів BME280
    static constexpr uint8_t REG_DIG_T1       = 0x88; // Початок 1-го блоку калібрування (26 байт)
    static constexpr uint8_t REG_DIG_H1       = 0xA1;
    static constexpr uint8_t REG_CHIP_ID      = 0xD0;
    static constexpr uint8_t REG_SOFT_RESET   = 0xE0;
    static constexpr uint8_t REG_DIG_H2       = 0xE1; // Початок 2-го блоку калібрування (7 байт)
    static constexpr uint8_t REG_CTRL_HUM     = 0xF2;
    static constexpr uint8_t REG_STATUS       = 0xF3;
    static constexpr uint8_t REG_CTRL_MEAS    = 0xF4;
    static constexpr uint8_t REG_CONFIG       = 0xF5;
    static constexpr uint8_t REG_DATA_START   = 0xF7; // Початок блоку сирих вимірів (8 байт)

    /**
     * @brief Конструктор драйвера.
     * @param bus Посилання на об'єкт шини I2CBus.
     * @param address I2C-адреса сенсора (за замовчуванням 0x76).
     */
    explicit BME280(I2CBus& bus, uint8_t address = I2C_ADDR_PRIMARY);

    /**
     * @brief Ініціалізація давача: перевірка Chip ID, м'яке скидання та зчитування NVRAM.
     * @return true у разі успішної ініціалізації.
     */
    bool init();

    /**
     * @brief Переведення давача у Forced Mode із заданням конфігурації oversampling.
     */
    bool trigger_forced_measurement(
        Oversampling os_temp = Oversampling::X1,
        Oversampling os_press = Oversampling::X1,
        Oversampling os_hum = Oversampling::X1
    );

    /**
     * @brief Перевірка стану прапорця measuring у регістрі status (0xF3).
     * @param measuring Повертає true, якщо вимірювання триває.
     */
    bool is_measuring(bool& measuring);

    /**
     * @brief Очікування завершення циклу вимірювання.
     * @param timeout_ms Максимальний час очікування в мілісекундах.
     */
    bool wait_until_ready(uint32_t timeout_ms = 100);

    /**
     * @brief Зчитування 8 байтів сирих вимірів та обчислення компенсованих величин.
     */
    bool read_sensor_data(Bme280Data& data);

    /**
     * @brief Виконання повного циклу вимірювання за запитом (Forced Mode).
     */
    bool perform_single_measurement(
        Bme280Data& data,
        Oversampling os_temp = Oversampling::X1,
        Oversampling os_press = Oversampling::X1,
        Oversampling os_hum = Oversampling::X1
    );

    /**
     * @brief Отримання зчитаних калібрувальних коефіцієнтів.
     */
    const Bme280CalibData& calibration_data() const noexcept { return calib_; }

private:
    bool read_calibration_data();
    double compensate_temperature(int32_t adc_T, int32_t& t_fine);
    double compensate_pressure(int32_t adc_P, int32_t t_fine);
    double compensate_humidity(int32_t adc_H, int32_t t_fine);

    I2CBus& bus_;
    uint8_t address_;
    Bme280CalibData calib_{};
};

#endif // BME280_HPP
