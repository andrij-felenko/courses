#include "vl53l0x_array.hpp"
#include <iostream>
#include <map>
#include <vector>
#include <iomanip>
#include <string>

// Реалізація програмної симуляції апаратної шини I2C для демонстраційного прикладу
class SimulatedI2cBus : public tof::II2cBus {
public:
    struct DeviceState {
        uint8_t address{0x29};
        uint8_t interrupt_config{0};
        uint8_t sysrange_start{0};
        uint16_t simulated_range_mm{150};
    };

    bool write_register(uint8_t dev_addr, uint8_t reg_addr, uint8_t data) override {
        auto& dev = devices_[dev_addr];
        dev.address = dev_addr;

        if (reg_addr == tof::REG_I2C_SLAVE_DEVICE_ADDRESS) {
            // Зміна адреси веденого пристрою в симуляторі
            uint8_t new_addr = data & 0x7F;
            devices_[new_addr] = dev;
            devices_[new_addr].address = new_addr;
            devices_.erase(dev_addr);
            return true;
        }
        if (reg_addr == tof::REG_SYSTEM_INTERRUPT_CONFIG_GPIO) {
            dev.interrupt_config = data;
            return true;
        }
        if (reg_addr == tof::REG_SYSRANGE_START) {
            dev.sysrange_start = data;
            return true;
        }
        return true;
    }

    bool write_register16(uint8_t dev_addr, uint8_t reg_addr, uint16_t data) override {
        (void)dev_addr; (void)reg_addr; (void)data;
        return true;
    }

    bool read_register(uint8_t dev_addr, uint8_t reg_addr, uint8_t& data) override {
        if (reg_addr == tof::REG_IDENTIFICATION_MODEL_ID) {
            data = 0xEE; // VL53L0X Chip ID
            return true;
        }
        if (reg_addr == tof::REG_RESULT_INTERRUPT_STATUS) {
            data = 0x07; // Data ready status
            return true;
        }
        if (reg_addr == tof::REG_RESULT_RANGE_STATUS) {
            data = 0x00; // Status valid (0 = range valid)
            return true;
        }
        data = 0;
        return true;
    }

    bool read_register16(uint8_t dev_addr, uint8_t reg_addr, uint16_t& data) override {
        if (reg_addr == tof::REG_RESULT_RANGE_STATUS + 10) {
            data = devices_[dev_addr].simulated_range_mm;
            return true;
        }
        data = 0;
        return true;
    }

    void set_simulated_distance(uint8_t dev_addr, uint16_t distance_mm) {
        devices_[dev_addr].simulated_range_mm = distance_mm;
    }

private:
    std::map<uint8_t, DeviceState> devices_;
};

// Реалізація симуляції контролера GPIO для тестування сигналів переривання
class SimulatedGpioController : public tof::IGpioController {
public:
    void set_pin_mode_output(int pin) override {
        pin_modes_[pin] = "OUTPUT";
    }

    void set_pin_mode_input_pullup(int pin) override {
        pin_modes_[pin] = "INPUT_PULLUP";
        pin_levels_[pin] = true; // За замовчуванням підтяжка до VCC
    }

    void write_pin(int pin, bool level) override {
        pin_levels_[pin] = level;
    }

    bool read_pin(int pin) override {
        auto it = pin_levels_.find(pin);
        if (it != pin_levels_.end()) {
            return it->second;
        }
        return true;
    }

    void trigger_interrupt_pulse(int pin) {
        // Притискаємо GPIO1 до землі для імітації сигналу готовності даних
        pin_levels_[pin] = false;
    }

private:
    std::map<int, std::string> pin_modes_;
    std::map<int, bool> pin_levels_;
};

int main() {
    std::cout << "=== Ініціалізація масиву лазерних далекомірів VL53L0X ===" << std::endl;

    SimulatedI2cBus i2c_bus;
    SimulatedGpioController gpio;

    // Контролер масиву давачів
    tof::Vl53l0xArray sensor_array(i2c_bus, gpio);

    // Додаємо 3 давачі з різними XSHUT, GPIO1 перериваннями та унікальними I2C-адресами
    sensor_array.add_sensor_config(0, /*XSHUT*/ 4, /*INT*/ 16, /*Target I2C*/ 0x30);
    sensor_array.add_sensor_config(1, /*XSHUT*/ 5, /*INT*/ 17, /*Target I2C*/ 0x31);
    sensor_array.add_sensor_config(2, /*XSHUT*/ 6, /*INT*/ 18, /*Target I2C*/ 0x32);

    // Реєстрація асинхронного зворотного виклику для обробки вимірювань у застосунку
    sensor_array.set_distance_callback([](std::size_t sensor_id, uint16_t distance_mm, bool is_valid) {
        if (is_valid) {
            std::cout << "[CALLBACK] Сенсор #" << sensor_id 
                      << " | Дистанція: " << std::setw(4) << distance_mm << " мм | Стан: OK" << std::endl;
        } else {
            std::cout << "[CALLBACK] Сенсор #" << sensor_id 
                      << " | Помилка вимірювання!" << std::endl;
        }
    });

    // Виконання послідовної процедури ініціалізації та адресації
    if (!sensor_array.initialize_all()) {
        std::cerr << "Помилка ініціалізації масиву давачів VL53L0X!" << std::endl;
        return 1;
    }

    std::cout << "Усі давачі успішно переадресовані та запущені в безперервному режимі." << std::endl;
    std::cout << "\n=== Симуляція асинхронного неблокуючого циклу вимірювань ===" << std::endl;

    // Імітація кількох тактів роботи системи з надходженням нових вимірювань
    std::vector<uint16_t> sample_distances_s0 = {245, 248, 250, 242};
    std::vector<uint16_t> sample_distances_s1 = {512, 508, 515, 520};
    std::vector<uint16_t> sample_distances_s2 = {1120, 1115, 1100, 1090};

    for (size_t step = 0; step < 4; ++step) {
        std::cout << "\n--- Такт " << (step + 1) << " ---" << std::endl;

        // Задаємо симульовані дані вимірювання для сенсорів
        i2c_bus.set_simulated_distance(0x30, sample_distances_s0[step]);
        i2c_bus.set_simulated_distance(0x31, sample_distances_s1[step]);
        i2c_bus.set_simulated_distance(0x32, sample_distances_s2[step]);

        // Апаратні лінії GPIO1 надсилають переривання
        gpio.trigger_interrupt_pulse(16); // Сенсор 0
        gpio.trigger_interrupt_pulse(17); // Сенсор 1
        gpio.trigger_interrupt_pulse(18); // Сенсор 2

        // Основний неблокуючий диспетчер обробляє події готовності
        sensor_array.update();
    }

    std::cout << "\nРобота масиву VL53L0X завершена успішно." << std::endl;
    return 0;
}
