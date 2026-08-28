#include <cmath>
#include <stdexcept>

constexpr double WGS84_A   = 6378137.0;
constexpr double WGS84_F   = 1.0 / 298.257223563;
constexpr double WGS84_E2  = WGS84_F * (2.0 - WGS84_F);
constexpr double WGS84_B   = WGS84_A * (1.0 - WGS84_F);
constexpr double WGS84_EP2 = WGS84_E2 / (1.0 - WGS84_E2);
constexpr double RAD2DEG   = 57.29577951308232;

struct Geodetic { double lat_deg, lon_deg, h; };

// Висоту беремо тією формулою, у якій знаменник не наближається до нуля.
static double height_from(double p, double z, double phi) {
    const double s = std::sin(phi), c = std::cos(phi);
    const double N = WGS84_A / std::sqrt(1.0 - WGS84_E2 * s * s);
    return std::fabs(c) > 0.5 ? p / c - N
                              : z / s - N * (1.0 - WGS84_E2);
}

// Боуринг 1976: один крок для всього наземного, другий — для орбіт.
Geodetic ecef_to_geodetic(double x, double y, double z, int steps = 1) {
    const double p = std::hypot(x, y);

    // Усередині цього еліпса нормаль не єдина — широти просто немає.
    if (p * p + (1.0 - WGS84_E2) * z * z < (WGS84_E2 * WGS84_A) * (WGS84_E2 * WGS84_A))
        throw std::domain_error("точка всередині еволюти: розв'язок неоднозначний");

    double beta = std::atan2(WGS84_A * z, WGS84_B * p);   // точно при h = 0
    double phi  = 0.0;
    for (int i = 0; i < steps; ++i) {
        const double sb = std::sin(beta), cb = std::cos(beta);
        phi = std::atan2(z + WGS84_EP2 * WGS84_B * sb * sb * sb,
                         p - WGS84_E2  * WGS84_A * cb * cb * cb);
        beta = std::atan2((1.0 - WGS84_F) * std::sin(phi), std::cos(phi));
    }
    return { phi * RAD2DEG, std::atan2(y, x) * RAD2DEG, height_from(p, z, phi) };
}

// Проста ітерація: |F'| <= e² = 0.0067, тож п'ять кроків вистачає завжди.
Geodetic ecef_to_geodetic_iter(double x, double y, double z) {
    const double p = std::hypot(x, y);
    double phi = std::atan2(z, p * (1.0 - WGS84_E2));     // старт: h = 0
    for (int i = 0; i < 5; ++i) {
        const double s = std::sin(phi);
        const double N = WGS84_A / std::sqrt(1.0 - WGS84_E2 * s * s);
        phi = std::atan2(z + WGS84_E2 * N * s, p);
    }
    return { phi * RAD2DEG, std::atan2(y, x) * RAD2DEG, height_from(p, z, phi) };
}
