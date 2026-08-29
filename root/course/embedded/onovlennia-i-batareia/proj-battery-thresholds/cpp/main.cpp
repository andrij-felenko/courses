#include <array>
#include <cstdint>
#include <exception>
#include <print>
#include <string>
#include <string_view>

#include "preflight.hpp"
#include "telemetry.hpp"

// Модель плати замість справжнього заліза: комірка з ЕРС і внутрішнім
// опором, послідовний опір монтажу, тестове навантаження й backup-регістр,
// що переживає скид. Апаратний BOR моделюємо винятком: розкрутка стека
// імітує втрату RAM, а вміст backup-домену лишається.

namespace {

constexpr std::uint32_t kWiringMilliOhm = 250;   // контакти відсіку, дроти, шунт
constexpr std::uint32_t kQuiescentMa    = 20;    // споживання в спокої
constexpr std::uint32_t kTestLoadMa     = 200;   // мусить збігатися з limits.testLoadMa
constexpr std::uint16_t kBorMv          = 2700;  // апаратний поріг скиду ядра

struct Scenario {
    std::string_view name;
    bool             vbus;
    bool             tempSensorOk;
    std::int16_t     tempC;
    std::uint8_t     soc;
    std::uint16_t    ocvMv;
    std::uint16_t    cellEsrMilliOhm;
    ota::Urgency     urgency;
};

class BrownoutReset : public std::exception {
public:
    [[nodiscard]] const char* what() const noexcept override {
        return "brownout reset during pulse test";
    }
};

class SimBoard {
public:
    explicit SimBoard(const Scenario& sc) noexcept : sc_(sc) {}

    bool vbusPresent() noexcept { return sc_.vbus; }

    std::optional<std::int16_t> temperatureC() noexcept {
        if (!sc_.tempSensorOk) {
            return std::nullopt;  // NTC відвалився або I2C не відповів
        }
        return sc_.tempC;
    }

    std::optional<std::uint8_t> stateOfCharge() noexcept { return sc_.soc; }

    std::optional<std::uint16_t> railVoltageMv() noexcept {
        if (resetting_) {
            return std::nullopt;
        }
        const int mv = static_cast<int>(railMv(loadOn_ ? kQuiescentMa + kTestLoadMa : kQuiescentMa))
                     + adcNoiseMv();
        return static_cast<std::uint16_t>(mv < 0 ? 0 : mv);
    }

    void testLoad(bool on) {
        loadOn_ = on;
        if (on && railMv(kQuiescentMa + kTestLoadMa) < kBorMv) {
            // Шина провалилась нижче порогу — ядро скидається. Flash цілий:
            // жодного байта ми ще не стерли.
            loadOn_ = false;
            resetting_ = true;
            ++brownouts_;
            throw BrownoutReset{};
        }
    }

    void sleep(std::chrono::microseconds) noexcept {}  // на моделі час не тече

    std::optional<std::uint32_t> loadFaultWord() noexcept { return backup_; }

    bool storeFaultWord(std::uint32_t word) noexcept {
        if (resetting_) {
            return false;  // ядро вже в скиді, запис не доходить
        }
        backup_ = word;
        return true;
    }

    // Перезавантаження: RAM чиста, backup-домен незайманий.
    void reboot() noexcept {
        loadOn_ = false;
        resetting_ = false;
    }

    [[nodiscard]] unsigned brownouts() const noexcept { return brownouts_; }

private:
    [[nodiscard]] std::uint16_t railMv(std::uint32_t loadMa) const noexcept {
        const std::uint32_t rTotal = sc_.cellEsrMilliOhm + kWiringMilliOhm;
        const std::uint32_t drop = rTotal * loadMa / 1000u;
        return drop >= sc_.ocvMv ? std::uint16_t{0}
                                 : static_cast<std::uint16_t>(sc_.ocvMv - drop);
    }

    // Детермінований шум АЦП ±4 мВ — саме через нього ми усереднюємо відліки.
    int adcNoiseMv() noexcept {
        rng_ = rng_ * 1664525u + 1013904223u;
        return static_cast<int>((rng_ >> 16) % 9u) - 4;
    }

    const Scenario& sc_;
    bool            loadOn_ = false;
    bool            resetting_ = false;
    std::uint32_t   backup_ = 0;
    std::uint32_t   rng_ = 0x1234;
    unsigned        brownouts_ = 0;
};

static_assert(ota::PowerHal<SimBoard>);

void printDiagnostics(const ota::Diagnostics& diag, const ota::SafetyLimits& limits)
{
    if (diag.tempC) {
        std::println("    температура: {} °C", *diag.tempC);
    }
    if (diag.socPercent) {
        std::println("    заряд: {} %", *diag.socPercent);
    }
    if (diag.idleMv) {
        std::println("    напруга спокою: {} мВ", *diag.idleMv);
    }
    if (diag.pulse) {
        std::println("    під навантаженням: {} мВ, опір {} мОм, прогноз {} мВ (бар'єр {} мВ)",
                     diag.pulse->loadMv, diag.pulse->esrMilliOhm,
                     diag.pulse->forecastMv, limits.safeFloorMv());
    }
    if (diag.powerFaults > 0) {
        std::println("    зривів живлення в латчі: {}", diag.powerFaults);
    }
}

void printVerdict(const ota::Verdict& verdict, const ota::SafetyLimits& limits)
{
    if (verdict) {
        const auto& allow = *verdict;
        if (allow.externalPower) {
            std::println("  дозволено (зовнішнє живлення)");
        } else if (allow.throttle) {
            std::println("  дозволено (пом'якшений режим): CPU {} МГц, SPI {} МГц, TX {:+} dBm",
                         allow.throttle->cpuMhz, allow.throttle->spiMhz,
                         static_cast<int>(allow.throttle->txDbm));
        } else {
            std::println("  дозволено (батарея в нормі)");
        }
        printDiagnostics(allow.diag, limits);
        return;
    }

    const auto& denial = verdict.error();
    std::println("  відмова: {}", ota::name(denial.reason));
    printDiagnostics(denial.diag, limits);

    const auto report = ota::summarize(denial, limits);
    std::println("    телеметрія: {}, retry-after {} с{}",
                 ota::name(report.code), report.retryAfter.count(),
                 report.serviceRequired ? ", потрібен виїзд техніка" : "");

    std::array<std::byte, 64> buffer{};
    const auto packet = ota::encode(denial, limits, buffer);
    if (!packet) {
        std::println("    телеметрія не вмістилась у буфер");
        return;
    }
    std::string hex;
    for (std::byte b : *packet) {
        hex += std::format(" {:02X}", std::to_integer<unsigned>(b));
    }
    std::println("    пакет:{}", hex);
}

constexpr std::array kScenarios{
    Scenario{"мережевий адаптер увімкнено",             true,  true,  24, 62, 4050,  120, ota::Urgency::Routine},
    Scenario{"свіжа комірка, кімнатна температура",     false, true,  22, 88, 3950,   90, ota::Urgency::Routine},
    Scenario{"комірка на морозі",                       false, true,  -2, 71, 3800,  400, ota::Urgency::Routine},
    Scenario{"паливомір показує 28 %",                  false, true,  20, 28, 3600,  150, ota::Urgency::Routine},
    Scenario{"зношена комірка, планове оновлення",      false, true,  12, 47, 3180,  950, ota::Urgency::Routine},
    Scenario{"та сама комірка, критичний патч безпеки", false, true,  12, 47, 3180,  950, ota::Urgency::EmergencySecurityFix},
    Scenario{"комірка провалює вже тестовий імпульс",   false, true,   8, 46, 2960, 1500, ota::Urgency::Routine},
    Scenario{"термодавач не відповідає",                false, false,  0, 80, 3900,  120, ota::Urgency::Routine},
};

}  // namespace

int main()
{
    const ota::SafetyLimits limits{};

    for (const auto& scenario : kScenarios) {
        std::println("=== {} ===", scenario.name);

        SimBoard board{scenario};
        ota::PreflightGate gate{board, limits};

        for (unsigned attempt = 1; attempt <= 8; ++attempt) {
            try {
                printVerdict(gate.evaluate(scenario.urgency), limits);
                break;
            } catch (const BrownoutReset&) {
                std::println("  [спроба {}] BOR під час тестового імпульсу — "
                             "перезавантаження у стару прошивку", attempt);
                board.reboot();
            }
        }

        if (board.brownouts() > 0) {
            std::println("  зривів живлення на цій платі: {}", board.brownouts());
        }
        std::println("");
    }

    return 0;
}
