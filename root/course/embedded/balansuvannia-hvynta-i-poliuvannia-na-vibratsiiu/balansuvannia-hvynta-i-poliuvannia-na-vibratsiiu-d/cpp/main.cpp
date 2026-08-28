#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <span>
#include <algorithm>
#include <iomanip>
#include <string_view>

struct PeakInfo {
    float frequency_hz;
    float amplitude;
    std::string_view diagnosis;
};

struct VibrationReport {
    float total_rms;
    float motor_freq_hz;
    float bpf_freq_hz;
    std::vector<PeakInfo> dominant_peaks;
};

class VibrationSpectrumAnalyzer {
public:
    explicit VibrationSpectrumAnalyzer(float sample_rate_hz)
        : sample_rate_{sample_rate_hz} {}

    [[nodiscard]] VibrationReport analyze(
        std::span<const float> raw_samples,
        float expected_rpm,
        int num_blades) const {

        const size_t n = raw_samples.size();
        if ((n & (n - 1)) != 0 || n == 0) {
            throw std::invalid_argument("Розмір вибірки має бути степенем 2.");
        }

        // 1. Усунення постійного зсуву (DC offset)
        float mean = 0.0f;
        for (float s : raw_samples) mean += s;
        mean /= static_cast<float>(n);

        // 2. Накладання вікна Ганна та підготовка комплексного буфера
        std::vector<std::complex<float>> buffer(n);
        for (size_t i = 0; i < n; ++i) {
            const float window = 0.5f * (1.0f - std::cos(2.0f * std::numbers::pi_v<float> * static_cast<float>(i) / static_cast<float>(n - 1)));
            buffer[i] = {(raw_samples[i] - mean) * window, 0.0f};
        }

        // 3. Обчислення ШПФ (Radix-2 Cooley-Tukey)
        computeFFT(buffer);

        // 4. Амплітудний спектр і загальний RMS
        const size_t num_bins = n / 2;
        const float df = sample_rate_ / static_cast<float>(n);
        std::vector<float> magnitudes(num_bins);
        float total_energy = 0.0f;

        for (size_t i = 0; i < num_bins; ++i) {
            // Масштабування з урахуванням вікна Ганна (множник 4/N)
            magnitudes[i] = (std::abs(buffer[i]) * 4.0f) / static_cast<float>(n);
            total_energy += magnitudes[i] * magnitudes[i];
        }
        const float total_rms = std::sqrt(total_energy * 0.5f);

        // 5. Пошук локальних максимумів (піків)
        struct ScoredBin { size_t bin; float mag; };
        std::vector<ScoredBin> peaks;

        for (size_t i = 1; i < num_bins - 1; ++i) {
            if (magnitudes[i] > magnitudes[i - 1] && magnitudes[i] > magnitudes[i + 1]) {
                peaks.push_back({i, magnitudes[i]});
            }
        }

        std::sort(peaks.begin(), peaks.end(), [](const auto &a, const auto &b) {
            return a.mag > b.mag;
        });

        const float motor_hz = expected_rpm / 60.0f;
        const float bpf_hz = motor_hz * static_cast<float>(num_blades);

        VibrationReport report{
            .total_rms = total_rms,
            .motor_freq_hz = motor_hz,
            .bpf_freq_hz = bpf_hz,
            .dominant_peaks = {}
        };

        const size_t top_k = std::min<size_t>(3, peaks.size());
        for (size_t k = 0; k < top_k; ++k) {
            const float freq = static_cast<float>(peaks[k].bin) * df;
            const float amp = peaks[k].mag;
            std::string_view diag = "Структурний резонанс рами";

            if (std::abs(freq - motor_hz) <= 2.0f * df || std::abs(freq - motor_hz) / motor_hz < 0.05f) {
                diag = "1x RPM: Дисбаланс ротора/гвинта";
            } else if (std::abs(freq - bpf_hz) <= 2.0f * df || std::abs(freq - bpf_hz) / bpf_hz < 0.05f) {
                diag = "BPF: Аеродинамічна лопатева пульсація";
            }

            report.dominant_peaks.push_back({freq, amp, diag});
        }

        return report;
    }

private:
    float sample_rate_;

    static void computeFFT(std::span<std::complex<float>> x) {
        const size_t n = x.size();
        // Бітова інверсія
        for (size_t i = 0, j = 0; i < n - 1; ++i) {
            if (i < j) std::swap(x[i], x[j]);
            size_t k = n / 2;
            while (k <= j) { j -= k; k /= 2; }
            j += k;
        }

        for (size_t len = 2; len <= n; len <<= 1) {
            const float angle = -2.0f * std::numbers::pi_v<float> / static_cast<float>(len);
            const std::complex<float> wlen = std::polar(1.0f, angle);

            for (size_t i = 0; i < n; i += len) {
                std::complex<float> w{1.0f, 0.0f};
                for (size_t j = 0; j < len / 2; ++j) {
                    const auto u = x[i + j];
                    const auto v = x[i + j + len / 2] * w;
                    x[i + j] = u + v;
                    x[i + j + len / 2] = u - v;
                    w *= wlen;
                }
            }
        }
    }
};

int main() {
    constexpr size_t n = 1024;
    constexpr float sample_rate = 2000.0f; // Blackbox 2 кГц
    constexpr float rpm = 15000.0f;        // 250 Гц
    constexpr int blades = 3;              // BPF = 750 Гц

    std::vector<float> samples(n);
    for (size_t i = 0; i < n; ++i) {
        float t = static_cast<float>(i) / sample_rate;
        samples[i] = 8.5f * std::sin(2.0f * std::numbers::pi_v<float> * 250.0f * t)
                   + 3.2f * std::sin(2.0f * std::numbers::pi_v<float> * 750.0f * t)
                   + 5.0f * std::sin(2.0f * std::numbers::pi_v<float> * 410.0f * t)
                   + ((static_cast<float>(std::rand()) / RAND_MAX) - 0.5f) * 1.5f;
    }

    try {
        VibrationSpectrumAnalyzer analyzer(sample_rate);
        auto report = analyzer.analyze(samples, rpm, blades);

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== ЗВІТ СПЕКТРАЛЬНОГО АНАЛІЗУ BLACKBOX (C++20) ===\n";
        std::cout << "Частота 1x RPM: " << report.motor_freq_hz << " Гц | Лопатева BPF: " << report.bpf_freq_hz << " Гц\n";
        std::cout << "Загальний RMS вібрацій: " << report.total_rms << " град/с\n\n";
        std::cout << "Виявлені спектральні аномалії:\n";

        for (size_t idx = 0; const auto &peak : report.dominant_peaks) {
            std::cout << "  [" << ++idx << "] " << std::setw(6) << peak.frequency_hz
                      << " Гц | Амплітуда: " << std::setw(5) << peak.amplitude
                      << " | Причина: " << peak.diagnosis << '\n';
        }
    } catch (const std::exception &ex) {
        std::cerr << "Помилка аналізу: " << ex.what() << '\n';
    }

    return 0;
}
