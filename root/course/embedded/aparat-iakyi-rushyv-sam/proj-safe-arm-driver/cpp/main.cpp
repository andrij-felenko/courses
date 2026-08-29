#include "safe_actuator.hpp"

#include <chrono>
#include <cstdint>

/*
 * Адаптер до BSP конкретної плати. Сам BSP написаний на C — звідси
 * extern "C"; далі жодного C у драйвері немає.
 */
extern "C" {
void hw_gpio_write_heartbeat(bool level);
void hw_timer_set_pwm_duty(std::uint16_t duty);
std::uint32_t hw_get_time_us(void);
std::uint16_t hw_read_supply_voltage_mv(void);
bool hw_read_estop_active(void);
bool hw_read_overtemp_flag(void);
bool hw_read_overcurrent_flag(void);
void hw_watchdog_start(std::uint16_t timeout_ms);
void hw_watchdog_feed(void);
}

namespace {

using namespace std::chrono_literals;

// Період головного циклу — коротший за півперіод меандру, інакше
// серцебиття втратить фронти ще до будь-якої аварії.
constexpr std::chrono::microseconds kCyclePeriod = 250us;

// Профіль місії: розгін до 40% за секунду, утримання, зупинка.
constexpr std::chrono::microseconds kRampTime = 1s;
constexpr std::chrono::microseconds kHoldTime = 5s;
constexpr std::uint16_t kMissionDuty = 400;

class Board {
public:
    void writeHeartbeat(bool level) { hw_gpio_write_heartbeat(level); }
    void setPwmDuty(std::uint16_t duty) { hw_timer_set_pwm_duty(duty); }

    std::chrono::microseconds now() {
        // Апаратний лічильник 32-бітний і переповнюється кожні ~71 хвилину.
        // chrono рахує різниці зі знаком, тож беззнакове «загортання» його
        // обдурило б: розширюємо лічильник до 64 бітів тут, на межі BSP.
        // Дозволено, бо цикл безпеки заходить сюди частіше за період
        // переповнення — і саме тому now() не const.
        const std::uint32_t raw = hw_get_time_us();
        if (raw < lastRaw_) {
            wrapOffset_ += std::uint64_t{1} << 32;
        }
        lastRaw_ = raw;
        return std::chrono::microseconds{
            static_cast<std::int64_t>(wrapOffset_ + raw)};
    }

    std::uint16_t supplyVoltageMv() { return hw_read_supply_voltage_mv(); }
    bool estopActive() { return hw_read_estop_active(); }
    bool overTemperature() { return hw_read_overtemp_flag(); }
    bool overCurrent() { return hw_read_overcurrent_flag(); }

    void startWatchdog(std::chrono::milliseconds window) {
        hw_watchdog_start(static_cast<std::uint16_t>(window.count()));
    }
    void feedWatchdog() { hw_watchdog_feed(); }

private:
    std::uint64_t wrapOffset_{0};
    std::uint32_t lastRaw_{0};
};

static_assert(safety::HardwarePlatform<Board>);

std::uint16_t missionDuty(std::chrono::microseconds armedFor) {
    if (armedFor >= kRampTime + kHoldTime) {
        return 0;
    }
    if (armedFor >= kRampTime) {
        return kMissionDuty;
    }
    // Лінійний розгін; рахунок у 64 бітах, бо 400 · 1e6 не влазить у 32.
    const auto scaled = static_cast<std::int64_t>(kMissionDuty) *
                        armedFor.count() / kRampTime.count();
    return static_cast<std::uint16_t>(scaled);
}

// Витримка періоду. Активне очікування чесніше за сон: цикл безпеки не
// має права заснути глибше, ніж дозволяє вікно сторожа.
void waitCycleEnd(Board &board, std::chrono::microseconds cycleStart) {
    while (board.now() - cycleStart < kCyclePeriod) {
    }
}

// Аварія незворотна: тримаємо нуль на виходах і годуємо сторожа, щоб
// причина аварії дожила до читання діагностики.
[[noreturn]] void holdSafe(safety::SafeActuator<Board> &actuator, Board &board) {
    for (;;) {
        const auto cycleStart = board.now();
        (void)actuator.update(0);
        waitCycleEnd(board, cycleStart);
    }
}

} // namespace

int main() {
    Board board;

    // Сторож стартує першим: зависла ініціалізація периферії теж має
    // закінчуватися скиданням, а не мовчанням.
    board.startWatchdog(safety::Config::watchdogWindow);

    safety::SafeActuator actuator{board};

    if (!actuator.requestArm(safety::kArmToken)) {
        holdSafe(actuator, board);
    }

    std::chrono::microseconds armedSince{0};
    bool missionStarted = false;
    bool missionDone = false;

    for (;;) {
        const auto cycleStart = board.now();
        std::uint16_t target = 0;

        if (actuator.armed()) {
            if (!missionStarted) {
                missionStarted = true;
                armedSince = cycleStart;
            }
            const auto armedFor = cycleStart - armedSince;
            if (!missionDone) {
                target = missionDuty(armedFor);
                missionDone = armedFor >= kRampTime + kHoldTime;
            }
        }

        if (!actuator.update(target)) {
            // Драйвер уже знеструмив вихід; лишається тримати стан.
            holdSafe(actuator, board);
        }

        if (missionDone && actuator.armed()) {
            actuator.disarm();
        }

        waitCycleEnd(board, cycleStart);
    }
}
