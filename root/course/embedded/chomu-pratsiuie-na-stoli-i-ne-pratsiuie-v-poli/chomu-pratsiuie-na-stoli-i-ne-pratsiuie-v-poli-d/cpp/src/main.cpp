// main.cpp — польовий модуль моніторингу середовища.
//
// Порядок старту тут не випадковий: спершу з'ясувати, ЧОМУ ми взагалі
// стартували, і лише потім вмикати те, що споживає струм. Прилад, який
// піднімає радіо до читання прапорів скидання, у циклі Brownout-перезапусків
// так і не доживе до діагностики самого себе.

#include <array>
#include <chrono>
#include <optional>

#include "field/bus_guard.hpp"
#include "field/fault_log.hpp"
#include "field/platform.hpp"
#include "field/supervisor.hpp"

namespace {

using namespace std::chrono_literals;
using field::plat::Load;

constexpr std::uint8_t kSensorAddr = 0x44;  // давач вологості на зовнішній шині
constexpr std::uint8_t kSensorStatusReg = 0x00;

constexpr auto kStepPeriod = 100ms;
constexpr auto kBusCheckPeriod = 1000ms;
constexpr auto kRadioPeriod = 30'000ms;
constexpr auto kRadioBurst = 300ms;
constexpr auto kWatchdogTimeout = 4000ms;

// Стільки марних порятунків шини поспіль — і перезапускаємось цілком.
constexpr std::uint16_t kBusGiveUp = 5;

// Скидання за власним рішенням: спершу знімаємо навантаження, щоб під час
// перезапуску шина не тримала імпульс струму, і лише тоді б'ємо по AIRCR.
[[noreturn]] void controlledReset(field::FaultLog& log, const field::Supervisor& sup,
                                  std::chrono::milliseconds now) {
    field::plat::setLoad(Load::Radio, false);
    field::plat::setLoad(Load::Heater, false);
    field::plat::setLoad(Load::Charger, false);

    log.append(field::ResetCause::Software, sup.lastTemperatureC(), sup.idleMv(), sup.uptime(now));
    field::plat::delayFor(2000us);
    field::plat::systemReset();
}

}  // namespace

int main() {
    field::plat::init();

    // Сторожовий таймер піднімаємо ДО першої довгої операції: якщо
    // ініціалізація впаде на завислій шині, нас перезапустить залізо.
    field::plat::watchdogStart(kWatchdogTimeout);

    field::FaultLog log;
    const field::BootReport boot = log.open();

    const auto bootAt = field::plat::now();
    field::BusGuard bus{log, kSensorAddr};
    field::Supervisor sup{boot.needsSafeStart(), bootAt};

    // Перший запис — сам факт старту з його причиною. Температури й напруги
    // ще не знаємо, тому пишемо нулі: подія важливіша за подробиці, і саме
    // за цим рядком потім видно ланцюг нічних перезапусків.
    log.append(boot.cause, 0, 0, 0ms);

    auto nextStep = bootAt;
    auto nextBusCheck = bootAt + kBusCheckPeriod;
    auto nextRadio = bootAt + kRadioPeriod;
    auto radioUntil = bootAt;
    std::optional<field::Supervisor::RadioLease> lease;

    for (;;) {
        field::plat::watchdogKick();

        const auto now = field::plat::now();

        // --- крок політики середовища ---
        if (now >= nextStep) {
            nextStep = now + kStepPeriod;
            sup.step(field::Supervisor::measure(), now);
        }

        // --- нагляд за зовнішньою шиною ---
        if (now >= nextBusCheck) {
            nextBusCheck = now + kBusCheckPeriod;

            const field::BusHealth health = bus.check();
            if (health == field::BusHealth::Ok || health == field::BusHealth::Recovered) {
                std::array<std::uint8_t, 2> raw{};
                static_cast<void>(bus.read(kSensorStatusReg, raw));
            } else if (bus.hopelessStreak() >= kBusGiveUp) {
                // Дев'ять тактів не допомогли п'ять разів поспіль: тримає не
                // раб, а щось на платі — конденсат, дендрит, тріщина в пайці.
                // Лишився повний перезапуск із перезаливкою периферії; якщо
                // і він не поможе, наступний старт побачить лічильник
                // сторожових скидань і піде в обережний режим.
                controlledReset(log, sup, now);
            }
        }

        // --- сеанс зв'язку ---
        if (!lease && now >= nextRadio) {
            if (auto granted = sup.requestRadio(); granted) {
                lease = std::move(*granted);
                radioUntil = now + kRadioBurst;
                nextRadio = now + kRadioPeriod;
            } else {
                // Відмову не «пропускаємо» до наступного повного періоду:
                // мороз і перегрів минають за хвилини, і сеанс краще
                // спробувати раніше, ніж за півгодини.
                nextRadio = now + kRadioPeriod / 6;
            }
        }

        // Друга умова — це коли передавач зняли не ми, а крок політики через
        // просадку шини. Знищення оренди все одно проходить через супервізор:
        // він на цій парі замірів уточнює внутрішній опір джерела.
        if (lease && (now >= radioUntil || !lease->live())) {
            lease.reset();
        }
    }
}
