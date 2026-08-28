#include <cstdint>
#include <optional>

// Субпіксельний зсув вершини параболи через три відліки fm, f0, fp.
// Повертає δ у пікселях (−0.5..+0.5 для коректного локального максимуму).
// nullopt, якщо точка не є максимумом (знаменник невід'ємний) — δ невизначений.
static std::optional<double> subpixel_offset(double fm, double f0, double fp) {
    double denom = fm - 2.0 * f0 + fp;        // ~друга похідна (має бути < 0)
    if (denom >= 0.0) return std::nullopt;    // не максимум — не уточнюємо
    double d = (fm - fp) / (2.0 * denom);     // δ = −f′/(2f″)
    if (d >  0.5) d =  0.5;                    // зсув > пів-пікселя — не сусідній гребінь
    if (d < -0.5) d = -0.5;
    return d;
}

// Приклад: уточнити позицію межі вздовж рядка в точці максимуму x0.
// Повертає координату субпіксельної межі по x.
static double refine_edge_x(const int *mag_row, int x0) {
    auto d = subpixel_offset(mag_row[x0 - 1], mag_row[x0], mag_row[x0 + 1]);
    return d ? x0 + *d : static_cast<double>(x0);
}
