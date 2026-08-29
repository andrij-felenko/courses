// Стенд на хост-машині: вичерпна перевірка матриці плюс прогін сценарію
// у темпі задачі арбітра (50 Гц).
// Збірка: g++ -std=c++20 cpp/*.cpp -o failsafe

#include <cstdlib>
#include <format>
#include <iostream>
#include <string>

#include "arbiter.hpp"

namespace {

using namespace autopilot::failsafe;
using namespace std::chrono_literals;

constexpr Millis kTick{20};

/* Еталонна модель: та сама ієрархія, записана вручну ланцюжком if-else.
 * Вона навмисно не використовує decide() — інакше тест порівнював би код
 * сам із собою. */
[[nodiscard]] Action referenceAction(std::uint32_t f) noexcept {
    const bool noGnss = (f & bit(Fault::GnssGlitch)) != 0u;

    if (f & bit(Fault::AttitudeLoss)) return Action::Terminate;
    if (f & bit(Fault::Actuator))     return Action::Land;
    if (f & bit(Fault::BatteryCrit))  return Action::Land;
    if (f & bit(Fault::Geofence))     return noGnss ? Action::Land : Action::ReturnToLaunch;
    if (f & bit(Fault::BatteryLow))   return noGnss ? Action::Land : Action::ReturnToLaunch;
    if (f & bit(Fault::RcLost))       return noGnss ? Action::Land : Action::ReturnToLaunch;
    if (noGnss)                       return Action::AltHold;
    if (f & bit(Fault::GcsLost))      return Action::Warn;
    return Action::None;
}

[[nodiscard]] std::string describe(const FaultMask& mask) {
    if (mask.none()) {
        return "норма";
    }
    std::string out;
    for (std::size_t i = 0; i < kFaultCount; ++i) {
        if (mask.test(i)) {
            out += name(static_cast<Fault>(i));
            out += ' ';
        }
    }
    return out;
}

// Усі 256 комбінацій восьмибітної маски. Пороги обнуляємо: тут судиться
// ієрархія, а не таймери.
[[nodiscard]] int checkMatrix() {
    Config cfg = Config::defaults();
    cfg.debounce.fill(0ms);
    cfg.actionHold = 0ms;

    int failed = 0;
    for (std::uint32_t bits = 0; bits < (1u << kFaultCount); ++bits) {
        Arbiter arbiter{cfg};
        arbiter.preflightDone(0ms);

        const FaultMask mask{bits};
        const Action got = arbiter.update(mask, kTick);
        const Action expected = referenceAction(bits);
        if (got != expected) {
            std::cout << std::format("  {:#04x}: таблиця дала {}, еталон {} | {}\n",
                                     bits, name(got), name(expected), describe(mask));
            ++failed;
        }
    }
    std::cout << std::format("Матриця: перевірено {} комбінацій, розбіжностей {}\n",
                             1u << kFaultCount, failed);
    return failed;
}

/* Сценарій драйверів. У прошивці кожен рядок — окремий обробник
 * переривання зі своїм бітом; тут події розкладені по осі часу. */
void driversTick(FaultInbox& inbox, Millis t) {
    // GNSS ловить сузір'я перші 200 мс — це старт, а не відмова
    inbox.report(Fault::GnssGlitch, t < 200ms);
    // Провал радіоканалу 400–600 мс фільтр з'їдає; 1000–4000 — справжня втрата
    inbox.report(Fault::RcLost, (t >= 400ms && t < 600ms) || (t >= 1000ms && t < 4000ms));
    // Просадка напруги на маневрі 3000–3200 мс і справжній розряд із 6000
    inbox.report(Fault::BatteryLow, (t >= 3000ms && t < 3200ms) || t >= 6000ms);
    inbox.report(Fault::BatteryCrit, t >= 8000ms);
    inbox.report(Fault::AttitudeLoss, t >= 10000ms);
}

void runTimeline() {
    FaultInbox inbox;
    Arbiter arbiter{Config::defaults()};
    Action last = Action::None;

    std::cout << "Час, мс | дія | підтверджені відмови\n";
    for (Millis t{0}; t <= 10400ms; t += kTick) {
        driversTick(inbox, t);

        if (t == 200ms) { // калібрування завершене
            arbiter.preflightDone(t);
            std::cout << std::format("{:>7} | преполіт завершено, арбітр увімкнено\n", t.count());
        }
        if (t == 5000ms) { // оператор побачив RTL і повернув собі керування
            const bool ok = arbiter.operatorAck(t);
            std::cout << std::format("{:>7} | команда оператора: скидання фіксації → {}\n",
                                     t.count(), ok ? "прийнято" : "відхилено");
            last = arbiter.action();
        }

        const Action action = arbiter.update(inbox.snapshot(), t);
        if (action != last) {
            std::cout << std::format("{:>7} | {:<9} | {}\n",
                                     t.count(), name(action), describe(arbiter.confirmed()));
            last = action;
        }
    }

    // Після посадки й зняття з охорони фіксація знімається повністю
    arbiter.disarm();
    std::cout << std::format("  disarm → {}\n", name(arbiter.action()));
}

} // namespace

int main() {
    const int failed = checkMatrix();
    std::cout << '\n';
    runTimeline();
    return failed == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
