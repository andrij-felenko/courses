#include "checks.hpp"

#include <algorithm>
#include <array>
#include <format>
#include <numeric>

namespace {

using Findings = std::vector<std::string>;

// Порівняння записані як !(значення <= поріг): NaN, що просочився повз
// парсер, тоді валить перевірку, а не проходить її мовчки.

Findings probe_gnss(const TelemetrySnapshot& s)
{
    Findings out;
    if (s.gps_fix_type < limits::gps_min_fix) {
        out.push_back(std::format("тип рішення {}, потрібен щонайменше 3D-Fix ({})",
                                  static_cast<unsigned>(s.gps_fix_type),
                                  static_cast<unsigned>(limits::gps_min_fix)));
    }
    if (s.gps_satellites < limits::gps_min_sats) {
        out.push_back(std::format("у рішенні {} супутників, потрібно {}",
                                  static_cast<unsigned>(s.gps_satellites),
                                  static_cast<unsigned>(limits::gps_min_sats)));
    }
    if (!(s.gps_hdop <= limits::gps_max_hdop)) {
        out.push_back(std::format("HDOP {:.2f} перевищує допуск {:.2f} (похибка кілька метрів)",
                                  s.gps_hdop, limits::gps_max_hdop));
    }
    return out;
}

Findings probe_ekf(const TelemetrySnapshot& s)
{
    const std::array<std::pair<std::string_view, float>, 3> axes{{
        { "позиції",   s.ekf_pos_innov },
        { "швидкості", s.ekf_vel_innov },
        { "курсу",     s.ekf_yaw_innov }
    }};

    Findings out;
    for (const auto& [axis, innov] : axes) {
        if (!(innov < limits::ekf_max_innov)) {
            out.push_back(std::format("інновація {} {:.2f} при порозі {:.2f} (дрейф оцінки стану)",
                                      axis, innov, limits::ekf_max_innov));
        }
    }
    return out;
}

Findings probe_battery(const TelemetrySnapshot& s)
{
    Findings out;
    if (!(s.battery_voltage >= limits::bat_min_voltage)) {
        out.push_back(std::format("напруга шини {:.2f} В нижча за {:.2f} В",
                                  s.battery_voltage, limits::bat_min_voltage));
    }
    if (!(s.cell_delta_v <= limits::bat_max_cell_delta)) {
        out.push_back(std::format("перекіс осередків {:.3f} В понад {:.3f} В — акумулятор зняти",
                                  s.cell_delta_v, limits::bat_max_cell_delta));
    }
    if (!(s.battery_temp_c >= limits::bat_min_temp_c)) {
        out.push_back(std::format("акумулятор {:.1f} °C, нижче за {:.1f} °C електрохімія загальмована",
                                  s.battery_temp_c, limits::bat_min_temp_c));
    }
    if (!(s.battery_temp_c <= limits::bat_max_temp_c)) {
        out.push_back(std::format("акумулятор перегрітий, {:.1f} °C понад {:.1f} °C",
                                  s.battery_temp_c, limits::bat_max_temp_c));
    }
    return out;
}

Findings probe_geofence(const TelemetrySnapshot& s)
{
    Findings out;
    if (!s.geofence_enabled) {
        out.emplace_back("полігон завантажено, але примусовий контроль меж вимкнено");
    }
    if (s.geofence_points < limits::fence_min_points) {
        out.push_back(std::format("{} вершин, замкнений контур вимагає щонайменше {}",
                                  s.geofence_points, limits::fence_min_points));
    }
    if (s.geofence_action < 1) {
        out.emplace_back("дію при порушенні межі не задано (потрібно RTL або посадку)");
    }
    return out;
}

Findings probe_safety(const TelemetrySnapshot& s)
{
    Findings out;
    if (s.rc_rssi_dbm < limits::rc_min_rssi_dbm) {
        out.push_back(std::format("рівень сигналу пульта {} дБм на стоянці нижчий за {} дБм",
                                  s.rc_rssi_dbm, limits::rc_min_rssi_dbm));
    }
    if (s.rc_kill_channel < limits::kill_pwm_min || s.rc_kill_channel > limits::kill_pwm_max) {
        out.push_back(std::format("аварійний канал {} мкс поза вікном готовності {}..{} мкс",
                                  s.rc_kill_channel, limits::kill_pwm_min, limits::kill_pwm_max));
    }
    return out;
}

Findings probe_vibration(const TelemetrySnapshot& s)
{
    Findings out;
    if (!(s.acc_vibe_floor <= limits::vibe_max)) {
        out.push_back(std::format("фоновий шум {:.2f} м/с² при нерухомих гвинтах, поріг {:.2f}",
                                  s.acc_vibe_floor, limits::vibe_max));
    }
    return out;
}

struct Rule {
    Barrier          id;
    std::string_view name;
    Findings (*probe)(const TelemetrySnapshot&);
};

// Таблиця бар'єрів: додати сьомий — це один рядок, а не сьома гілка в evaluate
constexpr std::array<Rule, 6> RULES{{
    { Barrier::Gnss,      "GNSS",     &probe_gnss      },
    { Barrier::Ekf,       "EKF",      &probe_ekf       },
    { Barrier::Battery,   "Живлення", &probe_battery   },
    { Barrier::Geofence,  "Геозона",  &probe_geofence  },
    { Barrier::Safety,    "RC/Kill",  &probe_safety    },
    { Barrier::Vibration, "Вібрації", &probe_vibration }
}};

} // namespace

bool Verdict::is_go() const noexcept
{
    return std::ranges::all_of(barriers_, [](const BarrierResult& b) { return b.passed(); });
}

std::uint32_t Verdict::passed_mask() const noexcept
{
    std::uint32_t mask = 0;
    for (const auto& barrier : barriers_) {
        if (barrier.passed()) {
            mask |= static_cast<std::uint32_t>(barrier.id);
        }
    }
    return mask;
}

std::size_t Verdict::finding_count() const noexcept
{
    return std::accumulate(barriers_.begin(), barriers_.end(), std::size_t{0},
                           [](std::size_t sum, const BarrierResult& b) {
                               return sum + b.findings.size();
                           });
}

Verdict evaluate(const TelemetrySnapshot& snapshot)
{
    std::vector<BarrierResult> results;
    results.reserve(RULES.size());

    for (const auto& rule : RULES) {
        results.push_back(BarrierResult{rule.id, rule.name, rule.probe(snapshot)});
    }
    return Verdict{std::move(results)};
}
