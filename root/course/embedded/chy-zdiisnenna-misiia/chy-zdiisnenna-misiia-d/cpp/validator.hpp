#pragma once

#include <expected>
#include <vector>

#include "mission.hpp"
#include "power.hpp"
#include "terrain.hpp"
#include "wind.hpp"

namespace mission {

// Висота сонця над горизонтом за широтою, днем року й місцевим сонячним часом.
[[nodiscard]] float solar_elevation_deg(double latitude_deg, int day_of_year, float solar_hour) noexcept;

// Конвеєр із п'яти бар'єрів: план -> вітер -> рельєф -> енергія -> час.
// Відмова на будь-якому кроці зупиняє розрахунок і несе координату проблеми.
class Validator {
public:
    Validator(const DemGrid& dem, const Aircraft& aircraft,
              const Battery& battery, const WindProfile& wind) noexcept
        : dem_(dem), aircraft_(aircraft), battery_(battery), wind_(wind) {}

    [[nodiscard]] std::expected<Report, Rejection> run(const Plan& plan) const;

private:
    struct LegState {
        float distance_m{};
        float time_s{};
        float ground_speed_mps{};
        float energy_wh_at_end{};
    };

    [[nodiscard]] std::expected<void, Rejection> check_plan(const Plan& plan) const;
    // Заповнює psr_* у звіті або відхиляє місію, якщо точку вже пройдено.
    [[nodiscard]] std::expected<void, Rejection> check_safe_return(
        const Plan& plan, const std::vector<LegState>& legs, Report& report) const;

    const DemGrid&     dem_;
    const Aircraft&    aircraft_;
    const Battery&     battery_;
    const WindProfile& wind_;
};

}  // namespace mission
