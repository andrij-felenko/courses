#include <array>
#include <chrono>
#include <print>

#include "power_guard.hpp"
#include "sensor.hpp"

int main() {
    using namespace std::chrono_literals;
    platform::sim_reset_board();

    platform::I2cBus bus;
    platform::PowerRail rail;

    // Найповільніший чип на лінії: t_ramp + t_boot + запас
    bringup::PowerGuard guard{rail, 40ms};
    std::println("== підйом периферії ==");
    guard.power_on();

    // Поки піднімається живлення, процесор працює: годує watchdog, крутить цикл
    unsigned idle_ticks = 0;
    while (!guard.ready()) {
        platform::watchdog_kick();
        ++idle_ticks;
        platform::sleep(1ms);
    }
    std::println("живлення на режимі на {} мс, головний цикл провернувся {} разів",
                 platform::Clock::now().time_since_epoch().count(), idle_ticks);

    std::array devices{
        bringup::Sensor{bus, rail, 0x6A, "гіроскоп польотного контролера", true},
        bringup::Sensor{bus, rail, 0x6B, "давач вологості", false},
    };

    bool need_safe_state = false;
    for (auto& device : devices) {
        std::println("\n-- {} (адреса 0x{:02X})", device.name(), device.address());

        const auto result = device.bring_up();
        if (result) {
            const auto drdy = device.data_ready();
            std::println("   готовий зі спроби {}, DRDY={}", device.attempts(),
                         drdy.value_or(false));
            continue;
        }
        std::println("   ВІДМОВА після {} спроб: {}", device.attempts(),
                     bringup::to_string(result.error().error));

        if (device.critical()) {
            need_safe_state = true;
        } else {
            // Некритичний давач: відліки маркуються невалідними, виріб працює далі
            platform::fault_led(true);
            std::println("   некритичний: дані позначено невалідними, робота триває");
        }
    }

    if (need_safe_state) {
        platform::disable_actuators();
        platform::fault_led(true);
        std::println("\nКРИТИЧНИЙ давач не піднявся: приводи заблоковано, безпечний стан");
        return 1;
    }

    std::println("\nсистема в штатному режимі на {} мс",
                 platform::Clock::now().time_since_epoch().count());
    return 0;
}
