// main.cpp — стенд секвенсера: ганяємо автомат по сценаріях і дивимось на
// переходи станів так, як дивилися б аналізатором на лінії EN і PGOOD.
#include <array>
#include <format>
#include <iostream>

#include "sequencer.hpp"
#include "sim_board.hpp"

namespace {

using power::Ms;

constexpr Ms kTick{1};
constexpr Ms kRunLimit{120};

void run(const power::sim::Scenario& scenario)
{
    power::sim::Board board{scenario};
    power::Sequencer seq{board};

    std::cout << std::format("\n=== {} ===\n", scenario.name);

    if (auto started = seq.start(); !started) {
        std::cout << std::format("  старт відхилено: {}\n",
                                 power::to_string(started.error()));
        return;
    }

    auto prev = seq.state();
    std::cout << std::format("  {:4} мс  старт -> {}\n", board.now().count(),
                             power::to_string(prev));

    for (Ms t = Ms::zero(); t < kRunLimit; t += kTick) {
        board.advance(kTick);

        const auto step = seq.tick(kTick);
        if (!step) {
            std::cout << std::format("  {:4} мс  {} -> Fault: {}\n",
                                     board.now().count(), power::to_string(prev),
                                     power::to_string(step.error()));
            break;
        }
        if (*step != prev) {
            std::cout << std::format("  {:4} мс  {} -> {}\n", board.now().count(),
                                     power::to_string(prev), power::to_string(*step));
            prev = *step;
        }
    }

    std::cout << std::format("  підсумок: {}, падінь {}\n",
                             power::to_string(seq.state()), seq.faults());
    std::cout << std::format("  витік через піни при знеструмленій периферії: {} мс\n",
                             board.leak().count());

    seq.shutdown();
}

}  // namespace

int main()
{
    static constexpr std::array scenarios{
        power::sim::Scenario{.name = "штатне підняття"},
        power::sim::Scenario{.name = "не піднявся перший ступінь", .core_rail_dead = true},
        power::sim::Scenario{.name = "не піднявся LDO шини DVDD", .io_rail_dead = true},
        power::sim::Scenario{.name = "кидок струму C_load 1000 мкФ",
                             .periph_inrush_mv = 3500},
        power::sim::Scenario{.name = "перевантаження ключа в роботі",
                             .periph_inrush_mv = 800,
                             .overcurrent_at = Ms{40}},
        power::sim::Scenario{.name = "просів вхід 12 В у роботі",
                             .periph_inrush_mv = 800,
                             .vin_collapse_at = Ms{60}},
    };

    for (const auto& scenario : scenarios) {
        run(scenario);
    }
    return 0;
}
