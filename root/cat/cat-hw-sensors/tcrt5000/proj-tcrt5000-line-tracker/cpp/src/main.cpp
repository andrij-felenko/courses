#include "adc_interface.hpp"
#include "tcrt5000_array.hpp"
#include <iostream>
#include <vector>
#include <cmath>

/**
 * @brief Симуляція апаратного АЦП мікроконтролера з масивом з 5 сенсорів TCRT5000.
 */
class SimulatedAdcReader : public IAdcArrayReader {
public:
    explicit SimulatedAdcReader(std::size_t sensor_count) 
        : sensor_count_(sensor_count), simulated_raw_(sensor_count, 300) {}

    bool read_channels(std::span<std::uint16_t> buffer) override {
        if (buffer.size() < sensor_count_) {
            return false;
        }
        for (std::size_t i = 0; i < sensor_count_; ++i) {
            buffer[i] = simulated_raw_[i];
        }
        return true;
    }

    std::size_t get_channel_count() const override {
        return sensor_count_;
    }

    /**
     * @brief Задає іммітовані сирі значення АЦП від давачів.
     */
    void set_simulated_values(const std::vector<std::uint16_t>& values) {
        if (values.size() == sensor_count_) {
            simulated_raw_ = values;
        }
    }

private:
    std::size_t sensor_count_;
    std::vector<std::uint16_t> simulated_raw_;
};

int main() {
    constexpr std::size_t SENSOR_COUNT = 5;
    SimulatedAdcReader adc_hardware(SENSOR_COUNT);
    TCRT5000Array sensor_array(adc_hardware, SENSOR_COUNT, 0.4f);

    std::cout << "=== Ініціалізація масиву ІЧ-давачів TCRT5000 ===" << std::endl;
    sensor_array.reset_calibration();

    // 1. Симуляція процедури динамічного калібрування (рух над білою та чорною поверхнею)
    std::cout << "\n--- Запуск процедури калібрування ---" << std::endl;
    
    // Прохід 1: Біла поверхня
    adc_hardware.set_simulated_values({320, 310, 305, 315, 325});
    sensor_array.calibrate_step();

    // Прохід 2: Чорна лінія під сенсором 0 та 1
    adc_hardware.set_simulated_values({3800, 2500, 310, 315, 320});
    sensor_array.calibrate_step();

    // Прохід 3: Чорна лінія під сенсорами 2, 3, 4
    adc_hardware.set_simulated_values({320, 310, 3900, 3850, 3750});
    sensor_array.calibrate_step();

    // Друк результатів калібрування
    const auto& calib = sensor_array.get_calibration();
    for (std::size_t i = 0; i < SENSOR_COUNT; ++i) {
        std::cout << "Давач " << i << ": Min ADC = " << calib[i].min_value 
                  << ", Max ADC = " << calib[i].max_value << std::endl;
    }

    // 2. Симуляція робочого циклу відстеження лінії
    std::cout << "\n--- Робочий цикл відстеження лінії ---" << std::endl;

    // Сценарій 1: Лінія чітко по центру (Давач 2)
    adc_hardware.set_simulated_values({315, 310, 3880, 312, 320});
    sensor_array.update();
    
    std::cout << "Сценарій 1 (Центр):" << std::endl;
    std::cout << "  Позиція: " << sensor_array.get_line_position() 
              << " / 4000 (Центр = 2000)" << std::endl;
    std::cout << "  Помилка відхилення (Error): " << sensor_array.get_line_error() << std::endl;

    // Сценарій 2: Лінія зсунута вліво (між давачами 0 і 1)
    adc_hardware.set_simulated_values({3700, 2200, 310, 305, 315});
    sensor_array.update();

    std::cout << "\nСценарій 2 (Зсув вліво):" << std::endl;
    std::cout << "  Позиція: " << sensor_array.get_line_position() << std::endl;
    std::cout << "  Помилка відхилення (Error): " << sensor_array.get_line_error() << std::endl;

    // Обчислення керуючого сигналу (пропорційний регулятор)
    float kp = 0.05f;
    int32_t error = sensor_array.get_line_error();
    float steering_correction = kp * error;
    std::cout << "  Корригуючий сигнал мотора: " << steering_correction << std::endl;

    // Сценарій 3: Втрата лінії (усі давачі на білому)
    adc_hardware.set_simulated_values({315, 310, 305, 312, 320});
    sensor_array.update();

    std::cout << "\nСценарій 3 (Втрата лінії):" << std::endl;
    std::cout << "  Статус виявлення: " << (sensor_array.is_line_detected() ? "Знайдено" : "ВТРАЧЕНО") << std::endl;
    std::cout << "  Останній відомий зсув: " << sensor_array.get_line_error() << std::endl;

    return 0;
}
