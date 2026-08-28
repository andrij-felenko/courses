#include <cstdio>

constexpr double EPS0 = 8.854e-14;      // Ф/см — проникність вакууму

constexpr double cube(double x) { return x * x * x; }

struct Mat {
    const char* name;
    double er;                          // відносна проникність
    double mu;                          // рухливість, см²/(В·с)
    double ec;                          // критичне поле, В/см

    constexpr double bfom() const {     // Вт/см²
        return er * EPS0 * mu * cube(ec);
    }
};

constexpr Mat MAT[] = {
    {"Si",     11.7, 1350, 0.30e6},
    {"4H-SiC",  9.7,  950, 2.80e6},
    {"GaN",     9.0, 1250, 3.30e6},
};

int main() {
    constexpr Mat si = MAT[0];
    constexpr double base = si.bfom();
    std::printf("BFOM(Si) = %.3g Вт/см²  — точка відліку\n\n", base);

    for (const Mat& m : MAT) {
        const double k_eps = m.er / si.er;        // внесок проникності
        const double k_mu  = m.mu / si.mu;        // внесок рухливості
        const double k_ec  = cube(m.ec / si.ec);  // внесок куба поля
        std::printf("%-7s  ε×%.2f  μ×%.2f  поле³×%7.1f  →  разом ×%.0f\n",
                    m.name, k_eps, k_mu, k_ec, m.bfom() / base);
    }
    return 0;
}
