#include <cmath>

// Означальні сталі WGS-84 (задані точно, не виміряні).
constexpr double WGS84_A     = 6378137.0;            // велика піввісь, м
constexpr double WGS84_INV_F = 298.257223563;        // обернене сплющення
constexpr double DEG2RAD     = 3.14159265358979324 / 180.0;

struct Radii { double m, n; };                       // меридіанний і першого вертикала

Radii wgs84_radii(double lat_deg) {
    const double f  = 1.0 / WGS84_INV_F;
    const double e2 = 2.0 * f - f * f;               // квадрат ексцентриситету
    const double s  = std::sin(lat_deg * DEG2RAD);
    const double w2 = 1.0 - e2 * s * s;
    const double w  = std::sqrt(w2);
    return { WGS84_A * (1.0 - e2) / (w2 * w), WGS84_A / w };
}

// Скільки метрів в одному градусі широти й довготи на цій широті.
void metres_per_degree(double lat_deg, double& north, double& east) {
    const Radii r = wgs84_radii(lat_deg);
    north = r.m * DEG2RAD;
    east  = r.n * DEG2RAD * std::cos(lat_deg * DEG2RAD);
}
// lat = 50°:  north ≈ 111 229 м/°,  east ≈ 71 696 м/°
