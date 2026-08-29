// main.cpp — автономний датчик: раз на хвилину прокинутися на кілька
// мілісекунд, зміряти температуру й повернутися у Stop2 зі струмом
// одиниць мікроампер.
//
// Цінність тут не у вимірі, а в тому, що між вимірами плата справді спить:
// кожен цикл проходить повний автомат присипляння й доповідає, що по дорозі
// виглядало підозріло.
#include <chrono>
#include <cstdint>

#include "board.hpp"
#include "sleep.hpp"
#include "thermometer.hpp"

namespace {

using namespace std::chrono_literals;

constexpr std::uint8_t kSensorAddress = 0x48U;
constexpr auto kSleepInterval = 60s;

enum class Fault : std::uint32_t {
    None = 0,
    BusError = 1U << 0,
    BusStuck = 1U << 1,
    RailPowered = 1U << 2,
    FloatingPins = 1U << 3,
    ProbeAttached = 1U << 4,
    NoClock = 1U << 5
};

[[nodiscard]] constexpr std::uint32_t operator|(std::uint32_t bits, Fault fault) noexcept
{
    return bits | static_cast<std::uint32_t>(fault);
}

// Показання лягає в резервний регістр RTC: він переживає Stop2
// і не коштує ані мікроампера.
void store(sensor::Celsius sample, std::uint32_t faults) noexcept
{
    soc::rtc::backup0.store(static_cast<std::uint32_t>(
        static_cast<std::uint16_t>(sample.halfDegrees)));
    soc::rtc::backup1.store(faults);
}

[[nodiscard]] std::uint32_t measure(sensor::Celsius& sample) noexcept
{
    std::uint32_t faults = 0;

    // Живлення датчика тримає область видимості: на виході з неї лінії
    // припарковано в нуль, а ключ розімкнено — у якому б місці ми не вийшли.
    const board::SensorRail rail;

    auto bus = sensor::BusSession::open();
    if (!bus) {
        return faults | (bus.error() == sensor::BusError::Stuck ? Fault::BusStuck
                                                                : Fault::BusError);
    }

    const sensor::Thermometer thermometer{kSensorAddress};
    const auto reading = thermometer.read(*bus);
    if (reading) {
        sample = *reading;
        return faults;
    }

    faults = faults | Fault::BusError;
    if (sensor::busStuck() && !sensor::recoverBus()) {
        faults = faults | Fault::BusStuck;
    }
    return faults;
}

// Індикація вмикається лише під зондом: у полі кожен спалах — це десятки
// мікроампер·годин, яких датчик собі дозволити не може.
void report(std::uint32_t faults) noexcept
{
    if (faults == 0U || !lowpower::coresight::probeAttached()) {
        return;
    }
    for (unsigned blink = 0; blink < 3U; ++blink) {
        board::led(true);
        board::delayFor(60ms);
        board::led(false);
        board::delayFor(60ms);
    }
}

[[nodiscard]] std::uint32_t noteSleepFault(lowpower::Fault fault) noexcept
{
    switch (fault) {
    case lowpower::Fault::RailStillPowered:
        return 0U | Fault::RailPowered;
    case lowpower::Fault::FloatingPins:
        return 0U | Fault::FloatingPins;
    case lowpower::Fault::RtcTimeout:
        return 0U | Fault::NoClock;
    case lowpower::Fault::OutOfOrder:
    case lowpower::Fault::NoWakeSource:
    case lowpower::Fault::StandbyRefused:
        break;
    }
    return 0U;
}

} // namespace

int main()
{
    board::initClocks();
    board::initPins();

    // Без LSE немає чим відміряти хвилину: єдиним джерелом пробудження
    // лишається кнопка, і цикл спить до неї, а не крутиться порожнім.
    const bool haveClock = lowpower::initRtc().has_value();
    const auto interval = haveClock ? kSleepInterval : 0s;

    for (;;) {
        sensor::Celsius sample{};
        std::uint32_t faults = measure(sample);
        if (!haveClock) {
            faults = faults | Fault::NoClock;
        }

        const auto slept = lowpower::enterStop2(interval);
        if (slept) {
            if (slept->probeAttached) {
                faults = faults | Fault::ProbeAttached;
            }
            if (slept->railSuspect) {
                faults = faults | Fault::RailPowered;
            }
        } else {
            faults |= noteSleepFault(slept.error());
        }

        store(sample, faults);

        if (slept && slept->source == lowpower::WakeSource::Button) {
            board::led(true);
            board::delayFor(30ms);
            board::led(false);
        }
        report(faults);
    }
}
