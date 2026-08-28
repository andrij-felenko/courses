#include <complex>
#include <span>
#include <vector>
#include <cmath>
#include <algorithm>

namespace zero_if {

// Адаптивний рекурсивний фільтр вилучення постійної складової (DCOC)
class DcocFilter {
public:
    explicit constexpr DcocFilter(float alpha = 0.001f) noexcept 
        : alpha_{alpha} {}

    // Обробка комплексної послідовності IQ відліків за допомогою std::span
    void process(std::span<std::complex<float>> samples) noexcept {
        const float one_minus_alpha = 1.0f - alpha_;

        for (auto& sample : samples) {
            mean_i_ = one_minus_alpha * mean_i_ + alpha_ * sample.real();
            mean_q_ = one_minus_alpha * mean_q_ + alpha_ * sample.imag();

            sample = {sample.real() - mean_i_, sample.imag() - mean_q_};
        }
    }

    [[nodiscard]] constexpr std::complex<float> current_offset() const noexcept {
        return {mean_i_, mean_q_};
    }

    void reset() noexcept {
        mean_i_ = 0.0f;
        mean_q_ = 0.0f;
    }

private:
    float alpha_;
    float mean_i_{0.0f};
    float mean_q_{0.0f};
};

// Адаптивний компенсатор IQ дисбалансу на базі ортогоналізації Ґрама-Шмідта
class IqCalibrator {
public:
    explicit constexpr IqCalibrator(float adaptation_rate = 0.0005f) noexcept
        : mu_{adaptation_rate} {}

    void process(std::span<std::complex<float>> samples) noexcept {
        for (auto& sample : samples) {
            const float i_in = sample.real();
            const float q_in = sample.imag();

            // Оновлення ковзних оцінок потужностей та взаємної кореляції
            p_i_  = (1.0f - mu_) * p_i_  + mu_ * (i_in * i_in);
            p_q_  = (1.0f - mu_) * p_q_  + mu_ * (q_in * q_in);
            p_iq_ = (1.0f - mu_) * p_iq_ + mu_ * (i_in * q_in);

            if (p_i_ > 1e-9f && p_q_ > 1e-9f) {
                c_phase_ = p_iq_ / p_i_;
                c_gain_  = std::sqrt(p_i_ / p_q_);
            }

            // Корекція фазового та амплітудного розбалансу
            const float i_corr = i_in;
            const float q_corr = (q_in - c_phase_ * i_in) * c_gain_;

            sample = {i_corr, q_corr};
        }
    }

    [[nodiscard]] std::pair<float, float> current_coefficients() const noexcept {
        return {c_phase_, c_gain_};
    }

private:
    float mu_;
    float p_i_{1.0f};
    float p_q_{1.0f};
    float p_iq_{0.0f};
    float c_phase_{0.0f};
    float c_gain_{1.0f};
};

// Повний тракт базової обробки Zero-IF
class ZeroIfBasebandProcessor {
public:
    explicit ZeroIfBasebandProcessor(float dcoc_alpha = 0.001f, float iq_mu = 0.0005f)
        : dcoc_{dcoc_alpha}, iq_calib_{iq_mu} {}

    void process_frame(std::span<std::complex<float>> buffer) noexcept {
        dcoc_.process(buffer);
        iq_calib_.process(buffer);
    }

private:
    DcocFilter dcoc_;
    IqCalibrator iq_calib_;
};

} // namespace zero_if
