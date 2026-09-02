#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <vector>

#include "hardware.hpp"

namespace cart {

struct Record {
    static constexpr std::size_t kSize = 24;

    Millis        stamp{0};
    std::uint8_t  event{0};
    bool          critical{false};
    std::uint16_t count{0};   // скільки сирих семплів згорнуто в цю пачку
    float min{0.0f};
    float max{0.0f};
    float avg{0.0f};
    float rms{0.0f};

    [[nodiscard]] std::array<std::byte, kSize> encode() const noexcept;
    [[nodiscard]] static std::optional<Record> decode(std::span<const std::byte, kSize> raw) noexcept;
};

inline constexpr std::size_t kSlotsPerSector = kSectorSize / Record::kSize;
inline constexpr std::size_t kCrashSectors   = 3;
inline constexpr std::size_t kRingSectors    = kSectorCount - kCrashSectors;
inline constexpr std::size_t kRingSlots      = kRingSectors * kSlotsPerSector;
inline constexpr std::size_t kCrashSlots     = kCrashSectors * kSlotsPerSector;

inline constexpr Millis kSamplePeriod    = 20ms;
inline constexpr int    kPreErasePercent = 80;
inline constexpr std::uint8_t kEventSample = 0x10;

// Чорна скринька у Flash. Кільце секторів приймає рутинну телеметрію й
// затирається по колу; окремий пул наприкінці мікросхеми тримає критичні
// події, і кільце туди не дотягується ніколи.
class BlackBox {
public:
    struct Stats {
        std::uint32_t written{0};
        std::uint32_t overwritten{0};
        std::uint32_t dropped{0};
        std::uint32_t blockingErases{0};
    };

    explicit BlackBox(Board& board);

    void sample(Millis t, float value, Millis offline);
    void event(Millis t, std::uint8_t code, bool critical);
    void backgroundErase();
    std::size_t drain(std::size_t budgetBytes);

    [[nodiscard]] std::size_t pending() const noexcept { return writeIdx_ - readIdx_; }
    [[nodiscard]] std::vector<Record> crashRecords() const;
    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }

private:
    void ringPut(const Record& r);
    void crashPut(const Record& r);
    void discardSector(std::size_t sector);
    std::size_t scanCrashPool();

    Board& board_;
    std::size_t writeIdx_{0};
    std::size_t readIdx_{0};
    std::size_t crashIdx_{0};
    std::array<bool, kSectorCount> dirty_{};
    std::optional<std::size_t> preErase_{};

    Millis        windowStart_{0};
    std::uint16_t windowCount_{0};
    float wMin_{0.0f};
    float wMax_{0.0f};
    float wSum_{0.0f};
    float wSq_{0.0f};

    Stats stats_{};
};

}  // namespace cart
