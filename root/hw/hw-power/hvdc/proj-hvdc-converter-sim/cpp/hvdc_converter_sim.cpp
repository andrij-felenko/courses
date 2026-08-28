// hvdc_converter_sim.cpp - Моделювання контуру керування HVDC мостом (C++20)
#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <expected>
#include <string_view>

namespace hvdc {

struct Config {
    double u_ll_rms{400'000.0};    // Лінійна напруга AC (В)
    double x_c{15.0};              // Комутаційний опір (Ом)
    double r_line{100.0};          // Опір DC лінії (Ом)
    double i_ref{2000.0};          // Уставка струму (А)
    double kp{0.005};              // ПІ-пропорційний коефіцієнт
    double ki{0.05};               // ПІ-інтегральний коефіцієнт
    double alpha_min_deg{5.0};     // Мінімальний кут alpha
    double alpha_max_deg{150.0};   // Максимальний кут alpha
    double gamma_min_deg{15.0};    // Поріг аварії gamma
};

enum class ControlError {
    CommutationFailure,
    Overcurrent,
    VoltageCollapse
};

constexpr std::string_view to_string(ControlError err) noexcept {
    switch (err) {
        case ControlError::CommutationFailure: return "Аварія: збій комутації інвертора";
        case ControlError::Overcurrent:        return "Аварія: струмове перевантаження";
        case ControlError::VoltageCollapse:    return "Аварія: посадка напруги AC";
    }
    return "Невідома помилка";
}

class ConverterStation {
public:
    explicit ConverterStation(Config config, double initial_alpha_deg = 30.0)
        : config_{config}, alpha_deg_{initial_alpha_deg} {}

    struct Status {
        double alpha_deg;
        double u_dc_kv;
        double i_dc_a;
        double mu_deg;
        double gamma_deg;
    };

    // Оновлення стану підстанції на один крок dt (сек)
    [[nodiscard]] std::expected<Status, ControlError> step(double dt) noexcept {
        const double err = config_.i_ref - i_dc_;
        integrator_ += err * dt;

        double alpha_calc = alpha_deg_ - (config_.kp * err + config_.ki * integrator_);
        if (alpha_calc < config_.alpha_min_deg) {
            alpha_calc = config_.alpha_min_deg;
            integrator_ -= err * dt;
        } else if (alpha_calc > config_.alpha_max_deg) {
            alpha_calc = config_.alpha_max_deg;
            integrator_ -= err * dt;
        }
        alpha_deg_ = alpha_calc;

        const double alpha_rad = alpha_deg_ * (std::numbers::pi / 180.0);
        const double u_dc0 = (3.0 * std::numbers::sqrt2 / std::numbers::pi) * config_.u_ll_rms * std::cos(alpha_rad);
        const double r_eq = (3.0 / std::numbers::pi) * config_.x_c;

        i_dc_ = std::max(0.0, u_dc0 / (config_.r_line + r_eq));
        u_dc_ = u_dc0 - r_eq * i_dc_;

        const double mu_rad = calculate_commutation_overlap(alpha_rad);
        mu_deg_ = mu_rad * (180.0 / std::numbers::pi);
        gamma_deg_ = 180.0 - (alpha_deg_ + mu_deg_);

        if (alpha_deg_ > 90.0 && gamma_deg_ < config_.gamma_min_deg) {
            return std::unexpected(ControlError::CommutationFailure);
        }

        return Status{
            .alpha_deg = alpha_deg_,
            .u_dc_kv = u_dc_ / 1000.0,
            .i_dc_a = i_dc_,
            .mu_deg = mu_deg_,
            .gamma_deg = gamma_deg_
        };
    }

private:
    [[nodiscard]] double calculate_commutation_overlap(double alpha_rad) const noexcept {
        const double cos_alpha = std::cos(alpha_rad);
        const double drop = (2.0 * config_.x_c * i_dc_) / (std::numbers::sqrt2 * config_.u_ll_rms);
        double cos_alpha_mu = std::clamp(cos_alpha - drop, -1.0, 1.0);
        return std::max(0.0, std::acos(cos_alpha_mu) - alpha_rad);
    }

    Config config_;
    double alpha_deg_{30.0};
    double integrator_{0.0};
    double u_dc_{0.0};
    double i_dc_{0.0};
    double mu_deg_{0.0};
    double gamma_deg_{0.0};
};

} // namespace hvdc

int main() {
    hvdc::Config config;
    hvdc::ConverterStation station(config, 30.0);

    std::cout << "=== Симуляція контуру керування HVDC (C++20) ===\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Крок |  Alpha (°) |    U_dc (кВ) |    I_dc (А) |   Mu (°) |  Gamma (°) | Стан\n";
    std::cout << "-----+------------+--------------+-------------+----------+------------+------\n";

    constexpr double dt = 0.01;
    for (int step = 1; step <= 10; ++step) {
        auto result = station.step(dt);
        if (result) {
            const auto& st = *result;
            std::cout << std::setw(4) << step << " | "
                      << std::setw(10) << st.alpha_deg << " | "
                      << std::setw(12) << st.u_dc_kv << " | "
                      << std::setw(11) << st.i_dc_a << " | "
                      << std::setw(8) << st.mu_deg << " | "
                      << std::setw(10) << st.gamma_deg << " | ОК\n";
        } else {
            std::cout << std::setw(4) << step << " | "
                      << "  ПОМИЛКА: " << hvdc::to_string(result.error()) << '\n';
        }
    }

    return 0;
}
