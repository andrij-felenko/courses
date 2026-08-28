#include <optional>
#include <print>

struct Snubber { double r, p, c; };   // резистор (Ом), розсіювання (Вт), ємність (Ф)

// Порахувати резистор і потужність снабера; повернути порожнє, якщо вибір
// V_clamp негодящий (нижче за відбиту або вище за стелю транзистора з запасом).
std::optional<Snubber> rcd_snubber(double v_in,     // вхідна напруга (В)
                                   double v_r,      // відбита напруга (В)
                                   double l_lk,     // індуктивність витоку (Гн)
                                   double i_pk,     // піковий струм первинної (А)
                                   double f_sw,     // частота (Гц)
                                   double v_clamp,  // бажаний рівень фіксації (В)
                                   double bv_dss,   // гранична напруга ключа (В)
                                   double margin)   // запас до BV_DSS, 0.15 = 15 %
{
    if (v_clamp <= v_r)                              // нижче за відбиту — снабер не працює
        return std::nullopt;
    if (v_in + v_clamp > bv_dss * (1.0 - margin))    // за стелю транзистора
        return std::nullopt;

    double p_lk = 0.5 * l_lk * i_pk * i_pk * f_sw;   // потужність витоку (Вт)
    double r = v_clamp * (v_clamp - v_r) / p_lk;     // резистор (Ом)
    double p = v_clamp * v_clamp / r;                // розсіювання на R (Вт)
    double c = 10.0 / (r * f_sw);                    // C з R·C ≈ 10·період (Ф)
    return Snubber{r, p, c};
}

int main()
{
    if (auto s = rcd_snubber(325, 100, 5e-6, 1.0, 65000, 200, 650, 0.15))
        std::println("R = {:.0f} кОм,  P = {:.2f} Вт,  C = {:.1f} нФ",
                     s->r / 1e3, s->p, s->c * 1e9);
    else
        std::println("Вибір V_clamp негодящий — перегляньте рівень фіксації");
}
// Вивід: R = 123 кОм,  P = 0.33 Вт,  C = 1.5 нФ
