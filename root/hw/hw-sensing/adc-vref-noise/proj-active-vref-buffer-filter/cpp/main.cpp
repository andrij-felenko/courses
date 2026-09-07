#include "vref_buffer_model.hpp"
#include <iostream>
#include <iomanip>

int main() {
    std::cout << "==========================================================\n";
    std::cout << " Моделювання буфера VREF з in-loop компенсацією для SAR АЦП\n";
    std::cout << "==========================================================\n\n";

    // 1. Прецизійний підсилювач (аналог ультранизькошумного ОП)
    // GBW = 20 МГц, Aol = 130 дБ, Rout = 50 Ом, SR = 10 В/мкс
    sensing::OpAmpModel opamp(20.0e6, 130.0, 50.0, 10.0);

    // 2. Параметри схеми in-loop компенсації
    // Riso = 2.2 Ом, Rf = 10 кОм, Cf = 100 нФ, Cload = 47 мкФ
    sensing::InLoopCompensation compensation(2.2, 10000.0, 100.0e-9, 47.0e-6);

    std::cout << "[1] Перевірка стійкості петлі зворотного зв'язку:\n";
    std::cout << "    - Необхідне Cf >= C_load * (R_iso / R_f) = "
              << (compensation.c_load_f * (compensation.r_iso_ohm / compensation.r_f_ohm)) * 1.0e9 << " нФ\n";
    std::cout << "    - Фактичне Cf = " << compensation.c_f_f * 1.0e9 << " нФ\n";
    std::cout << "    - Коефіцієнт запасу стійкості = " << compensation.compensation_ratio() << "\n";
    std::cout << "    - Стан контуру: "
              << (compensation.is_stable() ? "СТІЙКИЙ (фазовий запас > 45 град)" : "НЕСТІЙКИЙ (ризик генерації)")
              << "\n\n";

    // 3. Налаштування АЦП: VREF = 5.0 В, 18 біт, час такту зрівноваження = 200 нс
    const double vref_nominal = 5.0;
    const int adc_resolution = 18;
    const double charge_pulse = 200.0e-12; // 200 пКл імпульс перемикання CDAC
    const double bit_trial_time = 200.0e-9; // 200 нс

    sensing::VrefBufferSimulator sim(opamp, compensation, vref_nominal, adc_resolution);
    double lsb = sim.lsb_voltage();

    std::cout << "[2] Параметри аналого-цифрового перетворювача:\n";
    std::cout << "    - Номінальна опорна напруга VREF: " << vref_nominal << " В\n";
    std::cout << "    - Розрядність: " << adc_resolution << " біт\n";
    std::cout << "    - Вага молодшого розряду (1 LSB): " << lsb * 1.0e6 << " мкВ\n";
    std::cout << "    - Допустима динамічна похибка (0.5 LSB): " << (lsb * 0.5) * 1.0e6 << " мкВ\n\n";

    // 4. Запуск симуляції динамічного відновлення
    auto result = sim.simulate_step_response(charge_pulse, bit_trial_time, 20);

    std::cout << "[3] Результати симуляції перехідного процесу відновлення:\n";
    std::cout << "    - Початкове просідання VREF: " << result.max_voltage_drop_v * 1.0e6 << " мкВ\n";
    std::cout << "    - Залишкова похибка наприкінці такту: " << result.final_settling_error_v * 1.0e6 << " мкВ\n";
    std::cout << "    - Похибка у частках LSB: " << std::fixed << std::setprecision(4)
              << result.error_in_lsb << " LSB\n";
    std::cout << "    - Відповідність специфікації (< 0.5 LSB): "
              << (result.meets_half_lsb_spec ? "ТАК (без втрати кодів)" : "НІ (деградація DNL/INL)")
              << "\n\n";

    std::cout << "[4] Часовий графік відновлення VREF:\n";
    std::cout << "    Час (нс) | Напруга VREF (В) | Відхилення (мкВ)\n";
    std::cout << "    -------------------------------------------\n";
    for (size_t i = 0; i < result.time_points.size(); i += 2) {
        double t_ns = result.time_points[i] * 1.0e9;
        double v = result.vref_voltages[i];
        double dev_uv = (vref_nominal - v) * 1.0e6;
        std::cout << "    " << std::setw(8) << std::fixed << std::setprecision(1) << t_ns
                  << " | " << std::setw(16) << std::setprecision(6) << v
                  << " | " << std::setw(14) << std::setprecision(2) << dev_uv << "\n";
    }

    return 0;
}
