#include <cstdio>
#include <optional>
#include <initializer_list>

struct Switch {
    const char* name;
    double v0;      // В   — поріг ВАХ; у польового ключа його немає
    double r;       // Ом  — нахил ВАХ (rce) або Rds(on) — обов'язково ГАРЯЧИЙ
    double e_ref;   // Дж  — Eon+Eoff у даташитній точці
    double v_ref;   // В   — напруга тієї точки
    double i_ref;   // А   — струм тієї точки
    double price;   // $

    // Провідні втрати: поріг бере струм, опір бере квадрат струму.
    constexpr double p_cond(double i, double duty) const {
        return duty * (v0 * i + r * i * i);
    }
    // Даташитна енергія, перерахована на наш режим: лінійно по V і по I.
    constexpr double e_sw(double v, double i) const {
        return e_ref * (v / v_ref) * (i / i_ref);
    }
    constexpr double p_total(double v, double i, double duty, double fsw) const {
        return p_cond(i, duty) + e_sw(v, i) * fsw;
    }
};

constexpr Switch SIC { "SiC C2M0080120D @150 °C", 0.0, 0.144, 684e-6, 800.0, 20.0, 25.0 };
constexpr Switch IGBT{ "Si IKW40N120H3 @175 °C",  0.8, 0.0375, 7.0e-3, 600.0, 40.0, 8.0 };

// nullopt — «перетину не існує»; 0.0 — «виграє на будь-якій частоті»
std::optional<double> f_crossover(const Switch& mos, const Switch& igbt,
                                  double v, double i, double duty) {
    const double cond_gap = mos.p_cond(i, duty) - igbt.p_cond(i, duty);
    const double sw_gain  = igbt.e_sw(v, i) - mos.e_sw(v, i);
    if (sw_gain <= 0.0) return std::nullopt;   // відігравати нічим
    if (cond_gap <= 0.0) return 0.0;
    return cond_gap / sw_gain;
}

std::optional<double> breakeven_current(const Switch& mos, const Switch& igbt) {
    const double dr = mos.r - igbt.r;
    if (dr <= 0.0) return std::nullopt;
    return igbt.v0 / dr;
}

int main() {
    constexpr double V_DC = 800.0, I_SW = 20.0, DUTY = 0.5;

    std::printf("струм-беззбитковість : %.1f А\n", *breakeven_current(SIC, IGBT));
    std::printf("частота-перетин @%.0f А: %.2f кГц\n\n",
                I_SW, *f_crossover(SIC, IGBT, V_DC, I_SW, DUTY) / 1e3);

    std::printf("f, кГц    SiC, Вт   IGBT, Вт    виграш\n");
    for (double f_khz : {2.0, 5.0, 10.0, 20.0, 50.0}) {
        const double ps = SIC.p_total(V_DC, I_SW, DUTY, f_khz * 1e3);
        const double pi = IGBT.p_total(V_DC, I_SW, DUTY, f_khz * 1e3);
        std::printf("%6.0f   %8.1f   %8.1f   %+7.1f\n", f_khz, ps, pi, pi - ps);
    }
}
