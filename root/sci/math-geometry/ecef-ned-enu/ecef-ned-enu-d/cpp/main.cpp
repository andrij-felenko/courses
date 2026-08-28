#include <cmath>
#include <numbers>

// WGS-84: перші дві сталі — точні за означенням, третя з них випливає.
constexpr double WGS84_A  = 6378137.0;                  // велика піввісь, м
constexpr double WGS84_F  = 1.0 / 298.257223563;        // сплюснутість
constexpr double WGS84_E2 = WGS84_F * (2.0 - WGS84_F);  // квадрат ексцентриситету
constexpr double DEG      = std::numbers::pi / 180.0;

struct Geodetic { double lat_deg, lon_deg, h; };
struct Vec3     { double x, y, z; };
struct Enu      { double east, north, up; };

// (φ, λ, h) -> ECEF. Тільки double: самі координати мають порядок 6.4·10⁶ м.
Vec3 geodetic_to_ecef(Geodetic g) {
    const double phi = g.lat_deg * DEG, lam = g.lon_deg * DEG;
    const double s = std::sin(phi), c = std::cos(phi);
    const double N = WGS84_A / std::sqrt(1.0 - WGS84_E2 * s * s);
    const double p = (N + g.h) * c;              // відстань до осі обертання
    return { p * std::cos(lam),
             p * std::sin(lam),
             (N * (1.0 - WGS84_E2) + g.h) * s };
}

// Поворот ВІЛЬНОГО вектора з ECEF у місцеву трійку — рядки матриці R_ENU.
Enu rotate_to_enu(Vec3 v, double lat_deg, double lon_deg) {
    const double phi = lat_deg * DEG, lam = lon_deg * DEG;
    const double sp = std::sin(phi), cp = std::cos(phi);
    const double sl = std::sin(lam), cl = std::cos(lam);
    return { -sl * v.x + cl * v.y,
             -sp * cl * v.x - sp * sl * v.y + cp * v.z,
              cp * cl * v.x + cp * sl * v.y + sp * v.z };
}

// ТОЧКА: спершу відняти початок, аж потім повертати — і брати кути ПОЧАТКУ.
Enu point_to_enu(Geodetic origin, Geodetic p) {
    const Vec3 r0 = geodetic_to_ecef(origin);
    const Vec3 r  = geodetic_to_ecef(p);
    return rotate_to_enu({ r.x - r0.x, r.y - r0.y, r.z - r0.z },
                         origin.lat_deg, origin.lon_deg);
}

// NED — та сама трійка в іншому порядку: поміняти осі й розвернути вертикаль.
Vec3 enu_to_ned(Enu q) { return { q.north, q.east, -q.up }; }
