#include "HallGimbal.hpp"
#include <iostream>
#include <vector>
#include <iomanip>

int main() {
    std::cout << "=== Об'єктно-орієнтований C++ драйвер джойстика Холла ===" << std::endl;

    GimbalConfig config;
    config.axis_x = { .min_raw = 200, .center_raw = 2048, .max_raw = 3900 };
    config.axis_y = { .min_raw = 200, .center_raw = 2048, .max_raw = 3900 };
    config.deadzone_radial = 0.06f; // 6% мертва зона
    config.alpha_ema = 0.3f;        // Коефіцієнт EMA

    HallGimbal gimbal(config);

    struct Sample {
        uint16_t raw_x;
        uint16_t raw_y;
        const char* note;
    };

    std::vector<Sample> test_data = {
        { 2048, 2048, "Нейтральний стан (центр)" },
        { 2070, 2030, "Мале відхилення в межах deadzone" },
        { 3900, 2048, "Максимальне відхилення осі X вправо" },
        { 2048, 200,  "Максимальне відхилення осі Y вниз" },
        { 3800, 3800, "Діагональний відхил (X+ / Y+)" },
        { 10,   2048, "Симуляція обриву лінії Холла (Raw X = 10)" }
    };

    std::cout << std::fixed << std::setprecision(3);

    for (size_t i = 0; i < test_data.size(); ++i) {
        const auto& sample = test_data[i];
        std::cout << "\n[Тест " << (i + 1) << "] " << sample.note << "\n";
        std::cout << "  Вхід АЦП: Raw X = " << sample.raw_x << ", Raw Y = " << sample.raw_y << "\n";

        // Кілька ітерацій оновлення для стабілізації EMA фільтра
        GimbalPosition pos;
        for (int step = 0; step < 5; ++step) {
            pos = gimbal.update(sample.raw_x, sample.raw_y);
        }

        if (pos.valid) {
            std::cout << "  Вихід: X = " << (pos.x >= 0 ? "+" : "") << pos.x 
                      << ", Y = " << (pos.y >= 0 ? "+" : "") << pos.y << " (OK)\n";
        } else {
            std::cout << "  Вихід: ПРИЗПИНЕНО (Апаратний вихід за межі АЦП!)\n";
        }
    }

    return 0;
}
