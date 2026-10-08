#pragma once

#include "i2c_bus.hpp"
#include <cstdint>
#include <cstddef>

namespace sensors {

/**
 * @brief Контейнер для збереження виміряних та верифікованих параметрів довкілля.
 */
struct Sht30Data {
    float temperature_c{0.0f};     ///< Температура повітря (°C)
    float humidity_percent{0.0f};  ///< Відносна вологість (%)
    bool is_valid{false};          ///< Прапорець цілісності даних (CRC-8 пройдено)
};

/**
 * @brief Драйвер цифрового давача температури й вологості Sensirion SHT30.
 */
class SHT30 {
public:
    /// Можливі 7-бітні I2C-адреси сенсора SHT30
    enum class Address : uint8_t {
        Default = 0x44,     ///< ADDR піно підключений до GND
        Alternative = 0x45  ///< ADDR піно підключений до VDD
    };

    /// Режими повторюваності (точності) вимірювання
    enum class Repeatability {
        High,   ///< Висока точність (триваліший вимір)
        Medium, ///< Середня точність
        Low     ///< Низька точність (мінімальне енергоспоживання)
    };

    // Команди протоколу I2C для SHT30
    static constexpr uint16_t CMD_MEASURE_HIGH_REP   = 0x2400;
    static constexpr uint16_t CMD_MEASURE_MED_REP    = 0x240B;
    static constexpr uint16_t CMD_MEASURE_LOW_REP    = 0x2416;
    static constexpr uint16_t CMD_HEATER_ENABLE      = 0x306D;
    static constexpr uint16_t CMD_HEATER_DISABLE     = 0x3066;
    static constexpr uint16_t CMD_SOFT_RESET         = 0x30A2;
    static constexpr uint16_t CMD_SLEEP              = 0xB098;

    explicit SHT30(I2CBus& bus, Address address = Address::Default);

    /**
     * @brief Запитує разове вимірювання (Single Shot) та зчитує 6-байтовий кадр з CRC-8.
     */
    Sht30Data read_measurement(Repeatability level = Repeatability::High);

    /**
     * @brief Керує внутрішнім апаратним нагрівачем (для видалення конденсату).
     */
    bool set_heater(bool enable);

    /**
     * @brief Виконує програмне скидання сенсора (Soft Reset).
     */
    bool soft_reset();

    /**
     * @brief Переводить сенсор у режим зниженого енергоспоживання (Sleep Mode).
     */
    bool sleep();

    /**
     * @brief Обчислює контрольну суму CRC-8 за алгоритмом Sensirion (поліном 0x31, init 0xFF).
     */
    static uint8_t calculate_crc8(const uint8_t* data, size_t length) noexcept;

private:
    I2CBus& bus_;
    Address address_;

    [[nodiscard]] uint16_t get_measure_command(Repeatability level) const noexcept;
    [[nodiscard]] static float raw_to_temperature(uint16_t raw_t) noexcept;
    [[nodiscard]] static float raw_to_humidity(uint16_t raw_rh) noexcept;
};

} // namespace sensors
