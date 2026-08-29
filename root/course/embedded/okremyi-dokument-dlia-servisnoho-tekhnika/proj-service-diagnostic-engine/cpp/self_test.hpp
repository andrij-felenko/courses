// self_test.hpp — самотестування вузлів плати (BIST).
#pragma once

#include <cstdint>
#include <expected>

#include "hw_port.hpp"

namespace diag {

enum class BusError : std::uint8_t {
    Busy,        // шину тримає інша задача
    StuckLow,    // лінію прибито до нуля, відновлення не допомогло
    Timeout,     // ведений розтягнув такт понад бюджет
    NoAck,       // адресат не відгукнувся
};

struct Report {
    bool          busFree{false};
    bool          rtcOk{false};
    bool          eepromOk{false};
    std::uint16_t adcRaw{0};
    std::uint16_t adcMilliVolts{0};
};

inline constexpr hw::Millis ProbeTimeout{5};   // бюджет однієї спроби
inline constexpr hw::Millis BusLockTimeout{20};

// Пробник одного адресата: зациклитись не може за побудовою.
std::expected<void, BusError> probe(std::uint8_t address7) noexcept;

// Повний прохід BIST. Помилка означає, що тест не робився взагалі.
std::expected<Report, BusError> runBist() noexcept;

} // namespace diag
