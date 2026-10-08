#ifndef VL53L0X_SENSOR_HPP
#define VL53L0X_SENSOR_HPP

#include <cstdint>
#include <cstddef>
#include <optional>

namespace tof {

// Замовчувана початкова I2C-адреса VL53L0X після скидання
constexpr uint8_t DEFAULT_I2C_ADDRESS = 0x29;

// Адреси ключових регістрів VL53L0X
constexpr uint8_t REG_SYSRANGE_START                = 0x00;
constexpr uint8_t REG_SYSTEM_INTERRUPT_CONFIG_GPIO = 0x0A;
constexpr uint8_t REG_SYSTEM_INTERRUPT_CLEAR       = 0x0B;
constexpr uint8_t REG_RESULT_INTERRUPT_STATUS      = 0x13;
constexpr uint8_t REG_RESULT_RANGE_STATUS          = 0x14;
constexpr uint8_t REG_I2C_SLAVE_DEVICE_ADDRESS     = 0x8A;
constexpr uint8_t REG_IDENTIFICATION_MODEL_ID      = 0xC0;

// Структура з результатом вимірювання відстані
struct MeasurementResult {
    uint16_t distance_mm{0};    // Дистанція в міліметрах
    uint8_t range_status{0};    // Статус апаратного вимірювача (0 = успіх)
    bool is_valid{false};        // Прапор коректності даних
};

// Абстрактний інтерфейс для шини I2C
class II2cBus {
public:
    virtual ~II2cBus() = default;
    virtual bool write_register(uint8_t dev_addr, uint8_t reg_addr, uint8_t data) = 0;
    virtual bool write_register16(uint8_t dev_addr, uint8_t reg_addr, uint16_t data) = 0;
    virtual bool read_register(uint8_t dev_addr, uint8_t reg_addr, uint8_t& data) = 0;
    virtual bool read_register16(uint8_t dev_addr, uint8_t reg_addr, uint16_t& data) = 0;
};

// Абстрактний інтерфейс для керування лініями GPIO
class IGpioController {
public:
    virtual ~IGpioController() = default;
    virtual void set_pin_mode_output(int pin) = 0;
    virtual void set_pin_mode_input_pullup(int pin) = 0;
    virtual void write_pin(int pin, bool level) = 0;
    virtual bool read_pin(int pin) = 0;
};

// Клас керування одним лазерним давачем VL53L0X
class Vl53l0xSensor {
public:
    Vl53l0xSensor(std::size_t id, int xshut_pin, int interrupt_pin, II2cBus& i2c_bus, IGpioController& gpio);

    // Апаратне керування живленням/скиданням через лінію XSHUT
    void hardware_power_off();
    void hardware_power_on();

    // Програмна зміна I2C-адреси пристрою
    bool set_i2c_address(uint8_t new_address);
    uint8_t get_i2c_address() const { return current_address_; }

    // Конфігурація регістрів та перевірка зв'язку
    bool initialize();

    // Запуск та зупинка режиму безперервних вимірювань
    bool start_continuous();
    bool stop_continuous();

    // Перевірка готовності даних та неблокуюче зчитування
    bool is_data_ready();
    std::optional<MeasurementResult> read_range_continuous();

    // Скидання прапорця апаратного переривання на давачі
    bool clear_interrupt();

    std::size_t get_id() const { return sensor_id_; }
    int get_xshut_pin() const { return xshut_pin_; }
    int get_interrupt_pin() const { return interrupt_pin_; }

private:
    std::size_t sensor_id_;
    int xshut_pin_;
    int interrupt_pin_;
    uint8_t current_address_{DEFAULT_I2C_ADDRESS};
    bool is_continuous_{false};

    II2cBus& i2c_bus_;
    IGpioController& gpio_;

    // Приватні допоміжні методи для зручної роботи з I2C
    bool write_reg(uint8_t reg, uint8_t val);
    bool write_reg16(uint8_t reg, uint16_t val);
    bool read_reg(uint8_t reg, uint8_t& val);
    bool read_reg16(uint8_t reg, uint16_t& val);
};

} // namespace tof

#endif // VL53L0X_SENSOR_HPP
