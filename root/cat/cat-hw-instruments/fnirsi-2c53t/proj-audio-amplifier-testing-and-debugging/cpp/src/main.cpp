#include "waveform_analyzer.hpp"
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>

int main() {
    // Параметри вимірювального експерименту з осцилографом FNIRSI 2C53T
    constexpr double sample_rate_hz = 1'000'000.0; // 1 MSa/s
    constexpr std::size_t num_samples = 1000;
    constexpr double signal_freq_hz = 1000.0;     // Аудіосигнал 1 кГц
    constexpr double phase_true_deg = 45.0;       // Заданий фазовий зсув підсилювача
    constexpr double phase_rad = phase_true_deg * std::numbers::pi / 180.0;

    std::vector<double> ch1_buffer(num_samples); // Вхідний сигнал CH1
    std::vector<double> ch2_buffer(num_samples); // Вихідний сигнал CH2 (з підсиленням та зсувом)

    // Симуляція зняття відліків АЦП
    for (std::size_t i = 0; i < num_samples; ++i) {
        const double t = static_cast<double>(i) / sample_rate_hz;
        // CH1: Синусоїда 1.0 Vpp (амплітуда 0.5 В)
        ch1_buffer[i] = 0.5 * std::sin(2.0 * std::numbers::pi * signal_freq_hz * t);
        
        // CH2: Підсилений сигнал у 1.414 разів (3 дБ) з фазовим зсувом 45°
        ch2_buffer[i] = 0.5 * 1.414 * std::sin(2.0 * std::numbers::pi * signal_freq_hz * t + phase_rad);
    }

    try {
        WaveformAnalyzer analyzer(sample_rate_hz, 3.2); // Поріг АЦП 3.2 В
        const DualChannelResult res = analyzer.analyze_dual(ch1_buffer, ch2_buffer);

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== Результати цифрового аналізу сигнатур FNIRSI 2C53T ===" << std::endl;
        std::cout << "Канал 1 (Вхід):  Vpp = " << res.ch1_metrics.v_pp << " В, Vrms = " << res.ch1_metrics.v_rms << " В" << std::endl;
        std::cout << "Канал 2 (Вихід): Vpp = " << res.ch2_metrics.v_pp << " В, Vrms = " << res.ch2_metrics.v_rms << " В" << std::endl;
        std::cout << "Частота сигналу: " << res.ch1_metrics.frequency_hz << " Гц" << std::endl;
        std::cout << "Коефіцієнт підсилення: " << res.gain_linear << "x (" << res.gain_db << " дБ)" << std::endl;
        std::cout << "Фазовий зсув (CH2-CH1): " << res.phase_shift_deg << " град" << std::endl;
        std::cout << "Кліпінг CH1: " << (res.ch1_metrics.is_clipped ? "ВИЯВЛЕНО!" : "Немає") << std::endl;
        std::cout << "Кліпінг CH2: " << (res.ch2_metrics.is_clipped ? "ВИЯВЛЕНО!" : "Немає") << std::endl;

    } catch (const std::exception& ex) {
        std::cerr << "Помилка опрацювання: " << ex.what() << std::endl;
        return 1;
    }

    return 0;
}
