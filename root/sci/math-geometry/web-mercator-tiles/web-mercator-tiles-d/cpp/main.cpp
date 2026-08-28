#include <cmath>
#include <algorithm>

constexpr double MAX_LAT = 85.0511287798;   // широта зрізу: висота карти = ширині
constexpr int    TILE    = 256;             // сторона тайла в пікселях
constexpr double EQUATOR = 2.0 * M_PI * 6378137.0;   // 40 075 016.686 м

struct TilePos { int x, y; double px, py; };

// Географічні координати -> тайл рівня z і піксель усередині нього.
TilePos lat_lon_to_tile(double lat_deg, double lon_deg, int z) {
    const double lat = std::clamp(lat_deg, -MAX_LAT, MAX_LAT);  // зріз полярних шапок
    const double phi = lat * M_PI / 180.0;

    const double xn = (lon_deg + 180.0) / 360.0;                // довгота лінійна
    const double ym = std::log(std::tan(M_PI / 4.0 + phi / 2.0));  // інтеграл секанса
    const double yn = 0.5 - ym / (2.0 * M_PI);                  // мінус: північ угорі

    const double n  = std::ldexp(1.0, z);                       // 2^z без pow()
    const double fx = xn * n;
    const double fy = yn * n;
    const double ix = std::floor(fx);
    const double iy = std::floor(fy);
    return { static_cast<int>(ix), static_cast<int>(iy),
             (fx - ix) * TILE, (fy - iy) * TILE };
}

// Скільки метрів землі в пікселі на цій широті й цьому рівні.
double resolution(double lat_deg, int z) {
    return EQUATOR * std::cos(lat_deg * M_PI / 180.0) / (TILE * std::ldexp(1.0, z));
}
