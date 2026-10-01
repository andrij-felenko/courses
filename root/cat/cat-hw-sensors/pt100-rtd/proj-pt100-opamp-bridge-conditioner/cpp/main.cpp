#include "Pt100Normalizer.hpp"
#include <iostream>
#include <iomanip>
#include <vector>
#include <string>

/**
 * @brief Допоміжна функція для друку текстового опису статусу давача
 */
const char* statusToString(SensorStatus status) {
    switch (status) {
        case SensorStatus::Ok:                   return "Норма (Відкалібровано)";
        case SensorStatus::Uncalibrated:         return "Норма (Номінальний режим)";
        case SensorStatus::AdcOutOfRange:        return "Помилка: Переповнення АЦП";
        case SensorStatus::ShortCircuit:         return "Аварія: Коротке замикання давача";
        case SensorStatus::OpenCircuit:          return "Аварія: Обрив лінії давача";
        case SensorStatus::TemperatureOutOfRange: return "Помилка: Температура поза межами PT100";
        default:                                 return "Невідомий статус";
    }
}

int main() {
    std::cout << "=== Система обробки аналогового сигналу PT100 ===" << std::endl;

    // Ініціалізація нормалізатора PT100 для 12-бітного АЦП (0...4095) з опорною напругою 3.3 В
    // Робочий діапазон напруги нормалізатора: 0.1 В ... 3.2 В
    constexpr uint32_t kAdcResolution = 4095;
    constexpr float kVref = 3.3f;
    Pt100Normalizer normalizer(kAdcResolution, kVref, 0.1f, 3.2f);

    // Налаштування номінального діапазону перетворення (наприклад, 0...200 °C відповідає 0...3.3 В)
    normalizer.setNominalRange(0.0f, 200.0f);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "\n--- 1. Перевірка роботи до двохточкового калібрування ---" << std::endl;
    std::cout << "Стан калібрування: " << (normalizer.isCalibrated() ? "Так" : "Ні") << std::endl;

    CalibCoeffs initial_coeffs = normalizer.getCoefficients();
    std::cout << "Номінальний gain  : " << initial_coeffs.gain << " °C/відлік" << std::endl;
    std::cout << "Номінальний offset: " << initial_coeffs.offset << " °C" << std::endl;

    uint32_t test_raw_adc = 1024; // Сирий відлік АЦП (приблизно 0.825 В)
    SensorStatus current_status{};
    auto uncalib_temp = normalizer.readTemperature(test_raw_adc, current_status);

    std::cout << "Відлік АЦП: " << test_raw_adc
              << " | Напруга: " << normalizer.rawToVoltage(test_raw_adc) << " В"
              << " | Температура: " << (uncalib_temp ? std::to_string(*uncalib_temp) : "N/A") << " °C"
              << " | Статус: " << statusToString(current_status) << std::endl;

    // --- 2. Процедура двохточкового калібрування ---
    std::cout << "\n--- 2. Виконання двохточкового калібрування ---" << std::endl;
    // Опорна точка 1: Суміш води та льоду при 0.0 °C (фактично виміряний АЦП = 210 відліків)
    // Опорна точка 2: Кипляча вода при 100.0 °C (фактично виміряний АЦП = 2250 відліків)
    CalibPoint ice_point{210, 0.0f};
    CalibPoint boiling_point{2250, 100.0f};

    std::cout << "Опорна точка 1: ADC = " << ice_point.raw_adc << " -> Temp = " << ice_point.reference_temp << " °C" << std::endl;
    std::cout << "Опорна точка 2: ADC = " << boiling_point.raw_adc << " -> Temp = " << boiling_point.reference_temp << " °C" << std::endl;

    if (normalizer.calibrate(ice_point, boiling_point)) {
        std::cout << "Калібрування успішно виконано!" << std::endl;
    } else {
        std::cerr << "Помилка калібрування: некоректні опорні дані!" << std::endl;
        return 1;
    }

    CalibCoeffs calib_coeffs = normalizer.getCoefficients();
    std::cout << "Обчислений gain  : " << calib_coeffs.gain << " °C/відлік" << std::endl;
    std::cout << "Обчислений offset: " << calib_coeffs.offset << " °C" << std::endl;
    std::cout << "Стан калібрування: " << (normalizer.isCalibrated() ? "Так" : "Ні") << std::endl;

    // --- 3. Симуляція періодичного вимірювального циклу мікроконтролера ---
    std::cout << "\n--- 3. Симуляція циклу вимірювання та діагностики ---" << std::endl;

    // Набір тестових відліків АЦП: нормальні значення та аварійні режими
    const std::vector<uint32_t> simulated_adc_readings = {
        50,    // Коротке замикання (напруга ~0.04 В < 0.1 В)
        210,   // Калібрувальна точка 0 °C
        1230,  // Нормальне вимірювання (~50 °C)
        2250,  // Калібрувальна точка 100 °C
        3100,  // Нормальне вимірювання високої температури (~141.6 °C)
        4000,  // Обрив лінії давача (напруга ~3.22 В > 3.2 В)
        4500   // Переповнення АЦП (> 4095)
    };

    for (size_t i = 0; i < simulated_adc_readings.size(); ++i) {
        uint32_t raw = simulated_adc_readings[i];
        float voltage = normalizer.rawToVoltage(raw);
        SensorStatus status{};
        std::optional<float> temp = normalizer.readTemperature(raw, status);

        std::cout << "Ітерація " << i + 1 << " | АЦП: " << std::setw(4) << raw
                  << " | Напруга: " << std::setw(5) << voltage << " В | ";

        if (temp.has_value()) {
            std::cout << "Температура: " << std::setw(7) << *temp << " °C | ";
        } else {
            std::cout << "Температура:   Н/Д    | ";
        }

        std::cout << "Статус: " << statusToString(status) << std::endl;
    }

    return 0;
}
