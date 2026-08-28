#include <cmath>
#include <print>

// Множник зростання за `years` років при подвоєнні кожні `T` років.
// Серце закону Мура: 2^(t/T). Усе інше — похідні цього рядка.
double moore_factor(double years, double T) {
    return std::pow(2.0, years / T);     // 2 у степені (минуло періодів)
}

// Річний приріст (CAGR) для періоду подвоєння T років: 2^(1/T) − 1.
double moore_cagr(double T) {
    return std::pow(2.0, 1.0 / T) - 1.0; // T=2 → √2 − 1 ≈ 0.4142
}

// Миттєвий (неперервний) темп r для періоду T: ln2 / T.
double moore_rate(double T) {
    return std::log(2.0) / T;            // T=2 → 0.693/2 ≈ 0.347
}

int main() {
    double T = 2.0;                      // подвоєння щодва роки

    // Три імені одного темпу — переконуємося, що крива одна:
    std::println("CAGR = {:.4f} ({:.1f}% на рік)", moore_cagr(T), 100 * moore_cagr(T));
    std::println("r    = {:.4f} ({:.1f}% миттєво)", moore_rate(T), 100 * moore_rate(T));
    std::println("звірка 1+CAGR проти e^r: {:.4f} vs {:.4f}",
                 1.0 + moore_cagr(T), std::exp(moore_rate(T)));   // мають збігтися

    // Екстраполяція крізь півстоліття від першого мікропроцесора.
    // 1971: Intel 4004 — 2300 транзисторів.
    double base   = 2300.0;
    double factor = moore_factor(50.0, T);             // 2^(50/2) = 2^25 ≈ 33.5 млн
    std::println("прогноз на 2021: {:.3g} транзисторів", base * factor);  // ≈ 7.7e10
}
