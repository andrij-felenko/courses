#include "vl53l0x_array.hpp"

namespace tof {

Vl53l0xArray::Vl53l0xArray(II2cBus& i2c_bus, IGpioController& gpio)
    : i2c_bus_(i2c_bus), gpio_(gpio) {}

void Vl53l0xArray::add_sensor_config(std::size_t id, int xshut_pin, int interrupt_pin, uint8_t target_address) {
    configs_.push_back(SensorConfig{id, xshut_pin, interrupt_pin, target_address});
}

bool Vl53l0xArray::initialize_all() {
    sensors_.clear();

    // КРОК 1: Вимикаємо всі давачі, притискаючи їхні лінії XSHUT до землі.
    // Це переводить усі VL53L0X у режим Shutdown, щоб запобігти конфліктам на дефолтній I2C-адресі (0x29).
    for (const auto& cfg : configs_) {
        gpio_.set_pin_mode_output(cfg.xshut_pin);
        gpio_.write_pin(cfg.xshut_pin, false);
    }

    // КРОК 2: Послідовно підключаємо кожен давач, міняємо його адресу та запускаємо
    for (const auto& cfg : configs_) {
        // Створюємо об'єкт давача для поточної конфігурації
        auto sensor = std::make_unique<Vl53l0xSensor>(
            cfg.id, cfg.xshut_pin, cfg.interrupt_pin, i2c_bus_, gpio_
        );

        // Подаємо високий рівень на XSHUT лише цього давача (активація)
        sensor->hardware_power_on();

        // Програмна зміна I2C-адреси з базової 0x29 на унікальну цільову адресу
        if (!sensor->set_i2c_address(cfg.target_i2c_address)) {
            return false;
        }

        // Ініціалізація внутрішніх регістрів давача за новою адресою
        if (!sensor->initialize()) {
            return false;
        }

        // Запуск неблокуючого безперервного вимірювання
        if (!sensor->start_continuous()) {
            return false;
        }

        sensors_.push_back(std::move(sensor));
    }

    return !sensors_.empty();
}

void Vl53l0xArray::set_distance_callback(DistanceCallback callback) {
    distance_callback_ = std::move(callback);
}

void Vl53l0xArray::update() {
    // Обхід усіх сенсорів у масиві та перевірка готовності даних без блокування
    for (auto& sensor : sensors_) {
        if (sensor->is_data_ready()) {
            process_sensor_readout(*sensor);
        }
    }
}

void Vl53l0xArray::handle_gpio_interrupt(int gpio_pin) {
    // Пошук давача, до якого прив'язано поточний пин переривання GPIO1
    for (auto& sensor : sensors_) {
        if (sensor->get_interrupt_pin() == gpio_pin) {
            process_sensor_readout(*sensor);
            break;
        }
    }
}

Vl53l0xSensor* Vl53l0xArray::get_sensor(std::size_t id) {
    for (auto& sensor : sensors_) {
        if (sensor->get_id() == id) {
            return sensor.get();
        }
    }
    return nullptr;
}

void Vl53l0xArray::process_sensor_readout(Vl53l0xSensor& sensor) {
    // Неблокуюче зчитування виміряної відстані
    auto result_opt = sensor.read_range_continuous();

    // Обов'язкове скидання прапорця апаратного переривання
    sensor.clear_interrupt();

    // Сповіщення прикладного застосунку через callback
    if (result_opt.has_value() && distance_callback_) {
        distance_callback_(sensor.get_id(), result_opt->distance_mm, result_opt->is_valid);
    }
}

} // namespace tof
