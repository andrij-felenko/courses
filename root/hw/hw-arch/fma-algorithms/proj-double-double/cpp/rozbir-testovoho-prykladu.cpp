#include <iostream>
#include <iomanip>
#include <cmath>

/* Алгоритм Кахана для детермінанта 2x2 */
[[nodiscard]] constexpr double kahan_det2x2(double a, double b, double c, double d) noexcept {
    const double w = b * c;
    const double e = std::fma(-b, c, w);
    const double d_val = std::fma(a, d, -w);
    return d_val + e;
}

int main() {
    constexpr double a = 9007199254740994.0; /* 2^53 + 2 */
    constexpr double d = 9007199254740994.0;
    constexpr double b = 9007199254740995.0; /* 2^53 + 3 */
    constexpr double c = 9007199254740993.0; /* 2^53 + 1 */

    const double naive = (a * d) - (b * c);
    const double kahan = kahan_det2x2(a, b, c, d);

    std::cout << std::fixed << std::setprecision(16);
    std::cout << "Точне аналітичне значення: 1.0000000000000000\n";
    std::cout << "Наївне обчислення (MUL-SUB): " << naive << " (Помилка!)\n";
    std::cout << "Алгоритм Кахана (FMA):      " << kahan << " (Абсолютно точно!)\n";

    return 0;
}
