#include <cmath>
#include <cstdint>
#include <cstddef>
#include <algorithm>
#include <initializer_list>
#include <string>
#include <vector>

namespace tiles {

inline constexpr double PI      = 3.14159265358979323846;
inline constexpr double MAX_LAT = 85.0511287798;   // широта зрізу: висота = ширині
inline constexpr int    TILE    = 256;             // сторона тайла в пікселях

struct LatLon { double lat, lon; };
struct BBox   { double north, south, west, east; };
struct TileId { int z; std::int64_t x, y; };

// 2^z точно й дешево — без pow()
inline double pow2(int z) { return std::ldexp(1.0, z); }

// Дробові тайлові координати рівня z -> широта/довгота.
LatLon tile_to_lat_lon(double fx, double fy, int z) {
    const double n   = pow2(z);
    const double lon = fx / n * 360.0 - 180.0;          // горизонталь лінійна
    const double ym  = (0.5 - fy / n) * 2.0 * PI;       // назад у меркаторові одиниці
    return { std::atan(std::sinh(ym)) * 180.0 / PI, lon };
}

// Тайл (z,x,y) плюс піксель усередині нього -> градуси.
LatLon pixel_to_lat_lon(std::int64_t x, std::int64_t y, double px, double py, int z) {
    return tile_to_lat_lon(static_cast<double>(x) + px / TILE,
                           static_cast<double>(y) + py / TILE, z);
}

// Географічні межі тайла: NW-кут і SE-кут.
BBox tile_bounds(std::int64_t x, std::int64_t y, int z) {
    const LatLon nw = tile_to_lat_lon(static_cast<double>(x),     static_cast<double>(y),     z);
    const LatLon se = tile_to_lat_lon(static_cast<double>(x + 1), static_cast<double>(y + 1), z);
    return { nw.lat, se.lat, nw.lon, se.lon };
}
