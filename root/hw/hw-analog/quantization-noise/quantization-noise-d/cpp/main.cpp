#include <cstdio>
#include <cmath>

int main() {
    // --- шум квантування 12-бітного АЦП ---
    const int    N   = 12;
    const double Vfs = 3.3;
    double q       = Vfs / (double)(1u << N);    // крок: 3.3/4096 ≈ 0.806 мВ
    double e_quant = q / std::sqrt(12.0);        // q/√12 ≈ 0.233 мВ rms

    // --- тепловий шум опору давача √(4kTRB) ---
    const double k = 1.38e-23, T = 300.0, R = 10000.0, B = 20000.0;
    double e_therm = std::sqrt(4.0 * k * T * R * B);   // ≈ 1.82 мкВ rms

    // --- складаємо незалежні шуми коренем із суми квадратів ---
    double e_total = std::sqrt(e_quant*e_quant + e_therm*e_therm);

    std::printf("шум квантування = %.3f мВ rms\n", e_quant * 1e3);   // 0.233
    std::printf("тепловий шум    = %.4f мВ rms\n", e_therm * 1e3);   // 0.0018
    std::printf("разом           = %.3f мВ rms\n", e_total * 1e3);   // ≈ 0.233
    return 0;
}
