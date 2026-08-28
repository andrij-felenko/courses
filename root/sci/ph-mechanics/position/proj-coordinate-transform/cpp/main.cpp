#include <cmath>
#include <cstdio>

struct Vec3 { double x, y, z; };

constexpr double A   = 6378137.0;              // WGS84, велика піввісь, м
constexpr double F   = 1.0 / 298.257223563;    // стиснення
constexpr double E2  = F * (2.0 - F);          // квадрат ексцентриситету
constexpr double DEG = 3.14159265358979324 / 180.0;

static Vec3 geodetic_to_ecef(double lat_deg, double lon_deg, double h) {
    const double lat = lat_deg * DEG, lon = lon_deg * DEG;
    const double sf = std::sin(lat), cf = std::cos(lat);
    const double sl = std::sin(lon), cl = std::cos(lon);
    const double N = A / std::sqrt(1.0 - E2 * sf * sf);   // радіус кривини
    return { (N + h) * cf * cl,
             (N + h) * cf * sl,
             (N * (1.0 - E2) + h) * sf };
}

static Vec3 ecef_to_enu(Vec3 p, Vec3 ref, double lat0_deg, double lon0_deg) {
    const double dx = p.x - ref.x, dy = p.y - ref.y, dz = p.z - ref.z;  // трансляція
    const double sf = std::sin(lat0_deg*DEG), cf = std::cos(lat0_deg*DEG);
    const double sl = std::sin(lon0_deg*DEG), cl = std::cos(lon0_deg*DEG);
    return {        -sl*dx +        cl*dy,                 // поворот на East-North-Up
             -sf*cl*dx - sf*sl*dy + cf*dz,
              cf*cl*dx + cf*sl*dy + sf*dz };
}

int main() {
    const Vec3 ref   = geodetic_to_ecef(50.4500, 30.5200, 180.0);  // майданчик
    const Vec3 drone = geodetic_to_ecef(50.4510, 30.5225, 205.0);  // GNSS-фікс
    const Vec3 enu   = ecef_to_enu(drone, ref, 50.4500, 30.5200);
    std::printf("E=%.2f  N=%.2f  U=%.2f m\n", enu.x, enu.y, enu.z);
    // E=177.56  N=111.24  U=25.00 m
    return 0;
}
