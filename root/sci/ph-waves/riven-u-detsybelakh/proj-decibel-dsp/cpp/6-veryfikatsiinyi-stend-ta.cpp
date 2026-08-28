#include "decibel_dsp.hpp"
#include <iostream>
#include <vector>
#include <numbers>

int main() {
    using namespace dsp::acoustics;
    std::cout << "=== Перевірка модуля акустичних перетворень (C++20) ===\n\n";

    // 1. Перевірка калібратора 94 дБ SPL (1.0 Па)
    constexpr double p_cal = 1.0; // 1.0 Па RMS
    const double spl_cal = pressure_to_spl(p_cal);
    std::cout << "Акустичний калібратор: тиск = " << p_cal 
              << " Па -> SPL = " << spl_cal << " дБ (очікується 94.00 дБ)\n";

    // 2. Перевірка опорних напруг dBu та dBV
    std::cout << "+4 dBu (студійний стандарт) = " << dbu_to_voltage(4.0) << " В RMS\n";
    std::cout << "-10 dBV (побутовий стандарт) = " << dbv_to_voltage(-10.0) 
              << " В RMS (" << voltage_to_dbu(dbv_to_voltage(-10.0)) << " dBu)\n";

    // 3. Некогерентне підсумовування двох джерел по 80 дБ
    const std::vector<double> sources = {80.0, 80.0};
    std::cout << "Сума 80 дБ + 80 дБ = " << sum_noncoherent_spl(sources) 
              << " дБ (очікується 83.01 дБ)\n";

    // 4. Тестування фільтрації A-weighting на частоті 1 кГц
    AWeightingFilter filter;
    constexpr size_t fs = 48000;
    constexpr size_t num_samples = fs; // 1 секунда
    std::vector<double> sig_1k(num_samples);
    std::vector<double> out_1k(num_samples);

    for (size_t i = 0; i < num_samples; ++i) {
        sig_1k[i] = std::sqrt(2.0) * 1.0 * std::sin(2.0 * std::numbers::pi * 1000.0 * static_cast<double>(i) / fs);
    }
    filter.process_buffer(sig_1k, out_1k);

    std::span<const double> in_span{sig_1k.data() + 4800, num_samples - 4800};
    std::span<const double> out_span{out_1k.data() + 4800, num_samples - 4800};
    const double rms_in = calculate_rms(in_span);
    const double rms_out = calculate_rms(out_span);

    std::cout << "A-зважування на 1 кГц: Вхід RMS = " << rms_in 
              << " Па, Вихід RMS = " << rms_out 
              << " Па (Зсув = " << to_db_amplitude(rms_out, rms_in) << " дБ)\n";

    // 5. Перевірка швидкого логарифма
    constexpr uint32_t test_val = 1000000;
    std::cout << "Fast log10(1000000) = " << fast_log10(test_val) 
              << " (точне значення: 6.0000)\n";

    return 0;
}
