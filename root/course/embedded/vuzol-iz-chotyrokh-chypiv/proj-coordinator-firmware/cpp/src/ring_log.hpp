#pragma once

// Кільцевий журнал у NOR Flash. Записи збираються по десять у сторінковий
// буфер, сектор попереду стирається наперед, голова кільця після
// перезавантаження шукається скануванням заголовків секторів.

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <optional>

#include "spi_flash.hpp"
#include "telemetry.hpp"

namespace node {

enum class LogError : std::uint8_t {
    NoChip,      // Flash не відповіла або відповіла чужим ID
    ReadFailed,  // скан кільця не дочитався
};

class RingLog {
public:
    using Events = EventQueue<16>;

    RingLog(SpiFlash& flash, Events& events) noexcept : flash_{flash}, events_{events} {}

    // Повертає найновіший знайдений запис — з нього триває нумерація зрізів.
    std::expected<std::optional<Record>, LogError> mount() noexcept;

    // Кладе запис у сторінковий буфер. false — попередня сторінка ще в польоті.
    bool append(const Record& rec) noexcept;

    // Крок автомата: жодного очікування, лише перевірка BUSY.
    void poll() noexcept;

    [[nodiscard]] bool idle() const noexcept {
        return state_ == State::Idle && !pagePending_;
    }
    [[nodiscard]] bool lastWriteOk() const noexcept { return lastWriteOk_; }
    [[nodiscard]] std::uint32_t records() const noexcept { return records_; }
    [[nodiscard]] std::uint32_t writeErrors() const noexcept { return writeErrors_; }
    [[nodiscard]] std::uint32_t sectorsErased() const noexcept { return sectorsErased_; }

private:
    enum class State : std::uint8_t { Idle, Programming, Erasing };

    static constexpr std::uint32_t kEraseLimitMs   = 500;   // паспортні 400 плюс запас
    static constexpr std::uint32_t kProgramLimitMs = 10;    // паспортні 3
    static constexpr std::uint32_t kPagesPerSector = kFlashSectorSize / kFlashPageSize;

    [[nodiscard]] static std::uint32_t nextSector(std::uint32_t addr) noexcept {
        return ((addr / kFlashSectorSize + 1u) % kSectorCount) * kFlashSectorSize;
    }

    bool sectorIsErased(std::uint32_t sectorAddr) noexcept;
    void beginErase(std::uint32_t sectorAddr) noexcept;
    void resetPageBuffer() noexcept;

    SpiFlash& flash_;
    Events&   events_;

    std::array<std::byte, kFlashPageSize> page_{};
    std::uint32_t writeAddr_{0};
    std::size_t   pageUsed_{0};
    std::size_t   pageRecords_{0};
    bool          pagePending_{false};

    State         state_{State::Idle};
    std::uint32_t opStartedMs_{0};

    std::uint32_t records_{0};
    std::uint32_t writeErrors_{0};
    std::uint32_t sectorsErased_{0};
    bool          lastWriteOk_{true};
    bool          mounted_{false};
};

}  // namespace node
