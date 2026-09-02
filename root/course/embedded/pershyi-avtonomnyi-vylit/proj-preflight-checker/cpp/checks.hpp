#pragma once

#include <cstdint>
#include <string>
#include <string_view>
#include <vector>

#include "snapshot.hpp"

// Пороги допуску — рівно ті, що описані в шести бар'єрах статті
namespace limits {
inline constexpr std::uint8_t  gps_min_fix        = 3;      // 3D-Fix і вище
inline constexpr std::uint8_t  gps_min_sats       = 12;
inline constexpr float         gps_max_hdop       = 1.20F;
inline constexpr float         ekf_max_innov      = 0.30F;
inline constexpr float         bat_min_voltage    = 14.8F;  // 4S LiPo
inline constexpr float         bat_max_cell_delta = 0.05F;
inline constexpr float         bat_min_temp_c     = 5.0F;
inline constexpr float         bat_max_temp_c     = 50.0F;
inline constexpr std::uint16_t fence_min_points   = 4;
inline constexpr std::int16_t  rc_min_rssi_dbm    = -85;
inline constexpr std::uint16_t kill_pwm_min       = 980;    // готовність ≈ 1000 мкс
inline constexpr std::uint16_t kill_pwm_max       = 1050;
inline constexpr float         vibe_max           = 0.40F;
} // namespace limits

enum class Barrier : std::uint32_t {
    Gnss      = 1U << 0,
    Ekf       = 1U << 1,
    Battery   = 1U << 2,
    Geofence  = 1U << 3,
    Safety    = 1U << 4,
    Vibration = 1U << 5
};

// Результат одного бар'єра: порожній перелік зауважень і є «пройдено»
struct BarrierResult {
    Barrier                  id{};
    std::string_view         name;
    std::vector<std::string> findings;

    [[nodiscard]] bool passed() const noexcept { return findings.empty(); }
};

class Verdict {
public:
    explicit Verdict(std::vector<BarrierResult> barriers) noexcept
        : barriers_{std::move(barriers)} {}

    [[nodiscard]] bool is_go() const noexcept;
    [[nodiscard]] std::uint32_t passed_mask() const noexcept;
    [[nodiscard]] std::size_t finding_count() const noexcept;

    [[nodiscard]] const std::vector<BarrierResult>& barriers() const noexcept
    {
        return barriers_;
    }

private:
    std::vector<BarrierResult> barriers_;
};

// Проганяє зліпок крізь усі бар'єри. Перша невдача не спиняє перевірку:
// польотній групі потрібен повний перелік зауважень за один захід.
[[nodiscard]] Verdict evaluate(const TelemetrySnapshot& snapshot);
