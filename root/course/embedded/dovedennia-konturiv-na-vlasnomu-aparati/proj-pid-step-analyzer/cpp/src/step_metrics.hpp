#pragma once

#include "flight_log.hpp"
#include "step_finder.hpp"

#include <optional>
#include <span>

namespace pid {

/// П'ять метрик перехідного процесу плюс два свідки якості вимірювання.
/// Те, чого могло не бути в лозі, лежить в optional — нуль тут брехав би:
/// «час наростання 0 мс» і «до 90% не дотягнув» — протилежні діагнози.
struct StepMetrics {
    double amplitude{};                   ///< амплітуда сходинки, deg/s
    Millis tau{};                         ///< транспортне запізнення (вихід на 5%)
    std::optional<Millis> riseTime{};     ///< 10% → 90%
    double overshootPct{};                ///< перерегулювання першого екстремуму
    Millis settlingTime{};                ///< вхід у коридор ±5% від початку маневру
    std::optional<double> dNoiseRms{};    ///< ВЧ-залишок D-терма на плато
    int ringCrossings{};                  ///< перетини завдання після піка
    bool settled{};                       ///< чи вклався в коридор до кінця вікна
};

/// Міряє одне вікно. std::nullopt — реакції немає або відліків замало.
[[nodiscard]] std::optional<StepMetrics> measure(std::span<const Sample> log, const StepWindow& w);

/// Медіана по серії: один поганий кидок не має вирішувати вердикт.
[[nodiscard]] StepMetrics median(std::span<const StepMetrics> series);

} // namespace pid
