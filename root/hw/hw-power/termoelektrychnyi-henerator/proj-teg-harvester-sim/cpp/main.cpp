#include <cmath>
#include <array>
#include <optional>
#include <concepts>
#include <algorithm>

// Модель фізичних констант ТЕГ
struct TegModule {
    int pairs_count = 127;
    double seebeck_pair = 400e-6; // 400 мкВ/К
    double r_internal = 2.4;      // 2.4 Ом
    double theta_teg = 1.8;       // К/Вт
    double theta_hot = 0.3;       // К/Вт
    double theta_sink = 2.5;      // К/Вт

    [[nodiscard]] constexpr double total_thermal_resistance() const noexcept {
        return theta_hot + theta_teg + theta_sink;
    }

    [[nodiscard]] double open_circuit_voltage(double t_src, double t_amb) const noexcept {
        const double dt_sys = t_src - t_amb;
        if (dt_sys <= 0.0) return 0.0;
        const double dt_teg = dt_sys * (theta_teg / total_thermal_resistance());
        return (pairs_count * seebeck_pair) * dt_teg;
    }

    [[nodiscard]] double mpp_power(double voc) const noexcept {
        if (voc <= 0.0) return 0.0;
        return (voc * voc) / (4.0 * r_internal);
    }
};

// Стан мікропотужного автономного вузла
class EnergyHarvester {
public:
    struct Config {
        double capacitance = 0.47;      // Фарад
        double v_high = 3.3;            // Поріг передачі
        double v_low = 2.2;             // Поріг UVLO
        double i_leakage = 2.0e-6;      // А
        double i_sleep = 1.8e-6;        // А
        double i_active = 22.0e-3;      // А
        double t_active = 0.025;        // с
        double eta_boost = 0.78;        // ККД 78%
        double v_cold_start = 0.040;    // 40 мВ
    };

    struct StepReport {
        double time_s;
        double t_src;
        double v_teg_oc;
        double p_harvested_mw;
        double v_cap;
        bool transmission_occurred;
    };

    explicit EnergyHarvester(Config cfg, double initial_vcap = 2.0) noexcept
        : cfg_(cfg), v_cap_(initial_vcap) {}

    StepReport step(const TegModule& teg, double t_src, double t_amb, 
                    double dt, double current_time) noexcept {
        const double voc = teg.open_circuit_voltage(t_src, t_amb);
        double p_harvested = 0.0;

        if (voc >= cfg_.v_cold_start) {
            p_harvested = teg.mpp_power(voc) * cfg_.eta_boost;
        }

        // Баланс енергії в іоністорі: E = 0.5 * C * V^2
        double e_cap = 0.5 * cfg_.capacitance * v_cap_ * v_cap_;
        e_cap += p_harvested * dt;

        const double p_static_loss = v_cap_ * (cfg_.i_sleep + cfg_.i_leakage);
        e_cap -= p_static_loss * dt;

        bool tx_done = false;
        if (v_cap_ >= cfg_.v_high) {
            const double e_tx = v_cap_ * cfg_.i_active * cfg_.t_active;
            if (e_cap >= e_tx) {
                e_cap -= e_tx;
                tx_done = true;
            }
        }

        e_cap = std::max(0.0, e_cap);
        v_cap_ = std::sqrt((2.0 * e_cap) / cfg_.capacitance);

        return StepReport{
            .time_s = current_time,
            .t_src = t_src,
            .v_teg_oc = voc,
            .p_harvested_mw = p_harvested * 1000.0,
            .v_cap = v_cap_,
            .transmission_occurred = tx_done
        };
    }

    [[nodiscard]] double voltage() const noexcept { return v_cap_; }

private:
    Config cfg_;
    double v_cap_;
};
