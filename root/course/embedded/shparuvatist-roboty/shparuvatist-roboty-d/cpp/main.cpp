#include <iostream>
#include <iomanip>
#include <chrono>
#include <expected>
#include <string_view>

namespace power {

using namespace std::chrono_literals;

struct DutyConfig {
    double active_current_ma{0.0};
    std::chrono::milliseconds active_time{0ms};
    double sleep_current_ua{0.0};
    std::chrono::seconds period{0s};
    double battery_capacity_mah{0.0};
    double battery_derating{0.85};
};

struct DutyMetrics {
    double duty_cycle{0.0};
    double avg_current_ua{0.0};
    double active_energy_pct{0.0};
    double sleep_energy_pct{0.0};
    double lifetime_years{0.0};
    std::chrono::seconds saturation_period{0s};
};

enum class ProfileError {
    InvalidDuration,
    ActiveExceedsPeriod,
    ZeroCapacity
};

[[nodiscard]] constexpr auto analyze_profile(const DutyConfig& cfg) noexcept 
    -> std::expected<DutyMetrics, ProfileError> 
{
    if (cfg.period <= 0s || cfg.active_time <= 0ms) {
        return std::unexpected(ProfileError::InvalidDuration);
    }

    const double t_on_s = std::chrono::duration<double>(cfg.active_time).count();
    const double period_s = std::chrono::duration<double>(cfg.period).count();

    if (t_on_s > period_s) {
        return std::unexpected(ProfileError::ActiveExceedsPeriod);
    }
    if (cfg.battery_capacity_mah <= 0.0) {
        return std::unexpected(ProfileError::ZeroCapacity);
    }

    const double t_off_s = period_s - t_on_s;
    const double i_on_ua = cfg.active_current_ma * 1000.0;
    const double q_on = i_on_ua * t_on_s;
    const double q_off = cfg.sleep_current_ua * t_off_s;
    const double q_total = q_on + q_off;

    DutyMetrics m{};
    m.duty_cycle = t_on_s / period_s;
    m.avg_current_ua = q_total / period_s;
    m.active_energy_pct = (q_on / q_total) * 100.0;
    m.sleep_energy_pct = (q_off / q_total) * 100.0;

    const double eff_cap_uah = cfg.battery_capacity_mah * cfg.battery_derating * 1000.0;
    const double lifetime_hours = eff_cap_uah / m.avg_current_ua;
    m.lifetime_years = lifetime_hours / (24.0 * 365.25);

    if (cfg.sleep_current_ua > 0.0) {
        const double sat_s = 9.0 * (i_on_ua / cfg.sleep_current_ua) * t_on_s;
        m.saturation_period = std::chrono::seconds(static_cast<long long>(sat_s));
    }

    return m;
}

} // namespace power

int main() {
    constexpr power::DutyConfig config{
        .active_current_ma = 45.0,
        .active_time = 15ms,
        .sleep_current_ua = 3.2,
        .period = 300s,
        .battery_capacity_mah = 2400.0,
        .battery_derating = 0.85
    };

    const auto result = power::analyze_profile(config);
    if (!result) {
        std::cerr << "Помилка розрахунку профілю живлення\n";
        return 1;
    }

    const auto& m = *result;
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Шпаруватість D:        " << (m.duty_cycle * 100.0) << " %\n";
    std::cout << "Середній струм:        " << m.avg_current_ua << " мкА\n";
    std::cout << "Розподіл заряду:       Активний = " << m.active_energy_pct 
              << " %, Сон = " << m.sleep_energy_pct << " %\n";
    std::cout << "Термін автономності:   " << m.lifetime_years << " років\n";
    std::cout << "Точка насичення T_90:  " << m.saturation_period.count() << " с ("
              << (m.saturation_period.count() / 60) << " хв)\n";

    return 0;
}
