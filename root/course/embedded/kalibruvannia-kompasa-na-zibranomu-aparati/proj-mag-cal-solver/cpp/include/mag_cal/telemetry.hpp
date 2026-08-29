// ===========================================================================
//  mag_cal/telemetry.hpp — MAG_CAL_PROGRESS (#191) і MAG_CAL_REPORT (#192)
//
//  Заголовки MAVLink підключає тільки telemetry.cpp: решта конвеєра не
//  мусить залежати від згенерованого коду протоколу.
// ===========================================================================
#pragma once

#include <cstddef>
#include <cstdint>
#include <span>

#include "mag_cal/calibration.hpp"
#include "mag_cal/collector.hpp"

namespace mag_cal {

// Стан процедури в термінах наземної станції; перекладається в enum
// MAG_CAL_STATUS усередині telemetry.cpp.
enum class CalStatus : std::uint8_t {
    NotStarted,
    Waiting,
    Collecting,
    Solving,
    Success,
    Failed,
    BadRadius
};

class MavlinkReporter {
public:
    MavlinkReporter(std::uint8_t system_id, std::uint8_t component_id,
                    std::uint8_t compass_id) noexcept
        : system_id_{system_id}, component_id_{component_id}, compass_id_{compass_id} {}

    void next_attempt() noexcept;

    // Прогрес не частіше 5 Гц; true — кадр справді пішов у канал
    bool progress(const Collector& collector, CalStatus status,
                  std::uint32_t now_ms) noexcept;

    // Підсумок після роботи розв'язувача — рівно один кадр на спробу
    void report(const Calibration& cal, bool success, bool autosaved) noexcept;

    [[nodiscard]] std::uint8_t compass_id() const noexcept { return compass_id_; }

private:
    std::uint8_t system_id_;
    std::uint8_t component_id_;
    std::uint8_t compass_id_;
    std::uint8_t attempt_{0};
    std::uint32_t last_progress_ms_{0};
};

// Порт плати: віддає готовий кадр у телеметричний канал (радіомодем,
// USB-CDC, UDP). Черга й пріоритети — турбота транспорту, не наша.
namespace link_port {
[[nodiscard]] bool write(std::span<const std::byte> frame) noexcept;
}  // namespace link_port

}  // namespace mag_cal
