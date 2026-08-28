// --- test_supervisor_host.cpp: GoogleTest сумісний набір тестів ---
#include "supervisor.hpp"
#include <iostream>
#include <cassert>

namespace bsp {

class MockBoardSupport final : public IBoardSupport {
public:
    uint16_t voltage_mv{3800};
    LedState warn_led{LedState::Off};
    LedState status_led{LedState::Off};
    bool sensors_powered{false};
    bool sleep_entered{false};

    Status init() noexcept override { return Status::Ok; }
    Status deinit() noexcept override { return Status::Ok; }

    Status led_set(LedId led, LedState state) noexcept override {
        if (led == LedId::Warning) warn_led = state;
        if (led == LedId::SystemStatus) status_led = state;
        return Status::Ok;
    }
    Status led_toggle(LedId led) noexcept override {
        if (led == LedId::Warning) warn_led = (warn_led == LedState::On ? LedState::Off : LedState::On);
        return Status::Ok;
    }

    Status power_domain_set(PowerDomain domain, bool enable) noexcept override {
        if (domain == PowerDomain::Sensors) sensors_powered = enable;
        return Status::Ok;
    }

    std::expected<BatteryMetrics, Status> get_battery_metrics() noexcept override {
        BatteryMetrics m;
        m.voltage_mv = voltage_mv;
        return m;
    }

    std::expected<EnvironmentMetrics, Status> read_environment() noexcept override {
        EnvironmentMetrics e;
        e.temperature_centi_c = 2250;
        return e;
    }

    Status enter_low_power(SleepMode, std::chrono::milliseconds) noexcept override {
        sleep_entered = true;
        return Status::Ok;
    }

    std::chrono::milliseconds get_uptime() const noexcept override {
        return std::chrono::milliseconds(1000);
    }
    void delay(std::chrono::microseconds) const noexcept override {}
};

} // namespace bsp

int main() {
    bsp::MockBoardSupport mock;
    app::SystemSupervisor supervisor(mock);

    // Сценарій 1: Нормальна робота
    mock.voltage_mv = 3700;
    supervisor.run_cycle();
    assert(!supervisor.is_low_power_warning());
    assert(mock.warn_led == bsp::LedState::Off);
    assert(!mock.sleep_entered);
    std::cout << "[PASS] C++ Supervisor: Normal Mode\n";

    // Сценарій 2: Попередження про низький заряд
    mock.voltage_mv = 3150;
    supervisor.run_cycle();
    assert(supervisor.is_low_power_warning());
    assert(mock.warn_led == bsp::LedState::On);
    assert(!mock.sleep_entered);
    std::cout << "[PASS] C++ Supervisor: Low Power Warning\n";

    // Сценарій 3: Критичний розряд та глибокий сон
    mock.voltage_mv = 2850;
    supervisor.run_cycle();
    assert(supervisor.is_critical_shutdown());
    assert(!mock.sensors_powered);
    assert(mock.sleep_entered);
    std::cout << "[PASS] C++ Supervisor: Critical Deep Sleep\n";

    std::cout << "\nУсі тести C++ успішно виконано на хостовому ПК!\n";
    return 0;
}
