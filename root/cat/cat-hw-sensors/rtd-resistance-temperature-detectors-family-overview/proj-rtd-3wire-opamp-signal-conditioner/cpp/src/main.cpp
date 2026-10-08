#include <iostream>
#include <iomanip>
#include <vector>
#include "rtd_sensor.hpp"

using namespace sensors::rtd;

int main() {
    std::cout << "=========================================================\n";
    std::cout << "   Драйвер платинового терморезистора RTD (Pt100/Pt1000)  \n";
    std::cout << "=========================================================\n\n";

    // 1. Конфігурація АЦП у співвідносному (ratiometric) режимі
    AdcConfig adc_cfg;
    adc_cfg.vref_volts = 3.3;          // Опорна напруга 3.3 В
    adc_cfg.gain = 1.0;                // Коефіцієнт підсилення PGA = 1x
    adc_cfg.resolution_bits = 16;      // 16-бітний АЦП (0..65535)
    adc_cfg.is_ratiometric = true;     // Співвідносне вимірювання
    adc_cfg.r_ref_ohms = 400.0;        // Еталонний резистор вимірювального мосту R_ref = 400 Ом

    std::cout << "[1] Параметри вимірювального тракту АЦП:\n";
    std::cout << "  - Розрядність АЦП: " << static_cast<int>(adc_cfg.resolution_bits) << " біт (Max code: " << adc_cfg.getMaxCode() << ")\n";
    std::cout << "  - Коефіцієнт підсилення (PGA): " << adc_cfg.gain << "x\n";
    std::cout << "  - Режим вимірювання: Співвідносний (Ratiometric)\n";
    std::cout << "  - Еталонний опір R_ref: " << adc_cfg.r_ref_ohms << " Ом\n\n";

    // 2. Ініціалізація об'єкта драйвера для платинового датчика Pt100
    RtdSensor sensor(adc_cfg, RtdType::Pt100);

    // 3. Симуляція процедури двоточкового калібрування за еталонними опорами
    std::cout << "[2] Виконання процедури двоточкового калібрування:\n";
    const double r_std1 = 100.0;  // Точка 1: Еталонний опір 100.00 Ом (0 °C)
    const double r_std2 = 138.51; // Точка 2: Еталонний опір 138.51 Ом (100 °C)

    // Внаслідок системного зсуву нуля та масштабного зсуву, виміряні коди відображають 100.8 Ом та 139.6 Ом відповідно
    const int32_t raw_code1 = static_cast<int32_t>((100.8 / adc_cfg.r_ref_ohms) * adc_cfg.gain * adc_cfg.getMaxCode());
    const int32_t raw_code2 = static_cast<int32_t>((139.6 / adc_cfg.r_ref_ohms) * adc_cfg.gain * adc_cfg.getMaxCode());

    std::cout << "  - Точка 1 (Лід, 0 °C): R_std = " << r_std1 << " Ом, АЦП code = " << raw_code1 << "\n";
    std::cout << "  - Точка 2 (Пара, 100 °C): R_std = " << r_std2 << " Ом, АЦП code = " << raw_code2 << "\n";

    if (sensor.calibrateTwoPoint(r_std1, raw_code1, r_std2, raw_code2)) {
        const auto& cal = sensor.getCalibrationParams();
        std::cout << "  -> Калібрування успішне!\n";
        std::cout << "     Зсув нуля (Offset): " << std::fixed << std::setprecision(4) << cal.offset_ohms << " Ом\n";
        std::cout << "     Масштабний множник (Scale): " << cal.scale_factor << "\n\n";
    } else {
        std::cerr << "  -> Помилка калібрування!\n\n";
    }

    // 4. Тестові вимірювання температури у різних діапазонах
    std::cout << "[3] Результати вимірювання температури у тестових точках:\n";
    std::cout << std::setw(12) << "Темп.(теорет)"
              << std::setw(12) << "Код АЦП"
              << std::setw(14) << "Сирий опір"
              << std::setw(16) << "Відкалібр.опір"
              << std::setw(14) << "Температура"
              << std::setw(12) << "Статус" << "\n";
    std::cout << "------------------------------------------------------------------------- \n";

    const std::vector<double> test_temperatures = {-50.0, 0.0, 25.0, 100.0, 250.0};

    for (double target_temp : test_temperatures) {
        const double ideal_r = sensor.getSolver().temperatureToResistance(target_temp);

        const auto& cal = sensor.getCalibrationParams();
        const double simulated_raw_r = (ideal_r - cal.offset_ohms) / cal.scale_factor;

        const int32_t code = static_cast<int32_t>((simulated_raw_r / adc_cfg.r_ref_ohms) * adc_cfg.gain * adc_cfg.getMaxCode());

        MeasurementResult res = sensor.processAdcCode(code);

        std::cout << std::setw(10) << std::fixed << std::setprecision(1) << target_temp << " °C"
                  << std::setw(12) << code
                  << std::setw(12) << std::setprecision(2) << res.resistance_raw_ohms << " Ом"
                  << std::setw(14) << std::setprecision(2) << res.resistance_cal_ohms << " Ом"
                  << std::setw(12) << std::setprecision(2) << res.temperature_c << " °C"
                  << std::setw(14) << statusToString(res.status) << "\n";
    }

    // 5. Демонстрація діагностики аварійних станів
    std::cout << "\n[4] Тестування діагностики та аварійних станів вимірювального кола:\n";

    // Обрив лінії (Open Circuit): АЦП видає максимальний код
    const int32_t open_circuit_code = static_cast<int32_t>(adc_cfg.getMaxCode());
    MeasurementResult open_res = sensor.processAdcCode(open_circuit_code);
    std::cout << "  - Обрив датчика (код " << open_circuit_code << "): Статус = "
              << statusToString(open_res.status) << "\n";

    // Коротке замикання (Short Circuit): АЦП видає 0 код
    const int32_t short_circuit_code = 0;
    MeasurementResult short_res = sensor.processAdcCode(short_circuit_code);
    std::cout << "  - Коротке замикання (код " << short_circuit_code << "): Статус = "
              << statusToString(short_res.status) << "\n";

    std::cout << "\n=========================================================\n";
    std::cout << "   Завершено демонстрацію C++ драйвера RtdSensor.\n";
    std::cout << "=========================================================\n";

    return 0;
}
