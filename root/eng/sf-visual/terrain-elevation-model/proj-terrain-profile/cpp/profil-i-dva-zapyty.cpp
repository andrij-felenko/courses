struct Geo  { double lat, lon; };            // градуси
struct Vec3 { double x, y, z; };

static constexpr double kDeg = 3.14159265358979323846 / 180.0;
static constexpr double kR   = 6371000.0;    // середній радіус Землі, м
static constexpr double kMaxLeg = 10000.0;   // довша ділянка ріжеться на шматки, м

inline Vec3 toVec(const Geo& g) {
    const double la = g.lat * kDeg, lo = g.lon * kDeg, c = std::cos(la);
    return Vec3{ c * std::cos(lo), c * std::sin(lo), std::sin(la) };
}
inline Geo toGeo(const Vec3& v) {
    return Geo{ std::atan2(v.z, std::sqrt(v.x * v.x + v.y * v.y)) / kDeg,
                std::atan2(v.y, v.x) / kDeg };
}
// Центральний кут через atan2 від синуса й косинуса: чистий acos(dot)
// втрачає значущі цифри саме на малих кутах, а тут вони й є.
inline double centralAngle(const Vec3& a, const Vec3& b) {
    const Vec3 c{ a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x };
    return std::atan2(std::sqrt(c.x * c.x + c.y * c.y + c.z * c.z),
                      a.x * b.x + a.y * b.y + a.z * b.z);
}
inline Geo slerp(const Vec3& a, const Vec3& b, double ang, double f) {
    if (ang < 1e-12) return toGeo(a);
    const double s = std::sin(ang);
    const double ka = std::sin((1.0 - f) * ang) / s, kb = std::sin(f * ang) / s;
    return toGeo(Vec3{ ka * a.x + kb * b.x, ka * a.y + kb * b.y, ka * a.z + kb * b.z });
}
