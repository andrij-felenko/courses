#ifndef WAVEFORM_ANALYZER_HPP
#define WAVEFORM_ANALYZER_HPP

#include <vector>
#include <span>
#include <cstdint>
#include <string>

// Метрики сигналу окремого каналу осцилографа
struct WaveformMetrics {
    double v_max{0.0};       // Максимальна напруга [В]
    double v_min{0.0};       // Мінімальна напруга [В]
    double v_pp{0.0};        // Пікова амплітуда (Vpp) [В]
    double v_rms{0.0};       // Середньоквадратичне значення (Vrms) [В]
    double frequency_hz{0.0};// Обчислена частота сигналу [Гц]
    bool is_clipped{false};  // Прапорець амплітудного обрізання (кліпінгу)
};

// Результати порівняльного аналізу двох каналів (CH1 та CH2)
struct DualChannelResult {
    WaveformMetrics ch1_metrics; // Метрики каналу 1 (вхід)
    WaveformMetrics ch2_metrics; // Метрики каналу 2 (вихід)
    double gain_linear{0.0};     // Коефіцієнт підсилення (Vpp2 / Vpp1)
    double gain_db{0.0};         // Коефіцієнт підсилення в децибелах [дБ]
    double time_delay_s{0.0};    // Часова затримка між каналами [с]
    double phase_shift_deg{0.0}; // Фазовий зсув (CH2 відносно CH1) [град]
};

// Клас цифрового аналізатора сигналів для осцилографа FNIRSI 2C53T
class WaveformAnalyzer {
public:
    // Конструктор: приймає частоту дискретизації АЦП та поріг кліпінгу (вольти)
    explicit WaveformAnalyzer(double sample_rate_hz, double clip_threshold_v = 3.2);

    // Аналіз одного каналу
    [[nodiscard]] WaveformMetrics analyze_channel(std::span<const double> samples) const;

    // Спільний аналіз двох каналів для побудови АЧХ та фазочастотної характеристики
    [[nodiscard]] DualChannelResult analyze_dual(std::span<const double> ch1_samples,
                                                 std::span<const double> ch2_samples) const;

private:
    double sample_rate_hz_;     // Частота дискретизації АЦП [Гц]
    double clip_threshold_v_;   // Порогова напруга насичення тракту АЦП [В]

    // Допоміжний метод виявлення переходу через середній рівень (zero-crossing)
    [[nodiscard]] double find_first_rising_zero_crossing(std::span<const double> samples, double offset_v) const;
};

#endif // WAVEFORM_ANALYZER_HPP
