#pragma once

#include "step_metrics.hpp"

#include <string_view>

namespace pid {

/// Куди метрика впала відносно смуги норми.
enum class Band {
    Healthy,
    Watch,       ///< ще не біда, але вже не норма
    Undertuned,  ///< замале підсилення / завелика затримка
    Overtuned,   ///< надмірне підсилення
    Unknown
};

struct Bands {
    Band tau{Band::Unknown};
    Band rise{Band::Unknown};
    Band overshoot{Band::Unknown};
    Band noise{Band::Unknown};
};

enum class Tune {
    Healthy,
    SystemLaggy,
    DNoise,
    PHigh,
    DLow,
    RiseTooFast,
    PLow,
    Overdamped,
    NotSettled
};

struct Advice {
    std::string_view title;
    std::string_view action;
};

[[nodiscard]] Bands classify(const StepMetrics& m);
[[nodiscard]] Tune judge(const StepMetrics& m, const Bands& b);
[[nodiscard]] Advice adviceFor(Tune t);
[[nodiscard]] std::string_view name(Band b);

} // namespace pid
