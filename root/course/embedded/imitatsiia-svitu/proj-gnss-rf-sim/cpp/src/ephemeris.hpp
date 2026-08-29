// ephemeris.hpp — навігаційний файл RINEX 3 і стан супутника в ECEF
// за алгоритмом IS-GPS-200.
#pragma once

#include <expected>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

#include "geometry.hpp"
#include "gps_time.hpp"

namespace gnss {

struct SatelliteState {
    Vec3   position;
    Vec3   velocity;
    double clock_bias{};     // с, разом із релятивістською поправкою
    double clock_drift{};    // с/с
};

enum class OrbitError { Expired, NoConvergence };

struct Ephemeris {
    int prn{}, health{}, iode{}, iodc{}, week{};
    double toc{}, toe{};
    double af0{}, af1{}, af2{}, tgd{}, accuracy{};
    // Кути вже переведено в радіани; у файлі вони в напівобертах.
    double sqrt_a{}, ecc{}, m0{}, delta_n{}, omega0{}, i0{}, omega_arg{}, omega_dot{}, idot{};
    double cuc{}, cus{}, crc{}, crs{}, cic{}, cis{};

    [[nodiscard]] std::expected<SatelliteState, OrbitError> state_at(GpsTime t) const noexcept;
};

enum class RinexError { NotFound, TruncatedHeader, UnsupportedVersion, NoUsableRecords };

[[nodiscard]] std::string_view describe(RinexError e) noexcept;

class Navigation {
public:
    [[nodiscard]] static std::expected<Navigation, RinexError> load(const std::string& path);

    // Найсвіжіший придатний набір для апарата; nullptr, якщо такого немає.
    [[nodiscard]] const Ephemeris* select(int prn, GpsTime t) const noexcept;

    [[nodiscard]] const std::vector<Ephemeris>& all() const noexcept { return ephemerides_; }
    [[nodiscard]] std::vector<Ephemeris>&       all()       noexcept { return ephemerides_; }
    [[nodiscard]] const std::optional<Ionosphere>& ionosphere() const noexcept { return iono_; }
    [[nodiscard]] std::optional<int> leap_seconds() const noexcept { return leap_; }

private:
    std::vector<Ephemeris>    ephemerides_;
    std::optional<Ionosphere> iono_;
    std::optional<int>        leap_;
};

}  // namespace gnss
