#pragma once

#include "telemetry.hpp"

#include <span>

namespace postmortem {

// Скан усього запису рухомим вікном 300 мс. Повертає ПЕРШУ за часом сигнатуру:
// саме вона й є першопричиною, решта подій — уже наслідки падіння.
[[nodiscard]] Report analyze_incident(std::span<const Frame> frames);

} // namespace postmortem
