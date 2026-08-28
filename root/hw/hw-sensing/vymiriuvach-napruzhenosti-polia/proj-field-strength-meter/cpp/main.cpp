#include <array>
#include <span>
#include <cmath>
#include <concepts>
#include <optional>
#include <algorithm>

constexpr float WAVE_IMPEDANCE_VACUUM = 376.730313f;
constexpr std::size_t DEFAULT_RMS_WINDOW = 360; // 6 хвилин при 1 Гц

struct CalPoint {
    float freq_mhz;
    float af_db;
};

struct FieldMetrics {
    float e_x{0.0f};
    float e_y{0.0f};
    float e_z{0.0f};
    float e_total{0.0f};
    float s_power_wm2{0.0f};
    float e_rms_window{0.0f};
    float exposure_pct{0.0f};
};

template <std::size_t CalPointsMax = 32, std::size_t WindowSize = DEFAULT_RMS_WINDOW>
class FieldMeterProcessor {
public:
    struct Config {
        std::array<CalPoint, CalPointsMax> cal_table{};
        std::size_t cal_count{0};
        std::array<std::array<float, 3>, 3> ortho_matrix{
            std::array<float, 3>{1.0f, 0.0f, 0.0f},
            std::array<float, 3>{0.0f, 1.0f, 0.0f},
            std::array<float, 3>{0.0f, 0.0f, 1.0f}
        };
        float temp_coeff_v_per_c{0.0f};
        float t_cal_celsius{25.0f};
        std::array<float, 3> v_offset{0.0f, 0.0f, 0.0f};
    };

    explicit constexpr FieldMeterProcessor(Config config) noexcept 
        : config_(std::move(config)) {}

    [[nodiscard]] std::optional<FieldMetrics> process(
        std::span<const float, 3> v_raw, 
        float temp_celsius, 
        float target_freq_mhz) noexcept 
    {
        if (config_.cal_count == 0 || target_freq_mhz <= 0.0f) {
            return std::nullopt;
        }

        // 1. Температурна компенсація
        const float temp_delta = temp_celsius - config_.t_cal_celsius;
        std::array<float, 3> v_comp{};
        for (std::size_t i = 0; i < 3; ++i) {
            float v_adj = (v_raw[i] - config_.v_offset[i]) - (temp_delta * config_.temp_coeff_v_per_c);
            v_comp[i] = std::max(0.0f, v_adj);
        }

        // 2. Ортогоналізація
        std::array<float, 3> v_ortho{0.0f, 0.0f, 0.0f};
        for (std::size_t r = 0; r < 3; ++r) {
            for (std::size_t c = 0; c < 3; ++c) {
                v_ortho[r] += config_.ortho_matrix[r][c] * v_comp[c];
            }
            v_ortho[r] = std::max(0.0f, v_ortho[r]);
        }

        // 3. Інтерполяція антенного фактора
        const float af_db = interpolate_af(target_freq_mhz);
        const float af_lin = std::pow(10.0f, af_db / 20.0f);

        // 4. Обчислення векторних компонентів
        FieldMetrics m{};
        m.e_x = v_ortho[0] * af_lin;
        m.e_y = v_ortho[1] * af_lin;
        m.e_z = v_ortho[2] * af_lin;

        const float e_sq = m.e_x * m.e_x + m.e_y * m.e_y + m.e_z * m.e_z;
        m.e_total = std::sqrt(e_sq);
        m.s_power_wm2 = e_sq / WAVE_IMPEDANCE_VACUUM;

        // 5. Кільцевий RMS акумулятор
        update_rms(e_sq);
        m.e_rms_window = std::sqrt(ring_sum_sq_ / static_cast<float>(ring_count_));

        // 6. Санітарний ліміт ICNIRP 2020
        const float limit = calculate_icnirp_limit(target_freq_mhz);
        m.exposure_pct = (m.e_rms_window / limit) * 100.0f;

        return m;
    }

    void reset_rms() noexcept {
        ring_head_ = 0;
        ring_count_ = 0;
        ring_sum_sq_ = 0.0f;
        ring_buffer_.fill(0.0f);
    }

private:
    [[nodiscard]] float interpolate_af(float freq_mhz) const noexcept {
        const auto& table = config_.cal_table;
        if (freq_mhz <= table[0].freq_mhz) return table[0].af_db;
        if (freq_mhz >= table[config_.cal_count - 1].freq_mhz) {
            return table[config_.cal_count - 1].af_db;
        }

        for (std::size_t i = 0; i < config_.cal_count - 1; ++i) {
            if (freq_mhz >= table[i].freq_mhz && freq_mhz <= table[i + 1].freq_mhz) {
                const float t = (freq_mhz - table[i].freq_mhz) / 
                                (table[i + 1].freq_mhz - table[i].freq_mhz);
                return table[i].af_db + t * (table[i + 1].af_db - table[i].af_db);
            }
        }
        return table[0].af_db;
    }

    void update_rms(float e_sq) noexcept {
        if (ring_count_ == WindowSize) {
            ring_sum_sq_ -= ring_buffer_[ring_head_];
        } else {
            ++ring_count_;
        }
        ring_buffer_[ring_head_] = e_sq;
        ring_sum_sq_ = std::max(0.0f, ring_sum_sq_ + e_sq);
        ring_head_ = (ring_head_ + 1) % WindowSize;
    }

    [[nodiscard]] static constexpr float calculate_icnirp_limit(float freq_mhz) noexcept {
        if (freq_mhz < 0.1f) return 614.0f;
        if (freq_mhz <= 30.0f) return 87.0f / std::sqrt(freq_mhz);
        if (freq_mhz <= 400.0f) return 28.0f;
        if (freq_mhz <= 2000.0f) return 1.375f * std::sqrt(freq_mhz);
        return 61.0f;
    }

    Config config_;
    std::array<float, WindowSize> ring_buffer_{};
    std::size_t ring_head_{0};
    std::size_t ring_count_{0};
    float ring_sum_sq_{0.0f};
};
