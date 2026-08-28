#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <span>
#include <optional>

struct MeasurementResult {
    float discriminator_error{0.0f}; /* Безрозмірна похибка затримки (-1..+1) */
    float prompt_power{0.0f};        /* Накопичена енергія центрального піку */
    float estimated_snr_db{0.0f};    /* Оцінка вихідного відношення сигнал/шум */
};

class CoherentIntegrator {
public:
    CoherentIntegrator(uint32_t sample_rate_hz, float t_coh_sec, 
                       uint32_t num_blocks, float initial_doppler_hz = 0.0f)
        : sample_rate_hz_(sample_rate_hz),
          n_coh_(std::max(1u, static_cast<uint32_t>(sample_rate_hz * t_coh_sec + 0.5f))),
          m_blocks_(std::max(1u, num_blocks)) {
        set_doppler(initial_doppler_hz);
    }

    void set_doppler(float doppler_hz) noexcept {
        doppler_hz_ = doppler_hz;
        phase_step_rad_ = static_cast<float>(2.0 * std::numbers::pi * doppler_hz_ / sample_rate_hz_);
    }

    /* Потокова обробка масиву відліків */
    std::optional<MeasurementResult> process_sample(
        std::complex<float> raw_sample,
        float code_early,
        float code_prompt,
        float code_late) noexcept {
        
        /* 1. Фазова компенсація несучої: rot = raw * exp(-j * phi) */
        float cos_phi = std::cos(nco_phase_rad_);
        float sin_phi = std::sin(nco_phase_rad_);
        std::complex<float> nco_rot{cos_phi, -sin_phi};
        std::complex<float> bb_sample = raw_sample * nco_rot;

        /* Оновлення фази NCO */
        nco_phase_rad_ += phase_step_rad_;
        if (nco_phase_rad_ >= 2.0f * std::numbers::pi_v<float>) {
            nco_phase_rad_ -= 2.0f * std::numbers::pi_v<float>;
        } else if (nco_phase_rad_ < 0.0f) {
            nco_phase_rad_ += 2.0f * std::numbers::pi_v<float>;
        }

        /* 2. Когерентне накопичення */
        acc_coh_e_ += bb_sample * code_early;
        acc_coh_p_ += bb_sample * code_prompt;
        acc_coh_l_ += bb_sample * code_late;
        coh_counter_++;

        /* 3. Перевірка завершення когерентного вікна T_coh */
        if (coh_counter_ >= n_coh_) {
            power_early_  += std::norm(acc_coh_e_);
            power_prompt_ += std::norm(acc_coh_p_);
            power_late_   += std::norm(acc_coh_l_);

            acc_coh_e_ = {0.0f, 0.0f};
            acc_coh_p_ = {0.0f, 0.0f};
            acc_coh_l_ = {0.0f, 0.0f};
            coh_counter_ = 0;
            block_counter_++;

            /* 4. Перевірка завершення повного вікна T_meas */
            if (block_counter_ >= m_blocks_) {
                MeasurementResult res{};
                float sum_el = power_early_ + power_late_;
                
                if (sum_el > 1e-12f) {
                    res.discriminator_error = (power_early_ - power_late_) / sum_el;
                }
                res.prompt_power = power_prompt_;

                float noise_floor = 0.5f * sum_el;
                if (noise_floor > 1e-12f && power_prompt_ > noise_floor) {
                    float snr_lin = (power_prompt_ - noise_floor) / noise_floor;
                    res.estimated_snr_db = 10.0f * std::log10(snr_lin);
                } else {
                    res.estimated_snr_db = -30.0f;
                }

                /* Скидання некогерентних акумуляторів */
                power_early_ = 0.0f;
                power_prompt_ = 0.0f;
                power_late_ = 0.0f;
                block_counter_ = 0;

                return res;
            }
        }
        return std::nullopt;
    }

    [[nodiscard]] uint32_t total_measurement_samples() const noexcept {
        return n_coh_ * m_blocks_;
    }

private:
    uint32_t sample_rate_hz_;
    uint32_t n_coh_;
    uint32_t m_blocks_;

    float doppler_hz_{0.0f};
    float nco_phase_rad_{0.0f};
    float phase_step_rad_{0.0f};

    std::complex<float> acc_coh_e_{0.0f, 0.0f};
    std::complex<float> acc_coh_p_{0.0f, 0.0f};
    std::complex<float> acc_coh_l_{0.0f, 0.0f};
    uint32_t coh_counter_{0};

    float power_early_{0.0f};
    float power_prompt_{0.0f};
    float power_late_{0.0f};
    uint32_t block_counter_{0};
};
