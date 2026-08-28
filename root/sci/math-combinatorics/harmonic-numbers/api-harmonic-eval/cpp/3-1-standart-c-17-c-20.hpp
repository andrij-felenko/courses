#include <cmath>

namespace std {
    // Гамма-функція та її логарифм
    double tgamma(double x);
    double lgamma(double x);

    // Дзета-функція Рімана (доступна з C++17)
    double riemann_zeta(double s);
    float  riemann_zetaf(float s);
}
