// --- supervisor.cpp ---
#include "supervisor.hpp"

namespace app {

void SystemSupervisor::run_cycle() noexcept {
    auto bat_res = bsp_.get_battery_metrics();
    if (!bat_res.has_value()) {
        bsp_.led_set(bsp::LedId::Warning, bsp::LedState::On);
        return;
    }

    const auto& bat = bat_res.value();

    // Критичний поріг розряду (3000 мВ): аварійний сон
    if (bat.voltage_mv < 3000) {
        is_critical_shutdown_ = true;
        bsp_.led_set(bsp::LedId::SystemStatus, bsp::LedState::Off);
        bsp_.led_set(bsp::LedId::Warning, bsp::LedState::On);
        bsp_.power_domain_set(bsp::PowerDomain::Sensors, false);
        bsp_.enter_low_power(bsp::SleepMode::Deep, std::chrono::hours(1));
        return;
    }

    // Попереджувальний поріг розряду (3300 мВ)
    if (bat.voltage_mv < 3300) {
        is_low_power_warning_ = true;
        bsp_.led_set(bsp::LedId::Warning, bsp::LedState::On);
    } else {
        is_low_power_warning_ = false;
        bsp_.led_set(bsp::LedId::Warning, bsp::LedState::Off);
    }

    // Штатний цикл вимірювання з використанням RAII-гарантії живлення
    bsp_.led_set(bsp::LedId::SystemStatus, bsp::LedState::On);
    {
        bsp::PowerDomainGuard sensor_power(bsp_, bsp::PowerDomain::Sensors);
        if (sensor_power.is_active()) {
            auto env_res = bsp_.read_environment();
            // Обробка отриманих даних env_res...
        }
    }
    bsp_.led_set(bsp::LedId::SystemStatus, bsp::LedState::Off);
}

} // namespace app
