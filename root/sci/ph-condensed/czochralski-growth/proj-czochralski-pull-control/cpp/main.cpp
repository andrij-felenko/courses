#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <optional>

// Параметри теплового режиму печі та кристала
struct ProcessParams {
    double target_radius_m{0.150};    // Цільовий радіус зливка (150 мм = Ø 300 мм)
    double target_pull_rate_mps{2.0e-5}; // Базова швидкість витягування (1.2 мм/хв)
    double melt_temp_k{1690.0};       // Базова температура розплаву
    double latent_heat_j_kg{1.8e6};   // Прихована теплота плавлення Si
    double density_solid_kg_m3{2330.0}; // Густина твердого Si
    double thermal_cond_solid{22.0};  // Теплопровідність твердого Si (Вт/м·К)
};

// Стан контуру регулювання (ПІД)
class CzochralskiController {
public:
    explicit CzochralskiController(ProcessParams params)
        : params_(params), integral_err_(0.0), prev_err_(0.0) {}

    struct ControlOutput {
        double pull_rate_mps; // Скоригована швидкість витягування (м/с)
        double heater_power_kw; // Скоригована потужність нагрівача (кВт)
    };

    // Оновлення стану контролера за один крок часу dt
    [[nodiscard]] ControlOutput update(double measured_radius_m, double dt_sec) {
        const double error = params_.target_radius_m - measured_radius_m;
        integral_err_ += error * dt_sec;
        const double derivative_err = (error - prev_err_) / dt_sec;
        prev_err_ = error;

        // ПІД-коефіцієнти для швидкості витягування
        constexpr double Kp_v = 3.0e-4;
        constexpr double Ki_v = 1.0e-5;
        constexpr double Kd_v = 5.0e-5;

        // Відхилення від цільового радіуса коригує швидкість у протилежному напрямку:
        // якщо R занадто великий (error < 0), збільшуємо швидкість витягування.
        const double delta_v = -(Kp_v * error + Ki_v * integral_err_ + Kd_v * derivative_err);
        
        // Обмеження допустимої швидкості витягування (безпечний діапазон 0.2 .. 4.0 мм/хв)
        constexpr double min_pull = 0.33e-5; // ~0.2 мм/хв
        constexpr double max_pull = 6.67e-5; // ~4.0 мм/хв
        const double pull_rate = std::clamp(params_.target_pull_rate_mps + delta_v, min_pull, max_pull);

        // Розрахунок теплового балансу для визначення потрібної потужності
        // Q_solid = k_S * dT/dz = Q_melt + L_m * rho_S * v_p
        const double area = M_PI * measured_radius_m * measured_radius_m;
        const double latent_power_w = params_.latent_heat_j_kg * params_.density_solid_kg_m3 * area * pull_rate;
        const double base_heater_kw = 85.0; // 85 кВт базова потужність
        
        // Коригування потужності нагрівача: якщо кристал тоншає (error > 0), зменшуємо нагрів
        constexpr double Kp_p = 120.0;
        const double heater_kw = std::clamp(base_heater_kw - Kp_p * error, 50.0, 150.0);

        return ControlOutput{pull_rate, heater_kw};
    }

private:
    ProcessParams params_;
    double integral_err_;
    double prev_err_;
};

int main() {
    ProcessParams params{};
    CzochralskiController controller(params);

    std::cout << "--- Симуляція ПІД-контролера печі Чохральського ---\n";
    std::cout << "Час (хв) | Виміряний Ø (мм) | Швидкість v_p (мм/хв) | Потужність P (кВт)\n";

    double radius = 0.142; // Початковий радіус (142 мм замість 150 мм — зливок тонший)
    constexpr double dt = 5.0; // Крок симуляції 5 секунд

    for (int step = 0; step <= 24; ++step) {
        const double time_min = step * (dt / 60.0);
        const auto [v_p, p_kw] = controller.update(radius, dt);

        std::cout << time_min << " хв | "
                  << (radius * 2000.0) << " мм | "
                  << (v_p * 60000.0) << " мм/хв | "
                  << p_kw << " кВт\n";

        // Проста фізична модель динаміки радіуса під впливом v_p
        const double v_target = params.target_pull_rate_mps;
        radius += (v_target - v_p) * 0.05 * dt; // Зміна радіуса
    }
    return 0;
}
