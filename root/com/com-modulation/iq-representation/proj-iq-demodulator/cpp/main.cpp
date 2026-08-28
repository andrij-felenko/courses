#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <numeric>
#include <span>

// Комплексний відлік базової смуги
using IQSample = std::complex<float>;

// Клас цифрового ФНЧ з автозбереженням стану (RAII)
class LowPassFilter {
public:
    explicit LowPassFilter(float alpha) noexcept : alpha_(alpha), state_(0.0f) {}

    [[nodiscard]] float process(float input) noexcept {
        state_ += alpha_ * (input - state_);
        return state_;
    }

    void reset() noexcept { state_ = 0.0f; }

private:
    float alpha_;
    float state_;
};

// Усунення DC offset за допомогою std::span та алгоритмів STL
void correct_dc_offset(std::span<IQSample> samples) noexcept {
    if (samples.empty()) return;

    IQSample sum = std::accumulate(samples.begin(), samples.end(), IQSample{0.0f, 0.0f});
    IQSample mean = sum / static_cast<float>(samples.size());

    for (auto& sample : samples) {
        sample -= mean;
    }
}

// Алгоритм цифрової ортогоналізації Грама-Шмідта для компенсації IQ-дисбалансу
void correct_iq_imbalance(std::span<IQSample> samples, float phase_error_rad, float gain_ratio) noexcept {
    float tan_ph = std::tan(phase_error_rad);
    float sec_ph = 1.0f / std::cos(phase_error_rad);

    for (auto& s : samples) {
        float i_corr = s.real();
        float q_corr = (s.imag() - i_corr * tan_ph) * sec_ph * gain_ratio;
        s = IQSample{i_corr, q_corr};
    }
}

// Ідіоматичний C++ конвеєр обробки IQ-сигналу
void run_iq_pipeline_cpp(size_t num_samples, float sample_rate, float carrier_freq) {
    std::vector<IQSample> tx_iq(num_samples);
    std::vector<float> rf_signal(num_samples);
    std::vector<IQSample> rx_iq(num_samples);

    constexpr float mod_freq = 1000.0f; // 1 кГц

    // 1. Генерація комплексного огинаючого z(t) = e^(j w_m t)
    for (size_t n = 0; n < num_samples; ++n) {
        float t = static_cast<float>(n) / sample_rate;
        float phase = 2.0f * std::numbers::pi_v<float> * mod_freq * t;
        tx_iq[n] = std::polar(1.0f, phase);
    }

    // 2. Цифрова квадратурна модуляція (Upconversion): Re{ z(t) * e^(j w_c t) }
    for (size_t n = 0; n < num_samples; ++n) {
        float t = static_cast<float>(n) / sample_rate;
        float wc = 2.0f * std::numbers::pi_v<float> * carrier_freq * t;
        rf_signal[n] = tx_iq[n].real() * std::cos(wc) - tx_iq[n].imag() * std::sin(wc);
    }

    // 3. Цифрова квадратурна демодуляція
    LowPassFilter lpf_i(0.05f);
    LowPassFilter lpf_q(0.05f);

    for (size_t n = 0; n < num_samples; ++n) {
        float t = static_cast<float>(n) / sample_rate;
        float wc = 2.0f * std::numbers::pi_v<float> * carrier_freq * t;

        float raw_i = rf_signal[n] * std::cos(wc);
        float raw_q = rf_signal[n] * (-std::sin(wc));

        rx_iq[n] = IQSample{
            2.0f * lpf_i.process(raw_i),
            2.0f * lpf_q.process(raw_q)
        };
    }

    // 4. Корекція постійного зсуву та дисбалансу
    correct_dc_offset(rx_iq);
    correct_iq_imbalance(rx_iq, 0.01f, 1.02f); // Компенсація фазової помилки 0.01 рад та несиметрії 2%

    std::cout << "Контрольний відлік C++ [100]: TX " << tx_iq[100] << " -> RX " << rx_iq[100] << '\n';
}
