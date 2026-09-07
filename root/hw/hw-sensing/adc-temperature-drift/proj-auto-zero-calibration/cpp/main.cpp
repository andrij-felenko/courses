#include <iostream>
#include <iomanip>
#include <cmath>
#include "adc_calibrator.hpp"

int main() {
    std::cout << "=== Демонстрація термокомпенсації та автокалібрування АЦП ===\n\n";

    // Налаштування параметрів 12-розрядного перетворювача (0..4095)
    AdcCalibrator<12, float>::CalibrationParams params{
        .vref_nominal_v = 3.3f,
        .vref_temp_coeff_ppm = 25.0f,    // Дрейф ІОН 25 ppm/°C
        .t_cal_celsius = 25.0f,          // Заводське калібрування при 25°C
        .gain_temp_coeff_ppm = 12.0f,    // Температурний дрейф тракту АЦП
        .offset_drift_uv_per_c = 5.0f,   // Дрейф нуля 5 мкВ/°C
        .v_offset_base_mv = 2.4f         // Початковий зсув нуля при 25°C
    };

    AdcCalibrator<12, float> calibrator(params);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Номінальна розрядність: 12 біт (макс. код: " << calibrator.MaxAdcCode << ")\n";
    std::cout << "Початкова температура калібрування: " << calibrator.temperature() << " °C\n\n";

    // Симуляція надходження відліку при номінальній температурі (25°C)
    // Нехай подано тестову напругу 1650.0 мВ (половина шкали)
    uint32_t raw_code_nominal = 2051; // Дещо зміщений код через неідеальність
    float v_measured_25c = calibrator.convert_to_millivolts(raw_code_nominal);
    std::cout << "При T = 25.0°C:\n";
    std::cout << "  Сирий код: " << raw_code_nominal << " -> Напруга: " << v_measured_25c << " мВ\n\n";

    // Нагрівання плати до 65°C (промисловий діапазон)
    std::cout << "--> Підвищення температури до 65.0°C...\n";
    for (int i = 0; i < 10; ++i) {
        calibrator.update_temperature(65.0f, 0.3f);
    }
    std::cout << "  Встановлена відфільтрована температура: " << calibrator.temperature() << " °C\n";
    std::cout << "  Динамічно скоригований зсув нуля: " << calibrator.offset_drift_mv() << " мВ\n";
    std::cout << "  Коефіцієнт підсилення: " << calibrator.gain_factor() << "\n\n";

    // Той самий фізичний сигнал при 65°C призвів до зміщення коду через дрейф ІОН та ОП
    uint32_t raw_code_hot = 2043;
    float v_measured_hot = calibrator.convert_to_millivolts(raw_code_hot);
    uint32_t corrected_code = calibrator.correct_code(raw_code_hot);

    std::cout << "При T = 65.0°C:\n";
    std::cout << "  Сирий відлік (із дрейфом): " << raw_code_hot << "\n";
    std::cout << "  Відновлена напруга після термокомпенсації: " << v_measured_hot << " мВ\n";
    std::cout << "  Скоригований код відліку: " << corrected_code << "\n\n";

    // Демонстрація виконання операції Auto-Zero (автонуль)
    std::cout << "--> Виконання калібрування Auto-Zero (закорочення входу на землю)...\n";
    uint32_t ground_reading = 4; // Ненульовий код через дрейф
    calibrator.calibrate_zero_offset(ground_reading);
    std::cout << "  Нове зміщення нуля після Auto-Zero: " << calibrator.offset_drift_mv() << " мВ\n";
    std::cout << "  Вимір заземленого каналу тепер повертає: " 
              << calibrator.convert_to_millivolts(ground_reading) << " мВ\n";

    return 0;
}
