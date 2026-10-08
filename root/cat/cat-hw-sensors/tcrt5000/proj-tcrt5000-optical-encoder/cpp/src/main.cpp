#include "adc_interface.hpp"
#include "tcrt5000_array.hpp"
#include <iostream>
#include <vector>
#include <iomanip>

/**
 * @brief Симуляційний клас для імітації роботи АЦП мікроконтролера.
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
     * @brief Встановлює імітовані показання АЦП.
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

    std::cout << "=== Симуляція масиву ІЧ-давачів TCRT5000 ===" << std::endl;
    sensor_array.reset_calibration();

    // 1. Процедура динамічного калібрування екстремумів
    std::cout << "\n[1] Проведення динамічного калібрування..." << std::endl;
    
    // Прохід по білій поверхні
    adc_hardware.set_simulated_values({320, 310, 305, 315, 325});
    sensor_array.calibrate_step();

    // Прохід над чорною лінією (ліві давачі)
    adc_hardware.set_simulated_values({3800, 2500, 310, 315, 320});
    sensor_array.calibrate_step();

    // Прохід над чорною лінією (праві давачі)
    adc_hardware.set_simulated_values({320, 310, 3900, 3850, 3750});
    sensor_array.calibrate_step();

    const auto& calib = sensor_array.get_calibration();
    for (std::size_t i = 0; i < SENSOR_COUNT; ++i) {
        std::cout << "  Давач " << i << ": Min = " << calib[i].min_value 
                  << ", Max = " << calib[i].max_value << std::endl;
    }

    // 2. Демонстрація робочого циклу та обчислення помилки
    std::cout << "\n[2] Запуск робочого циклу відстеження траєкторії..." << std::endl;

    // Сценарій A: Лінія по центру (Давач 2)
    adc_hardware.set_simulated_values({315, 310, 3880, 312, 320});
    sensor_array.update();
    
    std::cout << "\n--- Сценарій A: Лінія в центрі ---" << std::endl;
    std::cout << "  Позиція: " << sensor_array.get_line_position() << " / 4000" << std::endl;
    std::cout << "  Помилка відхилення (Error): " << sensor_array.get_line_error() << std::endl;

    // Сценарій B: Зсув лінії вліво
    adc_hardware.set_simulated_values({3700, 2200, 310, 305, 315});
    sensor_array.update();

    std::cout << "\n--- Сценарій B: Зсув вліво ---" << std::endl;
    std::cout << "  Позиція: " << sensor_array.get_line_position() << std::endl;
    std::cout << "  Помилка відхилення (Error): " << sensor_array.get_line_error() << std::endl;

    // Обчислення керуючого сигналу (P-регулятор)
    constexpr float KP = 0.05f;
    std::int32_t error = sensor_array.get_line_error();
    float steering = KP * static_cast<float>(error);
    std::cout << "  Сигнал P-регулятора на мотори: " << std::fixed << std::setprecision(2) << steering << std::endl;

    // Сценарій C: Повна втрата лінії
    adc_hardware.set_simulated_values({315, 310, 305, 312, 320});
    sensor_array.update();

    std::cout << "\n--- Сценарій C: Втрата лінії ---" << std::endl;
    std::cout << "  Статус лінії: " << (sensor_array.is_line_detected() ? "ЗНАЙДЕНО" : "ВТРАЧЕНО") << std::endl;
    std::cout << "  Збережена помилка для розвороту: " << sensor_array.get_line_error() << std::endl;

    return 0;
}
