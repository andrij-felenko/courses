// supervisor.cpp — рішення про живлення й вимірювання.
#include "supervisor.hpp"

namespace app {

std::expected<bsp::EnvironmentMetrics, bsp::Status>
SystemSupervisor::read_env_retrying() noexcept
{
    bsp::Status last = bsp::Status::BusFault;

    // Стеля спроб — саме те, що ловить інжекція збоїв у хостовому тесті.
    for (unsigned attempt = 0; attempt < kEnvAttempts; ++attempt) {
        auto env = bsp_.read_environment();
        if (env) {
            env->timestamp = bsp_.uptime();
            return env;
        }
        last = env.error();
        ++env_faults_;
        bsp_.delay(kRetryPause);
    }
    return std::unexpected(last);
}

void SystemSupervisor::run_cycle() noexcept
{
    ++cycles_;
    fresh_env_ = false;
    critical_shutdown_ = false;

    const auto battery = bsp_.get_battery_metrics();
    if (!battery) {
        // Напруга невідома: сигналимо, але наосліп нічого не гасимо —
        // збій міг бути в самому АЦП, а не в батареї.
        ++battery_faults_;
        bsp_.led_set(bsp::LedId::Warning, bsp::LedState::On);
        return;
    }

    // Критичний поріг: гасимо все, що споживає, і лягаємо на годину.
    if (battery->voltage_mv < kVbatCriticalMv) {
        critical_shutdown_ = true;
        low_power_warning_ = true;
        bsp_.led_set(bsp::LedId::SystemStatus, bsp::LedState::Off);
        bsp_.led_set(bsp::LedId::Warning, bsp::LedState::On);
        bsp_.power_domain_set(bsp::PowerDomain::Radio, false);
        bsp_.power_domain_set(bsp::PowerDomain::Sensors, false);
        bsp_.enter_low_power(bsp::SleepMode::Deep, kDeepSleep);
        return;
    }

    // Попереджувальний поріг: вимірювати можна, передавати — ні.
    if (battery->voltage_mv < kVbatWarningMv) {
        low_power_warning_ = true;
        bsp_.led_set(bsp::LedId::Warning, bsp::LedState::On);
        bsp_.power_domain_set(bsp::PowerDomain::Radio, false);
    } else {
        low_power_warning_ = false;
        bsp_.led_set(bsp::LedId::Warning, bsp::LedState::Off);
        bsp_.power_domain_set(bsp::PowerDomain::Radio, true);
    }

    bsp_.led_set(bsp::LedId::SystemStatus, bsp::LedState::On);
    {
        // Вартовий сам витримає паузу стабілізації й сам знеструмить давачі.
        bsp::PowerDomainGuard sensors(bsp_, bsp::PowerDomain::Sensors, kSensorSettle);
        if (sensors.is_active()) {
            if (auto env = read_env_retrying()) {
                last_env_ = *env;
                fresh_env_ = true;
            }
        }
    }
    bsp_.led_set(bsp::LedId::SystemStatus, bsp::LedState::Off);
}

} // namespace app
