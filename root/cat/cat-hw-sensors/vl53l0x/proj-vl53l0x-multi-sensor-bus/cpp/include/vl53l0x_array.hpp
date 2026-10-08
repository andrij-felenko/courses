#ifndef VL53L0X_ARRAY_HPP
#define VL53L0X_ARRAY_HPP

#include "vl53l0x_sensor.hpp"
#include <vector>
#include <functional>
#include <memory>

namespace tof {

// Опис конфігурації окремого давача для ініціалізації масиву
struct SensorConfig {
    std::size_t id;
    int xshut_pin;
    int interrupt_pin;
    uint8_t target_i2c_address;
};

// Тип функції зворотного виклику для сповіщення про нові виміряні дані
using DistanceCallback = std::function<void(std::size_t sensor_id, uint16_t distance_mm, bool is_valid)>;

// Клас-контролер масиву давачів VL53L0X
class Vl53l0xArray {
public:
    Vl53l0xArray(II2cBus& i2c_bus, IGpioController& gpio);

    // Додавання опису давача до переліку конфігурацій
    void add_sensor_config(std::size_t id, int xshut_pin, int interrupt_pin, uint8_t target_address);

    // Послідовна процедура адресації та налаштування всіх сенсорів у масиві
    bool initialize_all();

    // Реєстрація прикладного callback для отримання даних
    void set_distance_callback(DistanceCallback callback);

    // Неблокуюча перевірка апаратних переривань та оновлення стану масиву
    void update();

    // Прямий обробник переривання GPIO1 для конкретного пина
    void handle_gpio_interrupt(int gpio_pin);

    // Доступ до окремих об'єктів давачів
    Vl53l0xSensor* get_sensor(std::size_t id);
    const std::vector<std::unique_ptr<Vl53l0xSensor>>& get_sensors() const { return sensors_; }

private:
    II2cBus& i2c_bus_;
    IGpioController& gpio_;
    std::vector<SensorConfig> configs_;
    std::vector<std::unique_ptr<Vl53l0xSensor>> sensors_;
    DistanceCallback distance_callback_{nullptr};

    void process_sensor_readout(Vl53l0xSensor& sensor);
};

} // namespace tof

#endif // VL53L0X_ARRAY_HPP
