#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

#include "battery.hpp"
#include "gimbals.hpp"
#include "hal.hpp"
#include "protocol.hpp"

namespace console {

struct HudSnapshot {
    std::uint16_t packMillivolts{};
    BatteryMonitor::Level batteryLevel{BatteryMonitor::Level::Ok};
    std::uint8_t linkQuality{};
    std::uint16_t lostFrames{};
    bool armed{};
    Fault faults{Fault::None};
    Telemetry air{};
};

// Рядок екрана збирається без printf: форматування плаваючою комою в циклі
// реального часу коштує більше, ніж уся телеметрія разом.
class TextLine {
public:
    void clear() noexcept { used_ = 0; }
    void append(std::string_view text) noexcept;
    void append(char symbol) noexcept;
    void appendNumber(std::uint32_t value, int minDigits = 1) noexcept;
    void appendMillivolts(std::uint16_t millivolts) noexcept;

    [[nodiscard]] std::string_view view() const noexcept { return {buffer_.data(), used_}; }

private:
    std::array<char, 24> buffer_{};
    std::size_t used_{};
};

class Hud {
public:
    void update(const HudSnapshot& snapshot) noexcept { snapshot_ = snapshot; }

    // Рендерить і віддає рівно одну сторінку за виклик: вісім викликів —
    // повний екран.
    void servicePage() noexcept;

private:
    void buildLine(std::uint8_t page, TextLine& line) const noexcept;
    void renderText(std::string_view text) noexcept;
    void renderBar(std::uint8_t percent) noexcept;

    HudSnapshot snapshot_{};
    std::uint8_t page_{};
    // Сторінка їде в дисплей теж через DMA — буфер вирівняний під рядок кешу.
    alignas(32) std::array<std::byte, hal::kLcdCols> columns_{};
};

}   // namespace console
