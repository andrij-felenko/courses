#include "sensor_bringup.hpp"
#include "simulated_sensor.hpp"

#include <array>
#include <format>
#include <iostream>
#include <span>
#include <string_view>

namespace {

using namespace bringup;

// Прогін одного сценарію: автомат крокує щомілісекунди, як у справжньому
// циклі диспетчера поруч з іншими драйверами.
State run_scenario(std::string_view title, SimulatedSensor::Faults faults,
                   std::span<const RegConfig> config, Millis budget)
{
    std::cout << std::format("\n=== {} ===\n", title);

    SimulatedSensor sensor{faults};
    SensorBringUp driver{sensor, Millis{0}, config};

    State prev = driver.state();
    std::cout << std::format("{:>6} мс  {}\n", 0, to_string(prev));

    for (Millis t{0}; t < budget; t += Millis{1}) {
        sensor.advance_to(t);
        driver.step(t);

        if (driver.state() != prev) {
            prev = driver.state();
            std::cout << std::format("{:>6} мс  {}\n", t.count(), to_string(prev));
        }
        if (driver.ready() || driver.fault()) {
            break;
        }
    }

    std::cout << std::format("       спроб: {}, відновлень шини: {}, SDA затиснута: {}\n",
                             driver.retries(), sensor.recoveries(),
                             sensor.sda_stuck() ? "так" : "ні");
    if (const auto reason = driver.fault()) {
        std::cout << std::format("       [FAULT-SAFE] {}\n", *reason);
    }
    return driver.state();
}

int expect(State got, State want)
{
    if (got == want) {
        std::cout << std::format("       ОК: очікували {}\n", to_string(want));
        return 0;
    }
    std::cout << std::format("       ЗБІЙ: очікували {}, дістали {}\n",
                             to_string(want), to_string(got));
    return 1;
}

// Штучна розбіжність Read-Back: у таблиці підмінено байт ODR на заборонену
// комбінацію, яку кремній не приймає.
constexpr std::array<RegConfig, 2> kForbiddenConfig{{
    {reg::RangeCtrl, 0x02, 0x0F},
    {reg::OdrFilter, 0x7F, 0x7F},
}};

}  // namespace

int main()
{
    int failures = 0;
    constexpr Millis kBudget{2000};

    failures += expect(run_scenario("Нормальний старт", {}, kDefaultConfig, kBudget),
                       State::Ready);

    // Штучний NACK: живлення зникає під час SW_RESET і повертається через 150 мс.
    failures += expect(run_scenario("Провал живлення під час SW_RESET",
                                    {.power_off_at = Millis{20}, .power_on_at = Millis{150}},
                                    kDefaultConfig, kBudget),
                       State::Ready);

    // Той самий обрив, але живлення не повертається: ліміт спроб вичерпано.
    failures += expect(run_scenario("Давач не повернувся після обриву",
                                    {.power_off_at = Millis{20}},
                                    kDefaultConfig, kBudget),
                       State::FaultSafe);

    failures += expect(run_scenario("Заборонена конфігурація (Read-Back Mismatch)", {},
                                    kForbiddenConfig, kBudget),
                       State::FaultSafe);

    // Імітація повільного POR: лабораторний блок наростає 50 мс.
    failures += expect(run_scenario("Повільне наростання V_DD (50 мс)",
                                    {.por_ramp = Millis{50}}, kDefaultConfig, kBudget),
                       State::Ready);

    std::cout << std::format("\nПідсумок: {}\n",
                             failures == 0 ? "усі сценарії пройдено" : "є розбіжності");
    return failures == 0 ? 0 : 1;
}
