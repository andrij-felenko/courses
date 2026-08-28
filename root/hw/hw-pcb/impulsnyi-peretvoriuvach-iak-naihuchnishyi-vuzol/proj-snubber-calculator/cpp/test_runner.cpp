/* test_runner.cpp */
#include "snubber_filter_calc.hpp"
#include <cassert>

void test_cpp_snubber() {
    std::cout << "=== C++20 ТЕСТ 1: Синхронний Buck 12V ===\n";
    using namespace power_emc;

    const SnubberSpec spec{
        .f1 = Frequency(185.0e6),
        .f2 = Frequency(118.0e6),
        .c_test = Capacitance(330.0e-12),
        .v_in_volts = 13.5,
        .f_sw = Frequency(2.2e6),
        .cap_multiplier = 3.0
    };

    const auto res = design_snubber(spec);
    assert(res.has_value());

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "C_par:         " << res->c_par.to_pf() << " пФ\n";
    std::cout << "L_par:         " << res->l_par.to_nh() << " нГн\n";
    std::cout << "Z0:            " << res->z0.ohms << " Ом\n";
    std::cout << "R_snub (E24):  " << res->r_snub_e24.ohms << " Ом\n";
    std::cout << "C_snub (E24):  " << res->c_snub_e24.to_pf() << " пФ\n";
    std::cout << "Теплові втрати: " << res->p_loss.to_mw() << " мВт\n";
    std::cout << "Піковий струм: " << res->i_peak_amps << " А\n\n";

    assert(res->c_par.to_pf() > 100.0 && res->c_par.to_pf() < 300.0);
}

void test_cpp_filter() {
    std::cout << "=== C++20 ТЕСТ 2: Вхідний EMI-фільтр Міддлбрука ===\n";
    using namespace power_emc;

    const FilterSpec spec{
        .v_in_min_v = 18.0,
        .p_out = Power(40.0),
        .efficiency = 0.92,
        .f_sw = Frequency(500.0e3),
        .target_attenuation_db = 36.0,
        .l_filter = Inductance(4.7e-6)
    };

    const auto res = design_input_filter(spec);
    assert(res.has_value());

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "R_in DC-DC:    " << res->r_in_converter.ohms << " Ом\n";
    std::cout << "Частота зрізу: " << res->f_cutoff_ideal.to_khz() << " кГц\n";
    std::cout << "C2 (E24):      " << res->c_filter_e24.to_uf() << " мкФ\n";
    std::cout << "Cd (E12):      " << res->c_damping_e12.to_uf() << " мкФ\n";
    std::cout << "Rd (E24):      " << res->r_damping_e24.ohms << " Ом\n";
    std::cout << "Z_out_max:     " << res->z_out_max.ohms << " Ом\n";
    std::cout << "Запас стійкості: " << res->stability_margin << " (" 
              << (res->is_stable ? "СТІЙКИЙ" : "НЕСТІЙКИЙ") << ")\n\n";

    assert(res->is_stable);
}

int main() {
    test_cpp_snubber();
    test_cpp_filter();
    std::cout << "УСІ C++20 ТЕСТИ ПРОЙДЕНО УСПІШНО!\n";
    return 0;
}
