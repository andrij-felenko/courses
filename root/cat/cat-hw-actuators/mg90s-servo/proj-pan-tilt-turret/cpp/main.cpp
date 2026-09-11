#include "pan_tilt_driver.hpp"
#include <iostream>
#include <chrono>
#include <thread>
#include <iomanip>

// Імітація апаратного ШІМ-виводу таймера мікроконтролера
void hardwarePwmWrite(uint8_t pin, uint32_t pulse_us) {
    // В реальній системі на Arduino/ESP32: ledcWrite(), servo.writeMicroseconds() або регістр OCRnx
    // Тут зафіксовано звернення до апаратного драйвера
    (void)pin;
    (void)pulse_us;
}

// Отримання поточного часу в мікросекундах (кросплатформна емуляція micros())
uint64_t getSystemTimeUs() {
    using namespace std::chrono;
    static const auto start_time = steady_clock::now();
    const auto now = steady_clock::now();
    return duration_cast<microseconds>(now - start_time).count();
}

int main() {
    std::cout << "=== Демонстрація неблокуючого драйвера Pan-Tilt на MG90S ===\n\n";

    // Налаштування конфігурації сервоприводів MG90S V2
    actuators::ServoConfig pan_cfg;
    pan_cfg.pin = 9;                      // GPIO9
    pan_cfg.min_pulse_us = 500;           // Калібрований мінімум для 0°
    pan_cfg.max_pulse_us = 2400;          // Калібрований максимум для 180°
    pan_cfg.min_angle_deg = 15.0f;        // Soft-limit: заборона підходу до упору ближче 15°
    pan_cfg.max_angle_deg = 165.0f;       // Soft-limit: максимум 165°
    pan_cfg.backlash_deg = 1.8f;          // Вибірка технологічного люфту 1.8°
    pan_cfg.default_speed_deg_s = 90.0f;  // Плавна швидкість 90°/с (захист редуктора)

    actuators::ServoConfig tilt_cfg;
    tilt_cfg.pin = 10;                    // GPIO10
    tilt_cfg.min_pulse_us = 500;
    tilt_cfg.max_pulse_us = 2400;
    tilt_cfg.min_angle_deg = 30.0f;       // Soft-limit для нахилу: від 30°
    tilt_cfg.max_angle_deg = 150.0f;      // до 150° (захист камери від удару об основу)
    tilt_cfg.backlash_deg = 2.0f;         // Люфт по вертикалі 2.0°
    tilt_cfg.default_speed_deg_s = 60.0f; // 60°/с

    // Створення екземпляра драйвера
    actuators::PanTiltDriver turret(pan_cfg, tilt_cfg, hardwarePwmWrite);

    // Ініціалізація у нейтральну точку (90°, 90°)
    uint64_t now_us = getSystemTimeUs();
    turret.init(now_us);

    std::cout << "Ініціалізація виконана: Pan=90°, Tilt=90°\n";

    // Сценарій тестування: послідовність цільових координат (Pan, Tilt, Speed, опис)
    struct Waypoint {
        float pan;
        float tilt;
        float speed;
        const char* desc;
    };

    const Waypoint route[] = {
        {135.0f, 60.0f, 90.0f, "Поворот праворуч і нахил униз"},
        {45.0f, 120.0f, 60.0f, "Реверс: поворот ліворуч і підйом угору (активація вибірки люфту)"},
        {90.0f, 90.0f, 120.0f, "Повернення у нейтральне положення"}
    };

    size_t current_wp = 0;
    const size_t total_wps = sizeof(route) / sizeof(route[0]);

    // Встановлюємо першу ціль
    now_us = getSystemTimeUs();
    turret.setTargetPanTilt(route[0].pan, route[0].tilt, route[0].speed, now_us);
    std::cout << "Задано ціль 1: " << route[0].desc << " -> (" << route[0].pan << "°, " << route[0].tilt << "°)\n";

    // Імітація незалежної періодичної задачі (наприклад, опитування сенсора кожні 50 мс)
    uint64_t last_sensor_poll_us = 0;
    uint32_t sensor_readings_count = 0;

    // Неблокуючий диспетчер loop()
    while (current_wp < total_wps) {
        now_us = getSystemTimeUs();

        // 1. Оновлення кінематики драйвера (виконується миттєво, без блокування CPU)
        turret.update(now_us);

        // 2. Паралельна задача: зчитування сенсора кожні 50 000 мкс (50 мс)
        if (now_us - last_sensor_poll_us >= 50000) {
            last_sensor_poll_us = now_us;
            sensor_readings_count++;
            
            // Демонстраційний вивід стану системи
            std::cout << std::fixed << std::setprecision(1)
                      << "[Час " << (now_us / 1000) << " мс] "
                      << "Pan: " << turret.getCurrentAngle(actuators::AxisId::PAN) << "° ("
                      << turret.getCurrentPulseUs(actuators::AxisId::PAN) << " мкс) | "
                      << "Tilt: " << turret.getCurrentAngle(actuators::AxisId::TILT) << "° ("
                      << turret.getCurrentPulseUs(actuators::AxisId::TILT) << " мкс) | "
                      << "Рух: " << (turret.isMoving() ? "ТАК" : "НІ") << " | "
                      << "Сенсор опитано: " << sensor_readings_count << " разів\n";
        }

        // 3. Перехід до наступної контрольної точки після завершення попереднього руху
        if (!turret.isMoving()) {
            current_wp++;
            if (current_wp < total_wps) {
                std::this_thread::sleep_for(std::chrono::milliseconds(200)); // Пауза між точками
                now_us = getSystemTimeUs();
                turret.setTargetPanTilt(route[current_wp].pan, route[current_wp].tilt, route[current_wp].speed, now_us);
                std::cout << "\nЗадано ціль " << (current_wp + 1) << ": " << route[current_wp].desc 
                          << " -> (" << route[current_wp].pan << "°, " << route[current_wp].tilt << "°)\n";
            }
        }

        // Мікро-пауза для розвантаження процесора в емуляторі
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }

    std::cout << "\n=== Тест успішно завершено: усі точки пройдені без блокування циклу loop()! ===\n";
    return 0;
}
