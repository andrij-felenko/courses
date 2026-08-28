#include <iostream>
#include <cmath>
#include <numbers>
#include <algorithm>

struct TimingConfig {
    float t_coh_sec{0.001f};        // Когерентне вікно, с
    int   m_noncoh_blocks{1};       // Кількість некогерентних блоків
    float t_total_meas_sec{0.001f}; // Повний час вимірювання T_meas, с
    float expected_sigma_m{0.0f};   // Очікувана похибка дальності за CRLB, м
};

class MeasurementTimePlanner {
public:
    static constexpr float C_LIGHT = 299792458.0f;

    [[nodiscard]] static TimingConfig plan(
        float cn0_db_hz,
        float bandwidth_hz,
        float vehicle_accel_mps2,
        float channel_tc_sec) noexcept {
        
        TimingConfig cfg{};

        // 1. Обмеження когерентного вікна часом когерентності та бітовою межею
        const float max_allowed_t_coh = std::min(0.020f, channel_tc_sec);

        if (vehicle_accel_mps2 > 20.0f) {
            cfg.t_coh_sec = 0.001f; // 1 мс для екстремального маневру
        } else if (vehicle_accel_mps2 > 5.0f) {
            cfg.t_coh_sec = 0.005f; // 5 мс
        } else {
            cfg.t_coh_sec = std::min(0.010f, max_allowed_t_coh);
        }

        // 2. Вибір числа некогерентних блоків M за рівнем C/N0
        if (cn0_db_hz < 30.0f) {
            cfg.m_noncoh_blocks = (vehicle_accel_mps2 > 10.0f) ? 10 : 50;
        } else if (cn0_db_hz < 40.0f) {
            cfg.m_noncoh_blocks = (vehicle_accel_mps2 > 10.0f) ? 5 : 20;
        } else {
            cfg.m_noncoh_blocks = (vehicle_accel_mps2 > 10.0f) ? 1 : 5;
        }

        cfg.t_total_meas_sec = cfg.t_coh_sec * static_cast<float>(cfg.m_noncoh_blocks);

        // 3. Теоретична похибка дальності за межею Крамера-Рао
        const float snr_linear = std::pow(10.0f, (cn0_db_hz - 10.0f * std::log10(bandwidth_hz)) / 10.0f);
        const float denom = 2.0f * std::numbers::pi_v<float> * bandwidth_hz * 
                            std::sqrt(2.0f * snr_linear * bandwidth_hz * cfg.t_total_meas_sec);
        const float sigma_tau = std::sqrt(3.0f) / denom;
        cfg.expected_sigma_m = sigma_tau * C_LIGHT;

        return cfg;
    }
};
