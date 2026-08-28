#include <iostream>
#include <string_view>
#include <vector>
#include <span>
#include <cmath>
#include <numbers>
#include <iomanip>

struct EsdCandidate {
    std::string_view name;
    std::string_view tech_type;
    double c_esd_pf;      // Паразитна ємність (пФ)
    double r_dyn_ohm;     // Динамічний опір (Ом)
    double v_cl_tlp_v;    // Напруга фіксації при TLP 16 А (В)
    double max_surge_a;   // Піковий струм 8/20 мкс (А)
};

struct EsdEvaluation {
    double f_cutoff_ghz;      // Частота зрізу -3 дБ (ГГц)
    double delta_tr_ps;       // Завал фронту (пс)
    double s21_loss_db;       // Внесені втрати S21 на f_Nyquist (дБ)
    bool is_signal_clean;     // Чи вкладається у критерій S21 > -0.5 дБ
    bool is_protection_safe;  // Чи безпечна V_cl для приймача (< V_max)
};

class SignalIntegrityAnalyzer {
public:
    constexpr SignalIntegrityAnalyzer(double data_rate_gbps, double z0_ohm, double v_max_phy_v) noexcept
        : data_rate_gbps_{data_rate_gbps}, z0_ohm_{z0_ohm}, v_max_phy_v_{v_max_phy_v} {}

    [[nodiscard]] EsdEvaluation evaluate(const EsdCandidate& cand) const noexcept {
        const double c_farad = cand.c_esd_pf * 1e-12;
        const double r_eff = z0_ohm_ / 2.0;
        const double f_nyquist_hz = (data_rate_gbps_ * 1e9) / 2.0;

        // 1. Гранична частота зрізу -3 дБ
        const double f_c_hz = 1.0 / (2.0 * std::numbers::pi * r_eff * c_farad);

        // 2. Деградація часу наростання фронту
        const double tr_sec = 2.2 * r_eff * c_farad;

        // 3. Внесені втрати S21 на частоті Найквіста
        const double omega = 2.0 * std::numbers::pi * f_nyquist_hz;
        const double denom = std::sqrt(4.0 + std::pow(omega * z0_ohm_ * c_farad, 2.0));
        const double s21_mag = 2.0 / denom;
        const double s21_loss_db = 20.0 * std::log10(s21_mag);

        return EsdEvaluation{
            .f_cutoff_ghz = f_c_hz / 1e9,
            .delta_tr_ps = tr_sec * 1e12,
            .s21_loss_db = s21_loss_db,
            .is_signal_clean = (s21_loss_db >= -0.5),
            .is_protection_safe = (cand.v_cl_tlp_v <= v_max_phy_v_)
        };
    }

    [[nodiscard]] constexpr double data_rate() const noexcept { return data_rate_gbps_; }
    [[nodiscard]] constexpr double nyquist_freq() const noexcept { return data_rate_gbps_ / 2.0; }
    [[nodiscard]] constexpr double impedance() const noexcept { return z0_ohm_; }
    [[nodiscard]] constexpr double max_voltage() const noexcept { return v_max_phy_v_; }

private:
    double data_rate_gbps_;
    double z0_ohm_;
    double v_max_phy_v_;
};

int main()
{
    const SignalIntegrityAnalyzer analyzer(20.0, 50.0, 6.0);

    const std::vector<EsdCandidate> candidates = {
        {"Силовий TVS (SMAJ5.0A)", "Кремній (Single PN)", 450.0, 0.08, 9.2, 40.0},
        {"Стандартний ESD-TVS",    "Кремній (ESD-Array)",   3.5, 0.45, 8.5, 12.0},
        {"Низькоємнісний TVS",     "Діодний міст + Zener", 0.35, 0.30, 5.8,  5.0},
        {"Ультра-ESD TVS",         "Snapback SCR Deep-Sub", 0.12, 0.18, 4.8,  3.5},
        {"Полімерний PVVM",        "Polymer Matrix",       0.08, 1.80, 32.0, 0.5}
    };

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Аналіз ESD-захисту для лінії " << analyzer.data_rate()
              << " Гбіт/с (f_Nyquist = " << analyzer.nyquist_freq()
              << " ГГц, Z0 = " << analyzer.impedance() << " Ом) ===\n";
    std::cout << "Гранична напруга приймача V_max = " << analyzer.max_voltage()
              << " В, критерій втрат S21 >= -0.5 дБ\n\n";

    for (const auto& c : candidates) {
        const auto eval = analyzer.evaluate(c);

        std::cout << "Компонент: " << c.name << " [" << c.tech_type << "]\n";
        std::cout << "  Параметри: C = " << c.c_esd_pf << " пФ, R_dyn = " << c.r_dyn_ohm
                  << " Ом, V_CL(@16A) = " << c.v_cl_tlp_v << " В\n";
        std::cout << "  Вплив на лінію: f_cutoff = " << eval.f_cutoff_ghz
                  << " ГГц, Δtr = " << eval.delta_tr_ps
                  << " пс, S21(10ГГц) = " << eval.s21_loss_db << " дБ\n";
        std::cout << "  Вердикт: "
                  << (eval.is_signal_clean ? "✓ СИГНАЛ ЧИСТИЙ" : "✗ СИГНАЛ ЗІПСОВАНО (велика ємність)")
                  << " | "
                  << (eval.is_protection_safe ? "✓ ЗАХИСТ НАДІЙНИЙ" : "✗ ЗАХИСТ НЕБЕЗПЕЧНИЙ (висока V_CL)")
                  << "\n\n";
    }

    return 0;
}
