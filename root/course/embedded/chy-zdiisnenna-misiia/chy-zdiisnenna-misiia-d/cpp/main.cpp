// Сценарій зі статті: 18 км над горбистим плато, вихід із попутним вітром
// і повернення проти нього. Той самий план проганяємо за трьох умов.

#include <cmath>
#include <format>
#include <iostream>

#include "validator.hpp"

namespace {

constexpr double kHomeLat = 49.0000;
constexpr double kHomeLon = 24.0000;

// Синтетичне підвікно рельєфу: плато 300 м і гряда 560 м поперек маршруту.
mission::DemGrid build_dem()
{
    constexpr double lat0 = 48.9800;
    constexpr double lon0 = 23.9700;
    constexpr double cell = 0.0020;   // ~222 м
    constexpr std::size_t side = 64;

    mission::DemGrid dem({lat0, lon0, 0.0f}, cell, side, side, 28.5f);

    for (std::size_t r = 0; r < side; ++r) {
        const double lat   = lat0 + cell * static_cast<double>(r);
        const double d     = (lat - 49.0450) / 0.0120;   // гряда з центром на 49.045
        const auto   ridge = static_cast<float>(260.0 * std::exp(-d * d));

        for (std::size_t c = 0; c < side; ++c) {
            dem.set_elevation(r, c, 300.0f + ridge);
        }
    }
    return dem;
}

mission::Plan build_plan(float cruise_msl_m)
{
    using mission::Waypoint;

    mission::Plan plan;
    plan.waypoints = {
        Waypoint{{kHomeLat, kHomeLon, 360.0f}, 15.0f, 0.0f, false},
        Waypoint{{49.0400, kHomeLon, cruise_msl_m}, 15.0f, 0.0f, true},
        Waypoint{{49.0800, kHomeLon, cruise_msl_m}, 15.0f, 60.0f, true},
        Waypoint{{kHomeLat, kHomeLon, 380.0f}, 15.0f, 0.0f, false},
    };
    plan.limits.site_latitude_deg = kHomeLat;
    return plan;
}

void print_outcome(std::string_view title,
                   const std::expected<mission::Report, mission::Rejection>& outcome)
{
    std::cout << std::format("=== {}\n", title);

    if (!outcome) {
        const auto& rejection = outcome.error();
        std::cout << std::format("    вердикт        : NO-GO — {}\n", mission::describe(rejection.reason));
        std::cout << std::format("    подробиця      : {}\n\n", rejection.detail);
        return;
    }

    const auto& r = *outcome;
    std::cout << "    вердикт        : GO — місія здійсненна\n";
    std::cout << std::format("    маршрут        : {:.0f} м, час {:.0f} с ({:.1f} хв)\n",
                             r.total_distance_m, r.total_time_s, r.total_time_s / 60.0f);
    std::cout << std::format("    мін. шляхова   : {:.1f} м/с, мін. кліренс {:.0f} м\n",
                             r.min_ground_speed_mps, r.min_clearance_m);
    std::cout << std::format("    енергія        : {:.1f} Вт·год з {:.1f} доступних (пік {:.0f} Вт / {:.1f} А)\n",
                             r.total_energy_wh, r.usable_energy_wh, r.peak_power_w, r.peak_current_a);
    std::cout << std::format("    резерв         : {:.1f}%, сонце (мін.) {:.1f}°\n",
                             r.reserve_left_pct, r.min_sun_elevation_deg);
    std::cout << std::format("    PSR            : точка {}, {:.0f} м від дому\n\n",
                             r.psr_waypoint, r.psr_distance_m);
}

}  // namespace

int main()
{
    const mission::DemGrid dem = build_dem();

    // Літак: маса 4.5 кг, крило 0.45 м², розмах 1.7 м.
    const mission::Aircraft aircraft{mission::Aircraft::Spec{}};
    // 6S Li-Ion, 5.2 А·год, холодний ранок.
    const mission::Battery battery{mission::Battery::Spec{}};

    const float rho = mission::air_density(700.0f);
    if (const auto endurance = aircraft.best_endurance_speed(rho)) {
        std::cout << std::format("Опорні швидкості на 700 м: тривалість {:.1f} м/с, дальність {:.1f} м/с\n\n",
                                 *endurance, aircraft.best_range_speed(rho).value_or(0.0f));
    }

    // 1. Помірний вітер із півдня: вихід попутний, повернення зустрічне.
    const mission::WindProfile calm{3.0f, 180.0f, 10.0f, 0.22f};
    print_outcome("Вітер 3 м/с біля землі",
                  mission::Validator{dem, aircraft, battery, calm}.run(build_plan(700.0f)));

    // 2. Той самий план, вітер удвічі сильніший — на висоті це вже 12 м/с.
    const mission::WindProfile strong{6.0f, 180.0f, 10.0f, 0.22f};
    std::cout << std::format("Вітер на висоті 400 м: {:.1f} м/с (біля землі {:.1f})\n",
                             strong.at_height(400.0f), strong.speed_mps);
    print_outcome("Вітер 6 м/с біля землі",
                  mission::Validator{dem, aircraft, battery, strong}.run(build_plan(700.0f)));

    // 3. Помірний вітер, але низький ешелон: гряда 560 м посеред маршруту.
    print_outcome("Ешелон 480 м над гряддям 560 м",
                  mission::Validator{dem, aircraft, battery, calm}.run(build_plan(480.0f)));

    return 0;
}
