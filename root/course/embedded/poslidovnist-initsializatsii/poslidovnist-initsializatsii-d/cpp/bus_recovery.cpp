#include <chrono>

#include "sensor.hpp"

namespace bringup {
namespace {
using namespace std::chrono_literals;

constexpr int kRecoveryClocks = 9;
constexpr auto kHalfPeriod = 5us;      // пів-період ручного тактування, ~100 кГц
constexpr auto kDischarge = 50ms;      // розряд декаплінгу, інакше POR не спрацює
constexpr auto kRebootWait = 40ms;     // t_ramp + t_boot після повернення живлення
constexpr auto kNrstWait = 10ms;
}  // namespace

// Ведений, збитий завадою посеред байта, тримає SDA у нулі й блокує всю шину.
// Сила удару наростає, і кожен наступний крок робиться лише тоді, коли
// попередній не допоміг.
void recover_bus(platform::PowerRail& rail, std::uint8_t dev) {
    {
        platform::GpioTakeover pins;  // виводи повернуться периферії на виході з блоку
        pins.sda(true);               // відпускаємо SDA: тепер її тримає лише ведений

        for (int i = 0; i < kRecoveryClocks && !pins.sda_is_high(); ++i) {
            pins.scl(false);
            platform::sleep(kHalfPeriod);
            pins.scl(true);
            platform::sleep(kHalfPeriod);
        }

        if (pins.sda_is_high()) {
            // Явна умова STOP: SDA 0 -> 1 при високому SCL
            pins.sda(false);
            platform::sleep(kHalfPeriod);
            pins.scl(true);
            platform::sleep(kHalfPeriod);
            pins.sda(true);
            platform::sleep(kHalfPeriod);
            return;
        }
    }

    if (platform::has_nrst(dev)) {
        platform::pulse_nrst(dev);
        platform::sleep(kNrstWait);
        return;
    }
    rail.cycle(kDischarge, kRebootWait);
}

}  // namespace bringup
