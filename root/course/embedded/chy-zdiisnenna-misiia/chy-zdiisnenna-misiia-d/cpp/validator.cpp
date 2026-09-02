#include "validator.hpp"

#include <algorithm>
#include <cmath>
#include <format>
#include <limits>
#include <utility>

namespace mission {
namespace {

float solar_declination_deg(int day_of_year) noexcept
{
    const auto arg_deg = static_cast<float>(360.0 / 365.0 * (day_of_year - 81));
    return 23.45f * std::sin(static_cast<float>(arg_deg * kDegToRad));
}

std::unexpected<Rejection> reject(Failure reason, std::size_t index, std::string detail)
{
    return std::unexpected(Rejection{reason, index, std::move(detail)});
}

}  // namespace

float solar_elevation_deg(double latitude_deg, int day_of_year, float solar_hour) noexcept
{
    const double phi   = latitude_deg * kDegToRad;
    const double delta = static_cast<double>(solar_declination_deg(day_of_year)) * kDegToRad;
    const double hour  = 15.0 * (static_cast<double>(solar_hour) - 12.0) * kDegToRad;

    const double sin_alpha =
        std::clamp(std::sin(phi) * std::sin(delta) + std::cos(phi) * std::cos(delta) * std::cos(hour),
                   -1.0, 1.0);
    return static_cast<float>(std::asin(sin_alpha) * kRadToDeg);
}

std::expected<void, Rejection> Validator::check_plan(const Plan& plan) const
{
    const auto& wps = plan.waypoints;
    if (wps.size() < 2) {
        return reject(Failure::BadPlan, kWholeMission,
                      std::format("точок у плані: {}", wps.size()));
    }

    const auto& ac = aircraft_.spec();
    for (std::size_t i = 0; i < wps.size(); ++i) {
        const auto& wp = wps[i];
        if (!std::isfinite(wp.position.latitude_deg) || !std::isfinite(wp.position.longitude_deg) ||
            !std::isfinite(wp.position.altitude_msl_m)) {
            return reject(Failure::BadPlan, i, std::format("точка {}: нечислові координати", i));
        }
        if (std::abs(wp.position.latitude_deg) > 90.0 || std::abs(wp.position.longitude_deg) > 180.0) {
            return reject(Failure::BadPlan, i, std::format("точка {}: координати поза межами", i));
        }
        if (wp.loiter_s < 0.0f) {
            return reject(Failure::BadPlan, i, std::format("точка {}: від'ємний час очікування", i));
        }
        if (i > 0 && (wp.airspeed_mps < ac.airspeed_min_mps || wp.airspeed_mps > ac.airspeed_max_mps)) {
            return reject(Failure::BadPlan, i,
                          std::format("точка {}: швидкість {:.1f} поза діапазоном {:.1f}...{:.1f} м/с",
                                      i, wp.airspeed_mps, ac.airspeed_min_mps, ac.airspeed_max_mps));
        }
    }
    return {};
}

std::expected<Report, Rejection> Validator::run(const Plan& plan) const
{
    if (auto ok = check_plan(plan); !ok) {
        return std::unexpected(ok.error());
    }

    const auto& wps    = plan.waypoints;
    const auto& limits = plan.limits;

    Report report;
    report.min_clearance_m      = std::numeric_limits<float>::max();
    report.min_ground_speed_mps = std::numeric_limits<float>::max();

    std::vector<LegState> legs;
    legs.reserve(wps.size() - 1);

    float energy_wh = limits.takeoff_wh;
    float elapsed_s = 0.0f;

    for (std::size_t i = 0; i + 1 < wps.size(); ++i) {
        const auto& from = wps[i];
        const auto& to   = wps[i + 1];

        const float leg_dist  = distance_m(from.position, to.position);
        const float track_deg = bearing_deg(from.position, to.position);
        const float v_air     = to.airspeed_mps;

        if (leg_dist < 1.0f) {
            return reject(Failure::BadPlan, i,
                          std::format("відрізок {} вироджений ({:.1f} м)", i, leg_dist));
        }
        report.total_distance_m += leg_dist;

        // 1. Вітрове вікно. Вітер беремо на середній висоті відрізка.
        const GeoPoint mid = interpolate(from.position, to.position, 0.5f);
        const auto mid_agl = dem_.height_agl(mid);
        if (!mid_agl) {
            return reject(Failure::DemGap, i, std::format("відрізок {} поза підвікном DEM", i));
        }

        const auto leg_wind = solve_leg(wind_, track_deg, *mid_agl, v_air);
        if (!leg_wind) {
            return reject(leg_wind.error(), i,
                          std::format("відрізок {}: вітер {:.1f} м/с проти повітряної {:.1f} м/с",
                                      i, wind_.at_height(*mid_agl), v_air));
        }
        report.min_ground_speed_mps =
            std::min(report.min_ground_speed_mps, leg_wind->ground_speed_mps);

        if (leg_wind->ground_speed_mps < limits.min_ground_speed_mps) {
            return reject(Failure::GroundSpeedTooLow, i,
                          std::format("відрізок {}: шляхова {:.1f} м/с (вітер {:.1f}, поріг {:.1f})",
                                      i, leg_wind->ground_speed_mps, leg_wind->speed_mps,
                                      limits.min_ground_speed_mps));
        }

        const float leg_time = leg_dist / leg_wind->ground_speed_mps;

        // 2. Градієнт набору висоти.
        const float delta_h    = to.position.altitude_msl_m - from.position.altitude_msl_m;
        const float climb_rate = delta_h / leg_time;
        if (climb_rate > aircraft_.spec().max_climb_mps) {
            return reject(Failure::ClimbRateExceeded, i,
                          std::format("відрізок {}: треба {:.2f} м/с набору, апарат дає {:.2f}",
                                      i, climb_rate, aircraft_.spec().max_climb_mps));
        }

        // 3. Кліренс по всій довжині відрізка.
        const auto scan = dem_.scan_leg(from.position, to.position,
                                        limits.sample_step_m, limits.safe_clearance_m);
        if (!scan) {
            return reject(scan.error(), i, std::format("відрізок {} поза підвікном DEM", i));
        }
        report.min_clearance_m = std::min(report.min_clearance_m, scan->min_clearance_m);
        if (scan->collision) {
            return reject(Failure::TerrainCollision, i,
                          std::format("відрізок {}: кліренс {:.0f} м на {:.0f} м від початку (треба {:.0f})",
                                      i, scan->min_clearance_m, scan->min_clearance_dist_m,
                                      limits.safe_clearance_m));
        }

        // 4. Енергія відрізка.
        const float rho   = air_density(mid.altitude_msl_m);
        const float p_leg = aircraft_.level_power_w(v_air, rho)
                          + aircraft_.climb_power_w(climb_rate)
                          + aircraft_.spec().avionics_w;

        const auto current = battery_.current_a(p_leg);
        if (!current) {
            return reject(current.error(), i,
                          std::format("відрізок {}: потрібно {:.0f} Вт", i, p_leg));
        }
        if (p_leg > report.peak_power_w) {
            report.peak_power_w   = p_leg;
            report.peak_current_a = *current;
        }

        energy_wh += p_leg * leg_time / 3600.0f;
        elapsed_s += leg_time;

        // 5. Сонце над ділянкою зйомки — на середині проходу відрізка.
        if (to.survey) {
            const float solar_hour = limits.start_hour_local + (elapsed_s - leg_time * 0.5f) / 3600.0f;
            const float sun = solar_elevation_deg(limits.site_latitude_deg, limits.day_of_year, solar_hour);
            report.min_sun_elevation_deg = std::min(report.min_sun_elevation_deg, sun);
            if (sun < limits.min_sun_elevation_deg) {
                return reject(Failure::SunTooLow, i,
                              std::format("відрізок {}: сонце {:.1f}° (треба {:.1f}°)",
                                          i, sun, limits.min_sun_elevation_deg));
            }
        }

        // Очікування на точці: висіння для коптера, віраж для літака.
        if (to.loiter_s > 0.0f) {
            energy_wh += (aircraft_.loiter_power_w(rho) + aircraft_.spec().avionics_w)
                       * to.loiter_s / 3600.0f;
            elapsed_s += to.loiter_s;
        }

        legs.push_back(LegState{leg_dist, leg_time, leg_wind->ground_speed_mps, energy_wh});
    }

    energy_wh += limits.landing_wh;
    report.total_time_s    = elapsed_s;
    report.total_energy_wh = energy_wh;

    // Доступна ємність залежить від середнього струму — тому рахуємо її
    // після проходу всіх відрізків, за фактичною середньою потужністю.
    float avg_current_a = 0.0f;
    if (elapsed_s > 0.0f) {
        const float avg_power_w = energy_wh * 3600.0f / elapsed_s;
        const auto  current     = battery_.current_a(avg_power_w);
        if (!current) {
            return reject(current.error(), kWholeMission,
                          std::format("середня потужність {:.0f} Вт недосяжна", avg_power_w));
        }
        avg_current_a = *current;
    }
    report.delivered_energy_wh = battery_.delivered_wh(avg_current_a);
    report.usable_energy_wh    = battery_.usable_wh(avg_current_a);

    // 6. Часове вікно й захід сонця.
    if (elapsed_s > limits.max_duration_s) {
        return reject(Failure::TimeWindow, kWholeMission,
                      std::format("{:.0f} с проти дозволених {:.0f} с", elapsed_s, limits.max_duration_s));
    }
    const float finish_hour = limits.start_hour_local + elapsed_s / 3600.0f;
    const float deadline    = limits.sunset_hour_local - 0.5f;   // 30 хв до сутінків
    if (finish_hour > deadline) {
        return reject(Failure::SunsetDeadline, kWholeMission,
                      std::format("посадка о {:.2f}, крайній строк {:.2f}", finish_hour, deadline));
    }

    // 7. Енергетичний баланс.
    if (energy_wh > report.usable_energy_wh) {
        return reject(Failure::EnergyBudget, kWholeMission,
                      std::format("потрібно {:.1f} Вт·год, доступно {:.1f} Вт·год",
                                  energy_wh, report.usable_energy_wh));
    }
    report.reserve_left_pct =
        (report.delivered_energy_wh - energy_wh) / report.delivered_energy_wh * 100.0f;

    // 8. Точка безпечного повернення.
    if (auto ok = check_safe_return(plan, legs, report); !ok) {
        return std::unexpected(ok.error());
    }

    return report;
}

std::expected<void, Rejection> Validator::check_safe_return(const Plan& plan,
                                                            const std::vector<LegState>& legs,
                                                            Report& report) const
{
    const GeoPoint home       = plan.waypoints.front().position;
    const float    reserve_wh = battery_.spec().reserve_margin * battery_.nominal_wh();

    for (std::size_t k = 1; k < plan.waypoints.size(); ++k) {
        const auto& wp        = plan.waypoints[k];
        const float dist_home = distance_m(wp.position, home);
        if (dist_home < 1.0f) {
            continue;   // фінальна точка збігається з домом
        }

        const auto agl = dem_.height_agl(wp.position);
        if (!agl) {
            return reject(Failure::DemGap, k, std::format("точка {} поза підвікном DEM", k));
        }

        const auto back = solve_leg(wind_, bearing_deg(wp.position, home), *agl, wp.airspeed_mps);
        if (!back || back->ground_speed_mps < plan.limits.min_ground_speed_mps) {
            return reject(Failure::NoSafeReturn, k,
                          std::format("з точки {} повернення проти вітру неможливе", k));
        }

        const float rho    = air_density(wp.position.altitude_msl_m);
        const float p_back = aircraft_.level_power_w(wp.airspeed_mps, rho) + aircraft_.spec().avionics_w;
        const float e_rtl  = p_back * (dist_home / back->ground_speed_mps) / 3600.0f
                           + plan.limits.landing_wh;
        const float remaining = report.delivered_energy_wh - legs[k - 1].energy_wh_at_end;

        if (remaining - e_rtl < reserve_wh) {
            return reject(Failure::NoSafeReturn, k,
                          std::format("у точці {} залишок {:.1f}, повернення коштує {:.1f}, резерв {:.1f} Вт·год",
                                      k, remaining, e_rtl, reserve_wh));
        }

        report.psr_waypoint   = k;
        report.psr_distance_m = dist_home;
    }
    return {};
}

}  // namespace mission
