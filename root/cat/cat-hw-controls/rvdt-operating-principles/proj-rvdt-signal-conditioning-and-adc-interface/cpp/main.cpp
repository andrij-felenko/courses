#include <iostream>
#include <vector>
#include <iomanip>
#include <cmath>
#include "RvdtSensor.hpp"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Допоміжна функція форматованого виводу стану вимірювання
void printReading(std::string_view label, const RvdtSensor& sensor) {
    const auto& r = sensor.getReading();
    std::cout << std::left << std::setw(38) << label << " | "
              << "V1: " << std::fixed << std::setprecision(3) << r.v1Volts << " B | "
              << "V2: " << r.v2Volts << " B | "
              << "R: " << std::setw(6) << r.ratiometricRatio << " | "
              << "Кут: " << std::setw(6) << std::setprecision(2) << r.angleDegrees << "° | "
              << "Стан: " << RvdtSensor::statusToString(r.status) << "\n";
}

int main() {
    std::cout << "=== Бортовий драйвер опрацювання сигналів RVDT давача (C++17/20) ===\n\n";

    // 1. Конфігурація RVDT давача
    RvdtConfig config{
        .sensitivity = 50.0f,     // R = 0.8 відповідає куту +40.0°
        .zeroOffsetDeg = 0.0f,
        .minAngleDeg = -50.0f,
        .maxAngleDeg = +50.0f,
        .vSumMinVolts = 0.5f,
        .vSumMaxVolts = 7.0f,
        .filterAlpha = 0.4f
    };

    RvdtSensor sensor(config);

    std::cout << "--- Тест 1: Сканування кута повороту вала ---\n";
    sensor.processAmplitudes(2.50f, 2.50f);
    printReading("1. Нейтральне положення (0°)", sensor);

    sensor.processAmplitudes(4.00f, 1.00f);
    printReading("2. Поворот на +30°", sensor);

    sensor.processAmplitudes(0.75f, 4.25f);
    printReading("3. Поворот на -35°", sensor);

    std::cout << "\n--- Тест 2: Інваріантність ратіометричного розрахунку до дрейфу живлення/температури ---\n";
    std::cout << "Початковий стан: V1=4.0В, V2=1.0В (R=0.6, Кут=30.0°)\n";

    // Симуляція температурного зростання амплітуди джерела збудження на +30%
    sensor.processAmplitudes(5.20f, 1.30f);
    printReading("При +30% дрейфі живлення (V1=5.2, V2=1.3)", sensor);
    std::cout << "-> Результат: R = (5.2 - 1.3) / (5.2 + 1.3) = 3.9 / 6.5 = 0.6 -> Кут залишається точно 30.0°!\n";

    std::cout << "\n--- Тест 3: Фазочутлива демодуляція (PSD) відліків АЦП через std::span ---\n";
    constexpr size_t samplesCount = 32;
    std::vector<int16_t> s1(samplesCount);
    std::vector<int16_t> s2(samplesCount);
    std::vector<int16_t> ref(samplesCount);

    for (size_t i = 0; i < samplesCount; ++i) {
        float phase = 2.0f * static_cast<float>(M_PI) * static_cast<float>(i) / static_cast<float>(samplesCount);
        ref[i] = static_cast<int16_t>(2047.0f * std::sin(phase));
        s1[i]  = static_cast<int16_t>(2800.0f * std::sin(phase));
        s2[i]  = static_cast<int16_t>(1200.0f * std::sin(phase));
    }

    sensor.processAdcSamples(s1, s2, ref, 3.3f, 12);
    printReading("Декодування сирого кадру АЦП", sensor);

    std::cout << "\n--- Тест 4: Апаратна діагностика несправностей обмоток ---\n";

    // Обрив обмотки: V1 + V2 = 0.1В < 0.5В
    sensor.processAmplitudes(0.05f, 0.05f);
    printReading("Аварія: Обрив обмотки", sensor);

    // Коротке замикання: V1 + V2 = 8.0В > 7.0В
    sensor.processAmplitudes(4.00f, 4.00f);
    printReading("Аварія: Коротке замикання", sensor);

    // Перевищення робочого кута (> +50°)
    sensor.processAmplitudes(4.80f, 0.20f);
    printReading("Перевищення механічного кута", sensor);

    std::cout << "\n=== Обробку RVDT сигналів завершено успішно ===\n";
    return 0;
}
