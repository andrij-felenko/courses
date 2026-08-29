// geometry.hpp — геометрія «супутник ↔ приймач», атмосфера, бюджет рівнів
// і відбитий промінь.
#pragma once

#include <array>
#include <cmath>

namespace gnss {

inline constexpr double kSpeedOfLight = 299792458.0;
inline constexpr double kL1Hz         = 1575420000.0;
inline constexpr double kEarthRate    = 7.2921151467e-5;   // рад/с
inline constexpr double kGm           = 3.986005e14;       // м³/с²
inline constexpr double kRelF         = -4.442807633e-10;

struct Vec3 {
    double x{}, y{}, z{};

    [[nodiscard]] constexpr Vec3 operator-(const Vec3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    [[nodiscard]] constexpr Vec3 operator+(const Vec3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vec3 operator*(double k) const noexcept {
        return {x * k, y * k, z * k};
    }
    [[nodiscard]] constexpr double dot(const Vec3& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }
    [[nodiscard]] double norm() const noexcept { return std::sqrt(dot(*this)); }
};

struct Geodetic {
    double lat{}, lon{}, height{};        // рад, рад, м
};

[[nodiscard]] Vec3     to_ecef(const Geodetic& g) noexcept;
[[nodiscard]] Geodetic to_geodetic(const Vec3& p) noexcept;
[[nodiscard]] Vec3     enu_vector(const Geodetic& ref, double east, double north, double up) noexcept;

// Обертання ECEF за час поширення хвилі (ефект Саньяка).
[[nodiscard]] Vec3 rotate_earth(const Vec3& p, double tau) noexcept;

struct LineOfSight {
    Vec3   unit;
    double range{};
    double elevation{}, azimuth{};
};

[[nodiscard]] LineOfSight line_of_sight(const Vec3& user, const Geodetic& llh,
                                        const Vec3& satellite) noexcept;
[[nodiscard]] double doppler_hz(const LineOfSight& los, const Vec3& user_vel,
                                const Vec3& sat_vel, double f0) noexcept;

// Модель Клобучара живе коефіцієнтами з шапки RINEX — без них її просто немає.
class Ionosphere {
public:
    Ionosphere(std::array<double, 4> alpha, std::array<double, 4> beta) noexcept
        : alpha_{alpha}, beta_{beta} {}

    [[nodiscard]] double delay_s(const Geodetic& user, const LineOfSight& los,
                                 double tow) const noexcept;

    // Ті самі коефіцієнти їдуть у навігаційне повідомлення, сторінка 18.
    [[nodiscard]] const std::array<double, 4>& alpha() const noexcept { return alpha_; }
    [[nodiscard]] const std::array<double, 4>& beta()  const noexcept { return beta_; }

private:
    std::array<double, 4> alpha_{}, beta_{};
};

[[nodiscard]] double troposphere_delay_s(const Geodetic& user, double elevation,
                                         double humidity) noexcept;
[[nodiscard]] double free_space_loss_db(double range_m, double f_hz) noexcept;
[[nodiscard]] double rx_antenna_gain_db(double elevation) noexcept;

// Відбитий промінь: додатковий хід 2·h·sin(θ) і обернена поляризація.
struct Multipath {
    double delay_s{};
    double gamma{};
    double xpol_db{-10.0};

    [[nodiscard]] static Multipath from_geometry(double antenna_height_m, double elevation,
                                                 double reflectivity) noexcept;
};

}  // namespace gnss
