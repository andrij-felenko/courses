#include <cmath>
#include <cstdio>

// Наскільки тихіший вищий порядок коло несучої на даному відступі.
// S_phi(f) ~ [2*sin(pi*f/fref)]^(2(L-1)); беремо відношення L=3 до L=2.

int main() {
    const double f_ref = 26.0e6;   // опора 26 МГц
    const double f_off = 10.0e3;   // відступ 10 кГц

    const double s = 2.0 * std::sin(M_PI * f_off / f_ref);   // формувальний множник |NTF|

    // показник фазового шуму = 2*(L-1):  L=2 -> степінь 2;  L=3 -> степінь 4
    const double pn_L2 = std::pow(s, 2.0);    // ~ [2 sin]^2
    const double pn_L3 = std::pow(s, 4.0);    // ~ [2 sin]^4

    const double ratio_db = 10.0 * std::log10(pn_L3 / pn_L2);   // у децибелах
    std::printf("|NTF| = %.6f\n", s);
    std::printf("3-й порядок тихіший за 2-й на %.1f дБ\n", -ratio_db);
    return 0;
}
