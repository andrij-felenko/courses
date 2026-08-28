#include <cmath>
#include <cstdio>

int main() {
    double m = 2.0;                 // модуль, мм
    double phi = 20.0 * M_PI / 180; // кут зачеплення
    int N1 = 20, N2 = 40;           // числа зубів

    double d1 = m * N1;                 // 2·20 = 40 мм
    double d2 = m * N2;                 // 2·40 = 80 мм
    double db1 = d1 * std::cos(phi);    // 40·cos20° = 37.59 мм
    double db2 = d2 * std::cos(phi);    // 80·cos20° = 75.18 мм
    double center = (d1 + d2) / 2;      // (40+80)/2 = 60 мм
    double ratio = (double)N2 / N1;     // 40/20 = 2.0

    std::printf("%.1f %.1f %.1f %.1f\n", d1, d2, center, ratio);
    return 0;
}
