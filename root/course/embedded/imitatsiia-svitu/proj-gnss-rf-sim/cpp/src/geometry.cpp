#include "geometry.hpp"

#include <algorithm>
#include <numbers>

namespace gnss {
namespace {

constexpr double kA  = 6378137.0;
constexpr double kF  = 1.0 / 298.257223563;
constexpr double kE2 = kF * (2.0 - kF);
constexpr double kPi = std::numbers::pi;

}  // namespace

Vec3 to_ecef(const Geodetic& g) noexcept
{
    const double sp = std::sin(g.lat), cp = std::cos(g.lat);
    const double sl = std::sin(g.lon), cl = std::cos(g.lon);
    const double n = kA / std::sqrt(1.0 - kE2 * sp * sp);

    return {(n + g.height) * cp * cl,
            (n + g.height) * cp * sl,
            (n * (1.0 - kE2) + g.height) * sp};
}

Geodetic to_geodetic(const Vec3& p) noexcept
{
    // Формула Боурінга: без ітерацій, з похибкою менш ніж міліметр.
    constexpr double b   = kA * (1.0 - kF);
    constexpr double ep2 = (kA * kA - b * b) / (b * b);

    const double r = std::hypot(p.x, p.y);
    Geodetic g{};
    g.lon = std::atan2(p.y, p.x);

    if (r < 1e-6) {                       // точка на осі обертання
        g.lat = (p.z >= 0.0) ? kPi / 2.0 : -kPi / 2.0;
        g.height = std::abs(p.z) - b;
        return g;
    }

    const double theta = std::atan2(p.z * kA, r * b);
    const double st = std::sin(theta), ct = std::cos(theta);
    g.lat = std::atan2(p.z + ep2 * b * st * st * st, r - kE2 * kA * ct * ct * ct);

    const double sp = std::sin(g.lat);
    g.height = r / std::cos(g.lat) - kA / std::sqrt(1.0 - kE2 * sp * sp);
    return g;
}

Vec3 enu_vector(const Geodetic& ref, double east, double north, double up) noexcept
{
    const double sp = std::sin(ref.lat), cp = std::cos(ref.lat);
    const double sl = std::sin(ref.lon), cl = std::cos(ref.lon);

    return {-sl * east - sp * cl * north + cp * cl * up,
             cl * east - sp * sl * north + cp * sl * up,
                         cp      * north + sp      * up};
}

Vec3 rotate_earth(const Vec3& p, double tau) noexcept
{
    const double a = kEarthRate * tau;
    const double c = std::cos(a), s = std::sin(a);
    return {p.x * c + p.y * s, -p.x * s + p.y * c, p.z};
}

LineOfSight line_of_sight(const Vec3& user, const Geodetic& llh, const Vec3& satellite) noexcept
{
    LineOfSight los{};
    const Vec3 d = satellite - user;
    los.range = d.norm();
    if (los.range < 1.0) return los;             // виродження: приймач у фазовому центрі

    los.unit = d * (1.0 / los.range);

    const double sp = std::sin(llh.lat), cp = std::cos(llh.lat);
    const double sl = std::sin(llh.lon), cl = std::cos(llh.lon);
    const double east  = -sl * los.unit.x + cl * los.unit.y;
    const double north = -sp * cl * los.unit.x - sp * sl * los.unit.y + cp * los.unit.z;
    const double up    =  cp * cl * los.unit.x + cp * sl * los.unit.y + sp * los.unit.z;

    los.elevation = std::atan2(up, std::hypot(east, north));
    los.azimuth   = std::atan2(east, north);
    if (los.azimuth < 0.0) los.azimuth += 2.0 * kPi;
    return los;
}

double doppler_hz(const LineOfSight& los, const Vec3& user_vel,
                  const Vec3& sat_vel, double f0) noexcept
{
    // Додатна променева швидкість означає віддалення, отже зсув униз.
    return -f0 * (sat_vel - user_vel).dot(los.unit) / kSpeedOfLight;
}

double Ionosphere::delay_s(const Geodetic& user, const LineOfSight& los, double tow) const noexcept
{
    if (los.elevation <= 0.0) return 0.0;

    // Модель працює в напівобертах.
    const double el  = los.elevation / kPi;
    const double lat = user.lat / kPi;
    const double lon = user.lon / kPi;

    const double psi = 0.0137 / (el + 0.11) - 0.022;
    double phi_i = std::clamp(lat + psi * std::cos(los.azimuth), -0.416, 0.416);
    const double lam_i = lon + psi * std::sin(los.azimuth) / std::cos(phi_i * kPi);
    const double phi_m = phi_i + 0.064 * std::cos((lam_i - 1.617) * kPi);   // геомагнітна широта

    double t = std::fmod(43200.0 * lam_i + tow, 86400.0);
    if (t < 0.0) t += 86400.0;

    double amp = alpha_[0] + phi_m * (alpha_[1] + phi_m * (alpha_[2] + phi_m * alpha_[3]));
    double per = beta_[0]  + phi_m * (beta_[1]  + phi_m * (beta_[2]  + phi_m * beta_[3]));
    amp = std::max(amp, 0.0);
    per = std::max(per, 72000.0);

    const double x = 2.0 * kPi * (t - 50400.0) / per;
    const double f = 1.0 + 16.0 * std::pow(0.53 - el, 3.0);      // нахилений хід променя

    const double zenith = (std::abs(x) < 1.57)
                        ? 5e-9 + amp * (1.0 + x * x * (-0.5 + x * x / 24.0))
                        : 5e-9;
    return f * zenith;
}

double troposphere_delay_s(const Geodetic& user, double elevation, double humidity) noexcept
{
    elevation = std::max(elevation, 3.0 * kPi / 180.0);      // нижче модель не працює
    const double h = std::clamp(user.height, 0.0, 12000.0);

    const double pressure = 1013.25 * std::pow(1.0 - 2.2557e-5 * h, 5.2568);   // гПа
    const double temp     = 15.0 - 6.5e-3 * h + 273.16;                        // К
    const double vapour   = 6.108 * humidity
                          * std::exp((17.15 * temp - 4684.0) / (temp - 38.45));

    const double z = kPi / 2.0 - elevation;
    const double dry = 0.0022768 * pressure
                     / (1.0 - 0.00266 * std::cos(2.0 * user.lat) - 0.00028 * h * 1e-3)
                     / std::cos(z);
    const double wet = 0.002277 * (1255.0 / temp + 0.05) * vapour / std::cos(z);

    return (dry + wet) / kSpeedOfLight;
}

double free_space_loss_db(double range_m, double f_hz) noexcept
{
    return 20.0 * std::log10(4.0 * kPi * std::max(range_m, 1.0) * f_hz / kSpeedOfLight);
}

double rx_antenna_gain_db(double elevation) noexcept
{
    if (elevation <= 0.0) return -20.0;
    return std::max(-20.0, 3.0 + 12.0 * std::log10(std::sin(elevation) + 1e-3));
}

Multipath Multipath::from_geometry(double antenna_height_m, double elevation,
                                   double reflectivity) noexcept
{
    Multipath mp{};
    mp.delay_s = 2.0 * antenna_height_m * std::sin(std::max(elevation, 0.0)) / kSpeedOfLight;
    mp.gamma   = reflectivity;
    // Дзеркало обертає поляризацію RHCP→LHCP; антена бере таку хвилю з великою
    // втратою, але не з нульовою — залишок і псує автокореляційний пік.
    mp.xpol_db = -10.0;
    return mp;
}

}  // namespace gnss
