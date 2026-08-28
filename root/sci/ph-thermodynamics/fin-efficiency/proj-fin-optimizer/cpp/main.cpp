#include <iostream>
#include <cmath>
#include <vector>
#include <optional>
#include <iomanip>
#include <algorithm>

namespace ThermalEngine {

// Конфігураційні параметри геометрії та теплообміну
struct HeatsinkConfig {
    double w_base{0.080};   // Ширина основи, м
    double l_base{0.060};   // Довжина основи вздовж потоку, м
    double h_fin{0.035};    // Висота ребер, м
    double k_metal{200.0};  // Теплопровідність металу, Вт/(м·К)
    double h_conv{45.0};    // Коефіцієнт тепловіддачі, Вт/(м²·К)
    double t_amb{25.0};     // Температура повітря, °C
    double p_heat{65.0};    // Розсіювана потужність, Вт
    double s_min{0.0015};   // Мінімальний аеродинамічний зазор, м
};

// Результат оцінки теплофізичних характеристик радіатора
struct HeatsinkResult {
    int num_fins{0};
    double fin_thick{0.0};
    double gap{0.0};
    double m_param{0.0};
    double eta_f{0.0};
    double eta_o{0.0};
    double r_th{0.0};
    double t_base{0.0};
    double total_area{0.0};
};

class HeatsinkOptimizer {
public:
    explicit HeatsinkOptimizer(HeatsinkConfig config) : cfg_(std::move(config)) {}

    // Обчислення параметрів конкретної конфігурації (N, t)
    [[nodiscard]] std::optional<HeatsinkResult> evaluate(int num_fins, double fin_thick) const {
        if (num_fins < 2 || fin_thick <= 0.0) return std::nullopt;

        const double total_fin_thick = num_fins * fin_thick;
        if (total_fin_thick >= cfg_.w_base) return std::nullopt;

        const double gap = (cfg_.w_base - total_fin_thick) / (num_fins - 1);
        if (gap < cfg_.s_min) return std::nullopt; // Обмеження на примежовий шар

        const double a_c = cfg_.l_base * fin_thick;
        const double p_perim = 2.0 * (cfg_.l_base + fin_thick);
        const double h_c = cfg_.h_fin + (fin_thick / 2.0); // Скоригована висота

        const double a_f_single = 2.0 * cfg_.l_base * h_c;
        const double a_f_total = num_fins * a_f_single;
        const double a_u = (num_fins - 1) * gap * cfg_.l_base;
        const double a_total = a_u + a_f_total;

        const double m_param = std::sqrt((cfg_.h_conv * p_perim) / (cfg_.k_metal * a_c));
        const double m_hc = m_param * h_c;
        const double eta_f = std::tanh(m_hc) / m_hc;

        const double eta_o = 1.0 - (a_f_total / a_total) * (1.0 - eta_f);
        const double r_th = 1.0 / (eta_o * cfg_.h_conv * a_total);
        const double t_base = cfg_.t_amb + cfg_.p_heat * r_th;

        return HeatsinkResult{
            num_fins, fin_thick, gap, m_param, eta_f, eta_o, r_th, t_base, a_total
        };
    }

    // Пошук оптимальної геометрії двовимірним скануванням
    [[nodiscard]] std::optional<HeatsinkResult> optimize() const {
        std::optional<HeatsinkResult> best_res;
        double min_r_th = 1e9;

        for (double t = 0.0005; t <= 0.0040; t += 0.0001) {
            for (int n = 3; n <= 60; ++n) {
                if (auto res = evaluate(n, t); res.has_value()) {
                    if (res->r_th < min_r_th) {
                        min_r_th = res->r_th;
                        best_res = res;
                    }
                }
            }
        }
        return best_res;
    }

private:
    HeatsinkConfig cfg_;
};

} // namespace ThermalEngine

int main() {
    using namespace ThermalEngine;

    HeatsinkConfig config;
    HeatsinkOptimizer optimizer(config);

    std::cout << "=== ОПТИМІЗАЦІЯ ГЕОМЕТРІЇ АЛЮМІНІЄВОГО РАДІАТОРА (C++17) ===\n\n";

    if (auto opt = optimizer.optimize(); opt.has_value()) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Знайдено оптимальну геометрію радіатора:\n"
                  << "  • Кількість ребер N    : " << opt->num_fins << " шт.\n"
                  << "  • Товщина ребра t     : " << opt->fin_thick * 1000.0 << " мм\n"
                  << "  • Зазор між ребрами S  : " << opt->gap * 1000.0 << " мм\n"
                  << "  • Повна площа поверхні  : " << std::setprecision(4) << opt->total_area << " м²\n"
                  << "  • Параметр згасання m  : " << std::setprecision(2) << opt->m_param << " 1/м\n"
                  << "  • Ефективність ребра η_f: " << opt->eta_f * 100.0 << "%\n"
                  << "  • Ефективність масиву η_o: " << opt->eta_o * 100.0 << "%\n"
                  << "  • Тепловий опір R_th   : " << std::setprecision(3) << opt->r_th << " °C/Вт\n"
                  << "  • Температура основи T : " << std::setprecision(1) << opt->t_base << " °C\n";
    } else {
        std::cout << "Помилка: Не вдалося знайти допустиму геометрію.\n";
    }

    return 0;
}
