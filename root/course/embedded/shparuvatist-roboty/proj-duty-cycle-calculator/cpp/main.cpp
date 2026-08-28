#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <string_view>
#include <chrono>
#include <numeric>
#include <expected>

namespace embedded::power {

using namespace std::chrono_literals;

struct PowerPhase {
    std::string name;
    double current_ma{0.0};
    std::chrono::duration<double, std::milli> duration{0.0ms};
};

struct BatterySpec {
    double nominal_capacity_mah{0.0};
    double derating_factor{0.85};
};

struct DeviceProfileConfig {
    std::vector<PowerPhase> phases;
    double sleep_current_ua{0.0};
    std::chrono::seconds cycle_period{0s};
    BatterySpec battery{};
};

struct ProfileEvaluationReport {
    std::chrono::duration<double, std::milli> total_active_time{0.0ms};
    double total_active_charge_uc{0.0};
    double sleep_charge_uc{0.0};
    double avg_current_ua{0.0};
    double duty_cycle{0.0};
    double active_energy_share_pct{0.0};
    double sleep_energy_share_pct{0.0};
    double battery_lifetime_years{0.0};
    std::chrono::seconds saturation_period{0s};
};

enum class ProfileError {
    EmptyPhases,
    InvalidDuration,
    ActiveExceedsPeriod,
    InvalidBattery
};

[[nodiscard]] constexpr auto evaluate_profile(const DeviceProfileConfig& cfg) noexcept
    -> std::expected<ProfileEvaluationReport, ProfileError>
{
    if (cfg.phases.empty()) {
        return std::unexpected(ProfileError::EmptyPhases);
    }
    if (cfg.cycle_period <= 0s) {
        return std::unexpected(ProfileError::InvalidDuration);
    }
    if (cfg.battery.nominal_capacity_mah <= 0.0 || cfg.battery.derating_factor <= 0.0) {
        return std::unexpected(ProfileError::InvalidBattery);
    }

    double total_active_ms = 0.0;
    double q_on_uc = 0.0;

    for (const auto& phase : cfg.phases) {
        if (phase.duration.count() < 0.0 || phase.current_ma < 0.0) {
            return std::unexpected(ProfileError::InvalidDuration);
        }
        total_active_ms += phase.duration.count();
        /* заряд підфази в мкКл: (мА * 1000 мкА/мА) * (мс / 1000 с/мс) = мкА * с */
        q_on_uc += phase.current_ma * phase.duration.count();
    }

    const double t_on_s = total_active_ms / 1000.0;
    const double period_s = std::chrono::duration<double>(cfg.cycle_period).count();

    if (t_on_s >= period_s) {
        return std::unexpected(ProfileError::ActiveExceedsPeriod);
    }

    const double t_off_s = period_s - t_on_s;
    const double q_off_uc = cfg.sleep_current_ua * t_off_s;
    const double q_total_uc = q_on_uc + q_off_uc;

    ProfileEvaluationReport rep{};
    rep.total_active_time = std::chrono::duration<double, std::milli>(total_active_ms);
    rep.total_active_charge_uc = q_on_uc;
    rep.sleep_charge_uc = q_off_uc;
    rep.duty_cycle = t_on_s / period_s;
    rep.avg_current_ua = q_total_uc / period_s;
    rep.active_energy_share_pct = (q_on_uc / q_total_uc) * 100.0;
    rep.sleep_energy_share_pct = (q_off_uc / q_total_uc) * 100.0;

    const double eff_capacity_uah = cfg.battery.nominal_capacity_mah * cfg.battery.derating_factor * 1000.0;
    const double lifetime_hours = eff_capacity_uah / rep.avg_current_ua;
    rep.battery_lifetime_years = lifetime_hours / (24.0 * 365.25);

    if (cfg.sleep_current_ua > 0.0) {
        const double sat_s = (9.0 * q_on_uc) / cfg.sleep_current_ua;
        rep.saturation_period = std::chrono::seconds(static_cast<long long>(sat_s));
    }

    return rep;
}

void print_report(const DeviceProfileConfig& cfg, const ProfileEvaluationReport& rep) {
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "================ ЗВІТ ЕНЕРГЕТИЧНОГО ПРОФІЛЮ ================\n";
    std::cout << "Декомпозиція активного вікна (t_on = " << rep.total_active_time.count() << " мс):\n";

    size_t idx = 1;
    for (const auto& phase : cfg.phases) {
        const double q_phase = phase.current_ma * phase.duration.count();
        const double share = (q_phase / rep.total_active_charge_uc) * 100.0;
        std::cout << "  [" << idx++ << "] " << std::left << std::setw(22) << phase.name
                  << " | " << std::right << std::setw(6) << phase.current_ma << " мА"
                  << " | " << std::setw(6) << phase.duration.count() << " мс"
                  << " | " << std::setw(7) << q_phase << " мкКл ("
                  << std::setw(5) << share << " %)\n";
    }
    std::cout << "------------------------------------------------------------\n";
    std::cout << "Шпаруватість D:             " << std::setprecision(7) << rep.duty_cycle
              << " (" << std::setprecision(5) << (rep.duty_cycle * 100.0) << " %)\n";
    std::cout << std::setprecision(2);
    std::cout << "Струм сну I_sleep:          " << cfg.sleep_current_ua << " мкА\n";
    std::cout << "Середній інтегральний струм: " << rep.avg_current_ua << " мкА\n";
    std::cout << "Розподіл енергії за цикл:   Активність: " << rep.active_energy_share_pct
              << " % | Сон: " << rep.sleep_energy_share_pct << " %\n";
    std::cout << "Розрахункова автономність:  " << rep.battery_lifetime_years << " років\n";
    std::cout << "Точка насичення T_90:       " << rep.saturation_period.count() << " с ("
              << (rep.saturation_period.count() / 60) << " хв)\n";
    std::cout << "============================================================\n";
}

} // namespace embedded::power

int main() {
    using namespace embedded::power;

    const DeviceProfileConfig lora_node{
        .phases = {
            { "Кварц + PLL старт",     8.0, 1.5ms },
            { "Живлення + АЦП давача", 5.0, 3.0ms },
            { "Обробка + AES-128",    18.0, 1.2ms },
            { "Радіопередача LoRa TX",45.0, 22.0ms },
            { "Прийом квитанції RX",  11.0, 6.0ms },
            { "Перехід у глибокий сон",3.0, 0.3ms }
        },
        .sleep_current_ua = 2.8,
        .cycle_period = 600s,
        .battery = {
            .nominal_capacity_mah = 2600.0,
            .derating_factor = 0.85
        }
    };

    const auto report = evaluate_profile(lora_node);
    if (!report) {
        std::cerr << "Помилка аналізу профілю енергоспоживання\n";
        return 1;
    }

    print_report(lora_node, *report);
    return 0;
}
