#include <cmath>

constexpr double WGS84_A  = 6378137.0;
constexpr double WGS84_E2 = 6.69437999014e-3;      // 2f − f², f = 1/298.257223563

// Довжина дуги меридіана від екватора до широти phi (радіани), метри.
double meridian_arc(double phi) {
    const double e2 = WGS84_E2, e4 = e2 * e2, e6 = e4 * e2, e8 = e4 * e4;
    const double A = 1.0 + 3.0*e2/4 + 45.0*e4/64 + 175.0*e6/256 + 11025.0*e8/16384;
    const double B =       3.0*e2/8 + 15.0*e4/32 + 525.0*e6/1024 + 2205.0*e8/4096;
    const double C =                  15.0*e4/256 + 105.0*e6/1024 + 2205.0*e8/16384;
    const double D =                                 35.0*e6/3072 +  315.0*e8/12288;
    const double k = WGS84_A * (1.0 - e2);
    return k * (A*phi - B*std::sin(2*phi) + C*std::sin(4*phi) - D*std::sin(6*phi));
}
// meridian_arc(M_PI/2) = 10001965.729 — чверть меридіана WGS-84
