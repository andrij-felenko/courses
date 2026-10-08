#ifndef INA226_DRIVER_HPP
#define INA226_DRIVER_HPP

#include <cstdint>

namespace power_monitor {

/**
 * @brief Абстрактний інтерфейс для шини I2C.
 * Дозволяє інкапсулювати апаратну залежність (Arduino Wire, ESP32 I2C, Linux /dev/i2c-X або симуляція).
 */
class I2CBus {
public:
    virtual ~I2CBus() = default;

    /**
     * @brief Запис 16-бітного значення у регістр INA226 (Big-Endian конвертація).
     * @param dev_addr 7-бітна I2C адреса пристрою.
     * @param reg_addr Адреса регістру INA226.
     * @param value 16-бітне значення для запису.
     * @return true при успішному записі, false — при помилці на шині.
     */
    virtual bool write_register(uint8_t dev_addr, uint8_t reg_addr, uint16_t value) = 0;

    /**
     * @brief Зчитування 16-бітного значення з регістру INA226 (Big-Endian конвертація).
     * @param dev_addr 7-бітна I2C адреса пристрою.
     * @param reg_addr Адреса регістру INA226.
     * @param value Посилання для збереження прочитаного 16-бітного значення.
     * @return true при успішному зчитанні, false — при помилці на шині.
     */
    virtual bool read_register(uint8_t dev_addr, uint8_t reg_addr, uint16_t& value) = 0;
};

/**
 * @brief Перерахування для налаштування кількості усереднень вимірів (AVG, біти 11-9 Config).
 */
enum class Averaging : uint16_t {
    AVG_1    = 0b000 << 9,
    AVG_4    = 0b001 << 9,
    AVG_16   = 0b010 << 9,
    AVG_64   = 0b011 << 9,
    AVG_128  = 0b100 << 9,
    AVG_256  = 0b101 << 9,
    AVG_512  = 0b110 << 9,
    AVG_1024 = 0b111 << 9
};

/**
 * @brief Перерахування для налаштування часу перетворення (Conversion Time, біти 8-6 VBUS CT, 5-3 VSH CT).
 */
enum class ConversionTime : uint16_t {
    TIME_140US  = 0b000,
    TIME_204US  = 0b001,
    TIME_332US  = 0b010,
    TIME_588US  = 0b011,
    TIME_1100US = 0b100,
    TIME_2116US = 0b101,
    TIME_4156US = 0b110,
    TIME_8244US = 0b111
};

/**
 * @brief Перерахування режимів роботи (Operating Mode, біти 2-0 Config).
 */
enum class OperatingMode : uint16_t {
    POWER_DOWN           = 0b000,
    SHUNT_TRIGGERED      = 0b001,
    BUS_TRIGGERED        = 0b010,
    SHUNT_BUS_TRIGGERED  = 0b011,
    POWER_DOWN_ALT       = 0b100,
    SHUNT_CONTINUOUS     = 0b101,
    BUS_CONTINUOUS       = 0b110,
    SHUNT_BUS_CONTINUOUS = 0b111
};

/**
 * @brief Низькорівневий C++ драйвер для цифрового монітора живлення INA226.
 */
class Ina226Driver {
public:
    static constexpr uint8_t DEFAULT_I2C_ADDR = 0x40;

    // Адреси регістрів INA226
    static constexpr uint8_t REG_CONFIG          = 0x00;
    static constexpr uint8_t REG_SHUNT_VOLTAGE   = 0x01;
    static constexpr uint8_t REG_BUS_VOLTAGE     = 0x02;
    static constexpr uint8_t REG_POWER           = 0x03;
    static constexpr uint8_t REG_CURRENT         = 0x04;
    static constexpr uint8_t REG_CALIBRATION     = 0x05;
    static constexpr uint8_t REG_MASK_ENABLE     = 0x06;
    static constexpr uint8_t REG_ALERT_LIMIT     = 0x07;
    static constexpr uint8_t REG_MANUFACTURER_ID = 0xFE;
    static constexpr uint8_t REG_DIE_ID          = 0xFF;

    // Очікувані значення ID пристрою
    static constexpr uint16_t EXPECTED_MANUFACTURER_ID = 0x5449; // "TI"
    static constexpr uint16_t EXPECTED_DIE_ID          = 0x2260; // INA226

    explicit Ina226Driver(I2CBus& bus, uint8_t dev_addr = DEFAULT_I2C_ADDR);

    /**
     * @brief Первинний запуск драйвера: перевірка чипа, скидання, калібрування та конфігурація.
     * @param r_shunt_ohms Опір вимірювального шунта в Омах (наприклад, 0.002 для 2 мОм).
     * @param max_expected_current_a Максимальний очікуваний струм в Амперах (наприклад, 10.0 A).
     * @return true якщо ініціалізація успішна.
     */
    bool begin(double r_shunt_ohms, double max_expected_current_a);

    /**
     * @brief Програмне скидання регістрів пристрою (Soft Reset).
     */
    bool soft_reset();

    /**
     * @brief Перевірка ідентифікаторів виробника та ревізії кристала INA226.
     */
    bool verify_device_id();

    /**
     * @brief Запис конфігурації у регістр Configuration (0x00).
     */
    bool configure(Averaging avg = Averaging::AVG_16,
                   ConversionTime vbus_ct = ConversionTime::TIME_1100US,
                   ConversionTime vsh_ct = ConversionTime::TIME_1100US,
                   OperatingMode mode = OperatingMode::SHUNT_BUS_CONTINUOUS);

    /**
     * @brief Обчислення та запис значення калібрувального регістра Calibration (0x05)
     *        за формулою CAL = floor(0.00512 / (Current_LSB * R_shunt)).
     */
    bool calibrate(double r_shunt_ohms, double max_expected_current_a);

    /**
     * @brief Пряме встановлення значення регістра калібрування та Current_LSB.
     */
    bool set_calibration_raw(uint16_t cal_val, double current_lsb);

    /**
     * @brief Зчитування напруги шини у Вольтах (В). LSB = 1.25 мВ.
     */
    bool read_bus_voltage(double& bus_voltage_v);

    /**
     * @brief Зчитування падіння напруги на шунті у Мілівольтах (мВ). LSB = 2.5 мкВ.
     */
    bool read_shunt_voltage(double& shunt_voltage_mv);

    /**
     * @brief Зчитування знакового струму в Амперах (А). 16-бітний доповняльний код.
     */
    bool read_current(double& current_a);

    /**
     * @brief Зчитування миттєвої потужності у Ватах (Вт). LSB = 25 * Current_LSB.
     */
    bool read_power(double& power_w);

    /**
     * @brief Одночасне зчитування напруги шини, струму та потужності.
     */
    bool read_all(double& bus_voltage_v, double& current_a, double& power_w);

    /**
     * @brief Керування сплячим режимом (Power-Down mode).
     * @param sleep true — перевести у Power-Down, false — відновити активний режим.
     */
    bool set_sleep_mode(bool sleep);

    /**
     * @brief Перевірка чи знаходиться сенсор у сплячому режимі.
     */
    bool is_sleeping() const { return is_sleeping_; }

    /**
     * @brief Отримати розраховане значення LSB струму (А/LSB).
     */
    double get_current_lsb() const { return current_lsb_; }

    /**
     * @brief Отримати розраховане значення LSB потужності (Вт/LSB).
     */
    double get_power_lsb() const { return power_lsb_; }

    /**
     * @brief Отримати значення регістра Calibration.
     */
    uint16_t get_calibration_raw() const { return calibration_val_; }

private:
    I2CBus& bus_;
    uint8_t dev_addr_;
    double current_lsb_{0.0};
    double power_lsb_{0.0};
    uint16_t calibration_val_{0};
    uint16_t config_cache_{0x4127};
    bool is_sleeping_{false};

    bool write_reg(uint8_t reg, uint16_t val);
    bool read_reg(uint8_t reg, uint16_t& val);
};

} // namespace power_monitor

#endif // INA226_DRIVER_HPP
