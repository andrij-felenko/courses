#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>
#include <stdexcept>

struct MtjParams {
    double r_p{1000.0};      // Опір у паралельному стані (Ом)
    double tmr0{2.0};        // TMR0 (2.0 = 200%)
    double v_half{0.5};      // V_1/2 (Вольт)
    double area_um2{0.01};   // Площа (мкм²)
    double t_fl_nm{1.4};     // Товщина вільного шару (нм)

    [[nodiscard]] constexpr double r_ap_zero() const noexcept {
        return r_p * (1.0 + tmr0);
    }
};

class MtjSimulator {
public:
    explicit MtjSimulator(MtjParams params) : params_(params) {
        if (params_.r_p <= 0.0 || params_.v_half <= 0.0) {
            throw std::invalid_argument("Некоректні фізичні параметри MTJ!");
        }
    }

    // Обчислення кутової залежності опору R(theta)
    [[nodiscard]] double resistance_at_angle(double theta_rad) const noexcept {
        const double r_ap = params_.r_ap_zero();
        const double cos_t = std::cos(theta_rad);
        const double num = 2.0 * params_.r_p * r_ap;
        const double den = (r_ap + params_.r_p) + (r_ap - params_.r_p) * cos_t;
        return num / den;
    }

    // Обчислення TMR при напрузі V
    [[nodiscard]] double tmr_at_bias(double v_bias) const noexcept {
        const double ratio = v_bias / params_.v_half;
        return params_.tmr0 / (1.0 + ratio * ratio);
    }

    // Обчислення струму в AP стані при V (Ампер)
    [[nodiscard]] double current_ap(double v_bias) const noexcept {
        if (std::abs(v_bias) < 1e-12) return 0.0;
        const double tmr_v = tmr_at_bias(v_bias);
        const double r_ap_v = params_.r_p * (1.0 + tmr_v);
        return v_bias / r_ap_v;
    }

    // Обчислення струму в P стані при V (Ампер)
    [[nodiscard]] double current_p(double v_bias) const noexcept {
        return v_bias / params_.r_p;
    }

    // Розрахунок критичного струму STT-перемикання (мкА)
    [[nodiscard]] double critical_stt_current() const noexcept {
        constexpr double alpha = 0.01;            // Загасання Гілберта
        constexpr double ms = 1000.0;             // Намагніченість насичення (ЕМУ/см³)
        constexpr double hk_oe = 2000.0;          // Ефективне поле анізотропії (Ерстед)
        constexpr double eta = 0.6;               // Спінова поляризація струму
        constexpr double e_charge = 1.602e-19;    // Заряд електрона (Кл)
        constexpr double hbar = 1.054e-34;        // Зведена константа Планка

        const double vol_cm3 = params_.area_um2 * 1e-8 * (params_.t_fl_nm * 1e-7);
        const double ic0_amp = (2.0 * e_charge * alpha * ms * vol_cm3 * hk_oe) / (hbar * eta);
        return ic0_amp * 1e6;
    }

private:
    MtjParams params_;
};

int main() {
    try {
        const MtjParams params{
            .r_p = 1000.0,
            .tmr0 = 2.0,
            .v_half = 0.5,
            .area_um2 = 0.01,
            .t_fl_nm = 1.4
        };
        const MtjSimulator sim(params);

        std::cout << "=============================================================\n";
        std::cout << "     СИМУЛЯТОР ЕЛЕКТРОФІЗИЧНИХ ХАРАКТЕРИСТИК MTJ (C++)\n";
        std::cout << "=============================================================\n\n";

        std::cout << "=== МОДЕЛЮВАННЯ КУТОВОЇ ЗАЛЕЖНОСТІ R(theta) ===\n";
        std::cout << std::setw(10) << "Кут (град)" << " | "
                  << std::setw(12) << "Опір R (Ом)" << " | "
                  << std::setw(18) << "Провідність (мСм)\n";
        std::cout << "---------------------------------------------\n";

        for (int deg = 0; deg <= 180; deg += 30) {
            const double rad = static_cast<double>(deg) * std::numbers::pi / 180.0;
            const double r_val = sim.resistance_at_angle(rad);
            const double g_mS = (1.0 / r_val) * 1000.0;
            std::cout << std::setw(10) << deg << " | "
                      << std::setw(12) << std::fixed << std::setprecision(1) << r_val << " | "
                      << std::setw(18) << std::setprecision(4) << g_mS << "\n";
        }

        std::cout << "\n=== МОДЕЛЮВАННЯ ВОЛЬТ-АМПЕРНОЇ ХАРАКТЕРИСТИКИ I(V) ===\n";
        std::cout << std::setw(12) << "Напруга (В)" << " | "
                  << std::setw(10) << "TMR(V) (%)" << " | "
                  << std::setw(10) << "I_P (мкА)" << " | "
                  << std::setw(10) << "I_AP (мкА)" << " | "
                  << std::setw(10) << "ΔI (мкА)\n";
        std::cout << "-------------------------------------------------------------\n";

        for (int step = 0; step <= 10; ++step) {
            const double v = static_cast<double>(step) * 0.1;
            const double tmr_pct = sim.tmr_at_bias(v) * 100.0;
            const double i_p_ua = sim.current_p(v) * 1e6;
            const double i_ap_ua = sim.current_ap(v) * 1e6;
            const double delta_i = i_p_ua - i_ap_ua;

            std::cout << std::setw(12) << std::setprecision(2) << v << " | "
                      << std::setw(10) << std::setprecision(1) << tmr_pct << " | "
                      << std::setw(10) << std::setprecision(2) << i_p_ua << " | "
                      << std::setw(10) << std::setprecision(2) << i_ap_ua << " | "
                      << std::setw(10) << std::setprecision(2) << delta_i << "\n";
        }

        const double ic0_ua = sim.critical_stt_current();
        std::cout << "\n--- ОЦІНКА ПАРАМЕТРІВ STT-ПЕРЕМИКАННЯ ---\n";
        std::cout << "Критичний струм перемикання I_c0 (T=0K): " << std::fixed << std::setprecision(2) << ic0_ua << " мкА\n";
        std::cout << "Порогова густина струму J_c0:            " << (ic0_ua * 1e-6) / (params.area_um2 * 1e-8) / 1e6 << " MA/см²\n";

    } catch (const std::exception& e) {
        std::cerr << "Помилка під час симуляції: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
