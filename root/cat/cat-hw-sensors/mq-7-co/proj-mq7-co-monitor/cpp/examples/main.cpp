#include <iostream>
#include <thread>
#include <chrono>
#include "../src/mq7.hpp"

// Симуляція апаратного таймера (повертає мілісекунди)
uint32_t mock_get_time_ms() {
    using namespace std::chrono;
    auto now = steady_clock::now().time_since_epoch();
    return static_cast<uint32_t>(duration_cast<milliseconds>(now).count());
}

// Симуляція читання АЦП
uint16_t mock_analog_read() {
    return 512; // Фіктивне значення (відповідає ~2.5В)
}

// Симуляція керування ШІМ нагрівача
void mock_set_heater(uint8_t pwm) {
    // В реальному середовищі тут виклик analogWrite(pin, pwm)
}

// Колбек для сповіщення про перевищення порогу
void alarm_handler(float ppm) {
    std::cerr << "[ТРИВОГА] Висока концентрація CO! Поточне значення: " 
              << ppm << " PPM" << std::endl;
}

int main() {
    // Налаштування: R0 = 10.0 (визначається при калібруванні), поріг тривоги = 50 PPM
    // Зменшимо тривалість циклів для прискореного тестування (60мс і 90мс замість секунд)
    mq7::Config config{10.0f, 50.0f, 60, 90};

    mq7::MQ7 sensor(config, mock_get_time_ms, mock_analog_read, mock_set_heater, alarm_handler);

    std::cout << "Запуск моніторингу MQ-7..." << std::endl;

    for (int i = 0; i < 20; ++i) {
        sensor.update();
        
        // Для демонстрації виводимо стан лише коли він змінюється
        static mq7::HeatingState last_state = mq7::HeatingState::Reading;
        if (sensor.get_state() != last_state) {
            last_state = sensor.get_state();
            if (last_state == mq7::HeatingState::HighVoltage) {
                std::cout << "Стан: Нагрів (High Voltage)" << std::endl;
            } else if (last_state == mq7::HeatingState::LowVoltage) {
                std::cout << "Стан: Охолодження (Low Voltage)" << std::endl;
            } else {
                std::cout << "Стан: Читання" << std::endl;
                std::cout << "Поточний рівень CO: " << sensor.get_ppm() << " PPM\n" << std::endl;
            }
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    return 0;
}
