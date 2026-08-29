/*
 * Сценарій життя зв'язаного вузла на настільній машині:
 * доба без зв'язку → дельти з порушеним порядком → узгодження заліза →
 * коротке вікно радіозв'язку → дренаж буфера телеметрії.
 */
#include <cstdint>
#include <format>
#include <iostream>
#include <string_view>

#include "shadow_agent.hpp"
#include "shadow_json.hpp"

namespace {

void feedDelta(iot::ShadowAgent& agent, std::string_view doc)
{
    const auto parsed = iot::parseDelta(doc);
    if (!parsed) {
        std::cout << std::format("  {:<44} → {}\n", doc, iot::describe(parsed.error()));
        return;
    }

    const auto applied = agent.applyDelta(*parsed);
    std::cout << std::format("  {:<44} → {}\n", doc,
                             applied ? std::string_view{"прийнято"}
                                     : iot::describe(applied.error()));
}

} // namespace

int main()
{
    const iot::NodeConfig boot{.targetTemperature = 21.0F,
                               .fanSpeedRpm = 1200,
                               .heatingEnabled = true,
                               .sequenceId = 4};
    iot::ShadowAgent agent{boot};

    std::cout << "== 1. Розділення мережі: вузол у полі, каналу немає ==\n";
    for (std::uint32_t i = 0; i < 40; ++i) {
        agent.recordTelemetry(iot::TelemetryEntry{
            .timestamp = 1000 + i * 10,
            .measuredTemperature = 20.5F + 0.1F * static_cast<float>(i % 5),
            .currentPowerWatts = static_cast<std::uint16_t>(800 + i)});
    }
    std::cout << std::format("  у буфері {} звітів, затерто найстаріших {}\n",
                             agent.bufferedCount(), agent.droppedCount());

    int total = 0;
    int window = 0;
    /* Імітація вузького радіоканалу: у вікні поміщається лише кілька пакетів. */
    auto radio = [&window, &total](const iot::TelemetryEntry& entry) {
        if (window <= 0) {
            return false; /* вікно скінчилося: решта лишається в буфері */
        }
        --window;
        ++total;
        std::cout << std::format("    t={} temp={:.2f} P={} Вт{}\n", entry.timestamp,
                                 entry.measuredTemperature, entry.currentPowerWatts,
                                 entry.fromOfflineCache ? " [з буфера]" : "");
        return true;
    };

    std::cout << std::format("  спроба дренажу без зв'язку: відправлено {}\n",
                             agent.drainTelemetry(radio));

    std::cout << "\n== 2. Дельти тіні: дублі, обгін пакетів, небезпечні значення ==\n";
    feedDelta(agent, R"({"version":7,"temp":24.5})");
    feedDelta(agent, R"({"version":5,"temp":18.0})");
    feedDelta(agent, R"({"version":9,"fan":5200})");
    feedDelta(agent, R"({"version":9,"fan":2400,"heat":false})");
    feedDelta(agent, R"({"temp":30.0})");
    feedDelta(agent, R"({"version":11,"temp":ой})");
    std::cout << std::format("  відкинуто застарілих {}, поза межами {}\n",
                             agent.staleRejected(), agent.rangeRejected());

    std::cout << "\n== 3. Узгодження заліза ==\n";
    std::cout << "  дельта до застосування:" << iot::describeFields(agent.pending()) << '\n';
    std::cout << "  записано в залізо:     " << iot::describeFields(agent.reconcileHardware())
              << '\n';
    std::cout << std::format("  active: {:.1f} °C, {} об/хв, нагрів {}, версія {}\n",
                             agent.active().targetTemperature, agent.active().fanSpeedRpm,
                             agent.active().heatingEnabled ? "увімкнено" : "вимкнено",
                             agent.active().sequenceId);
    std::cout << "  залишок дельти:        " << iot::describeFields(agent.pending()) << '\n';

    std::cout << "\n== 4. Канал повернувся: звіт про стан і дренаж буфера ==\n";
    agent.setLink(iot::Link::Connected);

    if (agent.reportedDirty()) {
        std::cout << "  publish shadow/update: " << iot::buildReported(agent.reported()) << '\n';
        agent.markReportedSent();
    }

    window = 5; /* коротке вікно: модем встиг лише п'ять пакетів */
    std::cout << std::format("  вікно 1: відправлено {}, у буфері лишилось {}\n",
                             agent.drainTelemetry(radio), agent.bufferedCount());

    window = 100; /* канал стабілізувався */
    std::cout << std::format("  вікно 2: відправлено {}, у буфері лишилось {}\n",
                             agent.drainTelemetry(radio), agent.bufferedCount());

    std::cout << std::format("\n  усього доїхало в хмару: {} звітів\n", total);
    return 0;
}
