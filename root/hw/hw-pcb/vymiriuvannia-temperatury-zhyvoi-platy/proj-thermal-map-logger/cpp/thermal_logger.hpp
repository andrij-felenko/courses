/**
 * @file thermal_logger.hpp
 * @brief Об'єктно-орієнтований аналітичний модуль теплового профілювання плати.
 * Стандарт: C++20 (strong typing, constexpr математика, std::span, std::expected).
 */

#pragma once

#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <string>
#include <string_view>
#include <cmath>
#include <algorithm>
#include <expected>
#include <iomanip>
#include <numbers>

namespace pcb_thermal {

enum class SensorType : uint8_t {
    ThermocoupleK,
    DigitalIC,
    LwirRadiometric
};

enum class ThermalAlert : uint32_t {
    None         = 0,
    HotspotWarn  = 1 << 0,
    GradientWarn = 1 << 1,
    RunawayWarn  = 1 << 2,
    SensorFault  = 1 << 3
};

[[nodiscard]] constexpr ThermalAlert operator|(ThermalAlert a, ThermalAlert b) noexcept {
    return static_cast<ThermalAlert>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

[[nodiscard]] constexpr bool has_flag(ThermalAlert flags, ThermalAlert mask) noexcept {
    return (static_cast<uint32_t>(flags) & static_cast<uint32_t>(mask)) != 0;
}

struct Point2D {
    float x_mm{0.0f};
    float y_mm{0.0f};
};

struct ChannelConfig {
    uint8_t id{0};
    std::string name;
    SensorType type{SensorType::DigitalIC};
    Point2D pos;
    float emissivity{0.95f};       ///< Випромінювальна здатність поверхні
    float psi_jt{1.2f};            ///< Параметр JESD51 Psi-JT (°C/Вт)
    float power_dissipation_w{0.0f}; ///< Потужність втрат компонента (Вт)
    float critical_temp_c{125.0f}; ///< Гранична температура кристала
};

struct ChannelState {
    float measured_temp_c{25.0f};
    float junction_temp_c{25.0f};
    float rate_of_rise_cps{0.0f};
    bool is_valid{true};
};

class NistPolynomialK {
public:
    /// Коефіцієнти NIST ITS-90 для діапазону 0 .. 500 °C
    static constexpr std::array<double, 10> kCoeffs = {
        0.0,
        2.508355e1,
        7.860106e-2,
        -2.503131e-1,
        8.315270e-2,
        -1.228034e-2,
        9.804036e-4,
        -4.413030e-5,
        1.057734e-6,
        -1.052755e-8
    };

    [[nodiscard]] static constexpr float voltage_to_temperature(float v_mv) noexcept {
        if (v_mv < -6.0f || v_mv > 55.0f) {
            return -999.0f;
        }
        double temp = 0.0;
        double v_pow = 1.0;
        for (size_t i = 1; i < kCoeffs.size(); ++i) {
            v_pow *= static_cast<double>(v_mv);
            temp += kCoeffs[i] * v_pow;
        }
        return static_cast<float>(temp);
    }

    [[nodiscard]] static constexpr float cold_junction_emf(float t_cjc_c) noexcept {
        constexpr float seebeck_k = 0.0405f; // мВ/°C
        return t_cjc_c * seebeck_k;
    }
};

class RadiometryEngine {
public:
    [[nodiscard]] static float correct_emissivity(float t_apparent_c, float emissivity, float t_refl_c) noexcept {
        const float eps = std::max(emissivity, 0.02f);
        const float t_app_k = t_apparent_c + 273.15f;
        const float t_refl_k = t_refl_c + 273.15f;

        const float w_app = std::pow(t_app_k, 4.0f);
        const float w_refl = std::pow(t_refl_k, 4.0f);

        const float w_obj = (w_app - (1.0f - eps) * w_refl) / eps;
        if (w_obj <= 0.0f) {
            return t_refl_c;
        }
        return std::pow(w_obj, 0.25f) - 273.15f;
    }
};

template <size_t Rows = 4, size_t Cols = 4>
class ThermalProfiler {
public:
    explicit ThermalProfiler(float ambient_c = 25.0f, float pitch_x = 10.0f, float pitch_y = 10.0f)
        : ambient_temp_c_(ambient_c), reflected_temp_c_(ambient_c),
          grid_pitch_x_mm_(pitch_x), grid_pitch_y_mm_(pitch_y) {}

    bool register_channel(const ChannelConfig& config) {
        if (configs_.size() >= 32) return false;
        configs_.push_back(config);
        states_.push_back(ChannelState{.measured_temp_c = ambient_temp_c_, .junction_temp_c = ambient_temp_c_});
        return true;
    }

    void update_measurement(size_t index, float raw_reading, float dt_seconds) noexcept {
        if (index >= configs_.size()) return;

        const auto& cfg = configs_[index];
        auto& st = states_[index];

        float computed_t = 0.0f;

        switch (cfg.type) {
            case SensorType::ThermocoupleK: {
                const float v_cjc = NistPolynomialK::cold_junction_emf(ambient_temp_c_);
                const float v_total = raw_reading + v_cjc;
                computed_t = NistPolynomialK::voltage_to_temperature(v_total);
                if (computed_t < -100.0f) {
                    st.is_valid = false;
                    return;
                }
                break;
            }
            case SensorType::LwirRadiometric: {
                computed_t = RadiometryEngine::correct_emissivity(raw_reading, cfg.emissivity, reflected_temp_c_);
                break;
            }
            case SensorType::DigitalIC:
            default: {
                computed_t = raw_reading;
                break;
            }
        }

        if (dt_seconds > 0.001f) {
            st.rate_of_rise_cps = (computed_t - st.measured_temp_c) / dt_seconds;
        }
        st.measured_temp_c = computed_t;
        st.junction_temp_c = computed_t + (cfg.psi_jt * cfg.power_dissipation_w);
        st.is_valid = true;
    }

    void evaluate_thermal_field() noexcept {
        alert_flags_ = ThermalAlert::None;
        max_board_temp_c_ = -273.15f;
        max_junction_temp_c_ = -273.15f;
        max_gradient_c_per_mm_ = 0.0f;

        for (auto& row : grid_) {
            row.fill(ambient_temp_c_);
        }

        for (size_t i = 0; i < configs_.size(); ++i) {
            const auto& cfg = configs_[i];
            const auto& st = states_[i];
            if (!st.is_valid) continue;

            max_board_temp_c_ = std::max(max_board_temp_c_, st.measured_temp_c);
            max_junction_temp_c_ = std::max(max_junction_temp_c_, st.junction_temp_c);

            if (st.junction_temp_c >= cfg.critical_temp_c) {
                alert_flags_ = alert_flags_ | ThermalAlert::HotspotWarn;
            }
            if (st.rate_of_rise_cps >= 5.0f) {
                alert_flags_ = alert_flags_ | ThermalAlert::RunawayWarn;
            }

            const int col = static_cast<int>(cfg.pos.x_mm / grid_pitch_x_mm_);
            const int row = static_cast<int>(cfg.pos.y_mm / grid_pitch_y_mm_);
            if (row >= 0 && row < static_cast<int>(Rows) && col >= 0 && col < static_cast<int>(Cols)) {
                grid_[row][col] = st.measured_temp_c;
            }
        }

        for (size_t r = 0; r < Rows; ++r) {
            for (size_t c = 0; c < Cols; ++c) {
                float dt_dx = 0.0f;
                float dt_dy = 0.0f;

                if (c > 0 && c < Cols - 1) {
                    dt_dx = (grid_[r][c + 1] - grid_[r][c - 1]) / (2.0f * grid_pitch_x_mm_);
                } else if (c == 0 && Cols > 1) {
                    dt_dx = (grid_[r][1] - grid_[r][0]) / grid_pitch_x_mm_;
                }

                if (r > 0 && r < Rows - 1) {
                    dt_dy = (grid_[r + 1][c] - grid_[r - 1][c]) / (2.0f * grid_pitch_y_mm_);
                } else if (r == 0 && Rows > 1) {
                    dt_dy = (grid_[1][c] - grid_[0][c]) / grid_pitch_y_mm_;
                }

                const float grad_mag = std::sqrt(dt_dx * dt_dx + dt_dy * dt_dy);
                max_gradient_c_per_mm_ = std::max(max_gradient_c_per_mm_, grad_mag);
            }
        }

        if (max_gradient_c_per_mm_ >= 1.5f) {
            alert_flags_ = alert_flags_ | ThermalAlert::GradientWarn;
        }

        sample_count_++;
    }

    void print_telemetry() const {
        std::cout << "\n=== [C++20] ТЕЛЕМЕТРІЯ ТЕПЛОВОГО ПОЛЯ PCB [# " << sample_count_ << "] ===\n"
                  << std::fixed << std::setprecision(1)
                  << "Фон T_amb: " << ambient_temp_c_ << " °C | "
                  << "Макс T_board: " << max_board_temp_c_ << " °C | "
                  << "Макс T_Junction: " << max_junction_temp_c_ << " °C\n"
                  << "Макс просторовий градієнт: " << std::setprecision(2)
                  << max_gradient_c_per_mm_ << " °C/мм (" << max_gradient_c_per_mm_ * 10.0f << " °C/см)\n"
                  << "Тривожні прапорці: " << static_cast<uint32_t>(alert_flags_) << "\n"
                  << "--------------------------------------------------------------------------------\n"
                  << "ID | Назва вузла         | T_вимір  | T_Junction | dT/dt    | Потужність\n"
                  << "---+---------------------+----------+------------+----------+-----------\n";

        for (size_t i = 0; i < configs_.size(); ++i) {
            const auto& cfg = configs_[i];
            const auto& st = states_[i];

            std::cout << std::setw(2) << std::setfill('0') << static_cast<int>(cfg.id) << " | "
                      << std::setfill(' ') << std::left << std::setw(19) << cfg.name << " | "
                      << std::right << std::fixed << std::setprecision(1)
                      << std::setw(6) << st.measured_temp_c << " °C | "
                      << std::setw(7) << st.junction_temp_c << " °C  | "
                      << std::showpos << std::setw(5) << st.rate_of_rise_cps << " °C/s | "
                      << std::noshowpos << std::setw(4) << cfg.power_dissipation_w << " Вт "
                      << ((st.junction_temp_c >= cfg.critical_temp_c) ? "(!)" : "   ") << "\n";
        }
        std::cout << "--------------------------------------------------------------------------------\n";
    }

private:
    float ambient_temp_c_{25.0f};
    float reflected_temp_c_{25.0f};
    float grid_pitch_x_mm_{10.0f};
    float grid_pitch_y_mm_{10.0f};
    float max_board_temp_c_{25.0f};
    float max_junction_temp_c_{25.0f};
    float max_gradient_c_per_mm_{0.0f};
    ThermalAlert alert_flags_{ThermalAlert::None};
    uint32_t sample_count_{0};

    std::vector<ChannelConfig> configs_;
    std::vector<ChannelState> states_;
    std::array<std::array<float, Cols>, Rows> grid_{};
};

} // namespace pcb_thermal
