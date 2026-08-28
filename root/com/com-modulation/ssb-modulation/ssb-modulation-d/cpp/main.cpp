#include <cmath>
#include <vector>
#include <numbers>
#include <span>

class SsbModulator {
public:
    static constexpr std::size_t filter_taps = 31;

    SsbModulator(float f_carrier, float f_sample)
        : buffer_(filter_taps, 0.0f),
          hilbert_coeffs_(filter_taps, 0.0f),
          phase_inc_(2.0f * std::numbers::pi_v<float> * f_carrier / f_sample) 
    {
        init_filter();
    }

    /* Обробка блоку відліків аудиосигналу з поверненням векторного SSB виходу */
    [[nodiscard]] std::vector<float> process_block(std::span<const float> audio_in, bool is_usb) {
        std::vector<float> ssb_out;
        ssb_out.reserve(audio_in.size());

        for (float sample : audio_in) {
            ssb_out.push_back(process_sample(sample, is_usb));
        }
        return ssb_out;
    }

private:
    std::vector<float> buffer_;
    std::vector<float> hilbert_coeffs_;
    std::size_t buf_idx_{0};
    float phase_acc_{0.0f};
    float phase_inc_{0.0f};

    void init_filter() {
        constexpr int center = filter_taps / 2;
        for (int i = 0; i < static_cast<int>(filter_taps); ++i) {
            int n = i - center;
            if (n % 2 != 0) {
                float w = 0.54f - 0.46f * std::cos(2.0f * std::numbers::pi_v<float> * i / (filter_taps - 1));
                hilbert_coeffs_[i] = (2.0f / (std::numbers::pi_v<float> * static_cast<float>(n))) * w;
            }
        }
    }

    float process_sample(float audio_sample, bool is_usb) {
        buffer_[buf_idx_] = audio_sample;

        float q_audio = 0.0f;
        for (std::size_t i = 0; i < filter_taps; ++i) {
            std::size_t idx = (buf_idx_ + filter_taps - i) % filter_taps;
            q_audio += buffer_[idx] * hilbert_coeffs_[i];
        }

        std::size_t delay_idx = (buf_idx_ + filter_taps - (filter_taps / 2)) % filter_taps;
        float i_audio = buffer_[delay_idx];

        buf_idx_ = (buf_idx_ + 1) % filter_taps;

        float cos_c = std::cos(phase_acc_);
        float sin_c = std::sin(phase_acc_);

        phase_acc_ += phase_inc_;
        if (phase_acc_ >= 2.0f * std::numbers::pi_v<float>) {
            phase_acc_ -= 2.0f * std::numbers::pi_v<float>;
        }

        return is_usb ? (i_audio * cos_c - q_audio * sin_c)
                      : (i_audio * cos_c + q_audio * sin_c);
    }
};
