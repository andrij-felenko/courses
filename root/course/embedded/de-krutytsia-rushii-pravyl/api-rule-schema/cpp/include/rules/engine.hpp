// Рушій правил: умови, дії, програмні таймери, оренда керування від хаба
// й режим блокування аварії.
#pragma once

#include "rules/schema.hpp"

#include <array>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>

namespace rules {

// Мітка часу з відніманням, що переживає переповнення systick.
struct Timestamp {
    std::uint32_t ms{};
    constexpr std::uint32_t since(Timestamp older) const noexcept { return ms - older.ms; }
};

struct SoftTimer {
    bool          armed{false};
    Timestamp     start{};
    std::uint32_t durationMs{0};
};

// RAII-критична секція: підміна таблиці не має рватися перериванням.
class InterruptLock {
public:
    InterruptLock() noexcept;
    ~InterruptLock() noexcept;
    InterruptLock(const InterruptLock&) = delete;
    InterruptLock& operator=(const InterruptLock&) = delete;

private:
    std::uint32_t saved_{0};
};

class RuleEngine {
public:
    RuleEngine(std::uint32_t hubLeaseMs, Timestamp now) noexcept;

    void         setSensor(std::uint8_t reg, std::int32_t value) noexcept;
    std::int32_t read(std::uint8_t reg) const noexcept;

    // Запис від хаба: давачі й таймери недоступні, заблоковані регістри теж.
    std::expected<void, RuleError> remoteWrite(std::uint8_t reg, std::int32_t value) noexcept;

    void hubHeartbeat(Timestamp now) noexcept;
    void tick(Timestamp now) noexcept;
    void resetAlarm() noexcept;

    // Перевірка + атомарна фіксація нової таблиці.
    std::expected<void, RuleError> install(std::span<const RuleDescriptor> table) noexcept;
    std::expected<void, RuleError> validate(std::span<const RuleDescriptor> table) const noexcept;

    std::size_t ruleCount() const noexcept { return count_; }
    bool inEmergency() const noexcept { return emergency_; }
    bool inFallback() const noexcept { return fallback_; }
    bool anyLatched() const noexcept { return latched_ != 0; }

private:
    bool writeRegister(std::uint8_t reg, std::int32_t value) noexcept;
    std::optional<std::size_t> timerSlot(std::uint8_t reg) noexcept;
    void mirrorTimers(Timestamp now) noexcept;
    bool evalCondition(const RuleDescriptor& r, Timestamp now) noexcept;
    void applyAction(const RuleDescriptor& r) noexcept;
    void undoAction(const RuleDescriptor& r) noexcept;
    void evalRule(std::size_t slot, Timestamp now) noexcept;
    void enterEmergency() noexcept;

    std::array<std::int32_t, kTotalRegisters>  regs_{};
    std::array<RuleDescriptor, kMaxRules>      rules_{};
    std::array<SoftTimer, kTimerCount>         timers_{};
    std::array<bool, kTotalRegisters>          inhibited_{};
    std::size_t   count_{0};
    std::uint32_t latched_{0};
    std::uint32_t fired_{0};
    bool          emergency_{false};
    bool          fallback_{false};
    std::uint32_t hubLeaseMs_{0};
    Timestamp     lastEval_{};
};

}  // namespace rules
