#include <cmath>
#include <cstdio>

int main() {
    double m = 2.0, phi = 20.0*M_PI/180;
    int N1 = 20, N2 = 40;

    double r1 = m*N1/2, r2 = m*N2/2;
    double rb1 = r1*std::cos(phi), rb2 = r2*std::cos(phi);
    double ra1 = r1 + m, ra2 = r2 + m;          // кола вершин
    double a  = r1 + r2;                        // міжосьова відстань

    double line = std::sqrt(ra1*ra1 - rb1*rb1)
                + std::sqrt(ra2*ra2 - rb2*rb2)
                - a*std::sin(phi);
    double pb  = M_PI * m * std::cos(phi);      // основний крок
    double eps = line / pb;

    std::printf("%.3f %.3f\n", pb, eps);        // 5.904  1.635
    return 0;
}
