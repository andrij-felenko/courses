#include "lcr_meter.hpp"
#include <iostream>
#include <iomanip>

int main() {
    std::cout << "=== Цифровий LCR-вимірювач із калібруванням Open/Short (C++17) ===\n\n";

    const double freq = 10000.0; // 10 кГц тестова частота
    LCRMeter meter(freq);

    std::cout << "Робоча частота: " << freq / 1000.0 << " кГц\n\n";

    // 1. Моделювання паразитних параметрів вимірювального кабелю та щупів:
    // Послідовний опір та індуктивність дротів щупів: R_cable = 0.15 Ом, L_cable = 0.8 мкГн
    const double omega = 2.0 * M_PI * freq;
    const std::complex<double> z_short_fixture{0.15, omega * 0.8e-6}; // ≈ 0.15 + j0.050 Ом

    // Паразитна ємність розімкнених щупів: C_stray = 25 пФ, опір витоку ізоляції R_leak = 20 МОм
    const double y_leak = 1.0 / 20.0e6;
    const double y_cap = omega * 25.0e-12;
    const std::complex<double> y_open_fixture{y_leak, y_cap};
    const std::complex<double> z_open_fixture = 1.0 / y_open_fixture;

    std::cout << "[Крок 1] Виконання калібрування щупів:\n";
    meter.calibrate_short(z_short_fixture);
    meter.calibrate_open(z_open_fixture);
    std::cout << "  - Short Cal: Z_short = " << z_short_fixture.real() << " + j" << z_short_fixture.imag() << " Ом\n";
    std::cout << "  - Open Cal:  Y_open  = " << y_open_fixture.real() * 1e9 << " нСм + j" << y_open_fixture.imag() * 1e6 << " мкСм\n\n";

    // 2. Тестовий зразок №1: Керамічний конденсатор C = 100 пФ з ESR = 0.5 Ом
    // Через високий імпеданс на 10 кГц (|Z_C| ≈ 159.15 кОм) паразитна ємність щупів 25 пФ без компенсації дасть похибку +25%!
    const double true_c = 100.0e-12;
    const double true_esr = 0.5;
    const std::complex<double> z_c_true{true_esr, -1.0 / (omega * true_c)};

    // Сирий виміряний імпеданс (зразок + паразити):
    // Z_raw = (Z_DUT || (1/Y_open)) + Z_short
    std::complex<double> y_dut_c = 1.0 / z_c_true;
    std::complex<double> z_raw_c = (1.0 / (y_dut_c + y_open_fixture)) + z_short_fixture;

    MeasurementResult res_c = meter.measure(z_raw_c);

    std::cout << "[Крок 2] Тестування зразка №1 (Конденсатор 100 пФ):\n";
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "  Сирий виміряний |Z_raw|: " << std::abs(res_c.z_raw) / 1000.0 << " кОм\n";
    std::cout << "  Скомпенсований  |Z_DUT|: " << std::abs(res_c.z_corrected) / 1000.0 << " кОм\n";
    std::cout << "  Відновлена ємність Cs:   " << res_c.c_series * 1e12 << " пФ (еталон: 100.0 пФ)\n";
    std::cout << "  Активний опір втрат Rs:  " << res_c.r_series << " Ом (еталон: 0.5 Ом)\n";
    std::cout << "  Тангенс втрат (D):       " << std::setprecision(5) << res_c.dissipation_factor << "\n\n";

    // 3. Тестовий зразок №2: Низькоомна індуктивність L = 10 мкГн, R_dc = 0.2 Ом
    // Тут впливає опір дротів 0.15 Ом (похибка 75% без Short Cal!)
    const double true_l = 10.0e-6;
    const double true_rl = 0.2;
    const std::complex<double> z_l_true{true_rl, omega * true_l};

    std::complex<double> y_dut_l = 1.0 / z_l_true;
    std::complex<double> z_raw_l = (1.0 / (y_dut_l + y_open_fixture)) + z_short_fixture;

    MeasurementResult res_l = meter.measure(z_raw_l);

    std::cout << "[Крок 3] Тестування зразка №2 (Індуктивність 10 мкГн):\n";
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "  Сирий активний опір Rs_raw: " << res_l.z_raw.real() << " Ом (із дротами щупів)\n";
    std::cout << "  Скомпенсований опір Rs_DUT: " << res_l.r_series << " Ом (еталон: 0.200 Ом)\n";
    std::cout << "  Відновлена індуктивність Ls: " << res_l.l_series * 1e6 << " мкГн (еталон: 10.000 мкГн)\n";
    std::cout << "  Добротність (Q):            " << res_l.quality_factor << "\n";

    return 0;
}
