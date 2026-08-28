#include <algorithm>
#include <cmath>
#include <complex>
#include <limits>
#include <vector>

// Затримка як нахил прямої, підігнаної МНК у вікні з m точок.
// PI — та сама стала, що й у першому оцінювачі.
// Точки, де |H| нижче floor_db від максимуму, не беруться: там фаза — шум.
// На краях (менше ніж m/2 сусідів) лишається NaN.
std::vector<double> group_delay_ls(const std::vector<double>& f,
                                  const std::vector<std::complex<double>>& H,
                                  std::size_t m = 11, double floor_db = -40.0)
{
    const std::size_t N = f.size();
    const double nan = std::numeric_limits<double>::quiet_NaN();
    std::vector<double> psi(N, 0.0), mag(N, 0.0), tau(N, nan);

    double peak = 0.0;
    for (std::size_t k = 0; k < N; ++k) peak = std::max(peak, std::abs(H[k]));
    for (std::size_t k = 0; k < N; ++k) mag[k] = 20.0 * std::log10(std::abs(H[k]) / peak);
    for (std::size_t k = 1; k < N; ++k)               // локально розгорнута фаза
        psi[k] = psi[k - 1] + std::arg(H[k] * std::conj(H[k - 1]));

    const std::size_t half = m / 2;
    for (std::size_t k = half; k + half < N; ++k) {
        double sw = 0.0, sp = 0.0;
        bool ok = true;
        for (std::size_t i = k - half; i <= k + half; ++i) {
            if (mag[i] < floor_db) ok = false;
            sw += 2.0 * PI * f[i];
            sp += psi[i];
        }
        if (!ok) continue;                            // у провалі АЧХ не рахуємо

        const double wbar = sw / m, pbar = sp / m;
        double num = 0.0, den = 0.0;
        for (std::size_t i = k - half; i <= k + half; ++i) {
            const double dw = 2.0 * PI * f[i] - wbar;
            num += dw * (psi[i] - pbar);
            den += dw * dw;
        }
        tau[k] = -num / den;                          // нахил прямої МНК
    }
    return tau;
}
