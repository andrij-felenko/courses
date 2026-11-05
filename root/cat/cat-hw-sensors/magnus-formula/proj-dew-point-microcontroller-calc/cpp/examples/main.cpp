#include <iostream>
#include <vector>
#include <iomanip>
#include <random>
#include "../src/DewPointDetector.hpp"

struct RawSensorData {
    float temperature; // °C
    float humidity;    // %
};

int main() {
    std::cout << "=== Система запобігання конденсації на базі Формули Магнуса ===\n\n";

    // Ініціалізуємо детектор: нагрівач вмикатиметься, коли температура
    // середовища наблизиться до точки роси на 2.5°C.
    DewPointDetector detector(2.5f);

    // Імітація зміни умов середовища (швидке охолодження і зростання вологості)
    std::vector<RawSensorData> environment_changes = {
        {25.0f, 45.0f}, // Сухо та тепло
        {23.0f, 50.0f},
        {20.0f, 65.0f}, // Температура падає
        {18.0f, 75.0f},
        {16.0f, 85.0f}, // Високий ризик: холодно і волого
        {15.5f, 90.0f}, 
        {15.0f, 92.0f},
        {16.0f, 88.0f}, // Припустимо, нагрівач почав прогрівати зону навколо
        {18.0f, 80.0f},
        {22.0f, 60.0f}  // Повернення до норми
    };

    // Генератор шуму для симуляції похибок дешевих давачів
    std::mt19937 gen(42);
    std::normal_distribution<float> noise(-0.5f, 0.5f);

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "Т(сира)\tВол(сира)\tТ(фільтр)\tТочка роси\tНАГРІВАЧ\n";
    std::cout << "------------------------------------------------------------------\n";

    for (const auto& env : environment_changes) {
        // Додаємо випадковий шум до показників
        float noisy_temp = env.temperature + noise(gen);
        float noisy_hum = env.humidity + noise(gen) * 2.0f; // Вологість більш шумна

        // Обробляємо нові показники та отримуємо рішення системи
        bool heater_active = detector.processReading(noisy_temp, noisy_hum);

        std::cout << noisy_temp << "°C\t" 
                  << noisy_hum << "%\t\t"
                  << detector.getFilteredTemperature() << "°C\t\t"
                  << detector.getLastDewPoint() << "°C\t\t"
                  << (heater_active ? "[ УВІМКНЕНО ]" : "[ ВИМКНЕНО ]") << "\n";
    }

    return 0;
}
