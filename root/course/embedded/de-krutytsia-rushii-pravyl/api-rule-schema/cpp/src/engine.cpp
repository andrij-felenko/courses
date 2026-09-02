#include "rules/engine.hpp"

#include <algorithm>

namespace rules {

// ── критична секція ─────────────────────────────────────────────────────
#if defined(__ARM_ARCH) && defined(__GNUC__)
InterruptLock::InterruptLock() noexcept {
    __asm volatile("mrs %0, primask" : "=r"(saved_));
    __asm volatile("cpsid i" ::: "memory");
}
InterruptLock::~InterruptLock() noexcept {
    if ((saved_ & 1u) == 0u) { __asm volatile("cpsie i" ::: "memory"); }
}
#else
InterruptLock::InterruptLock() noexcept = default;   // хостова збірка прикладу
InterruptLock::~InterruptLock() noexcept = default;
#endif

std::string_view describe(RuleError err) noexcept {
    switch (err) {
        case RuleError::None:            return "OK";
        case RuleError::BadSof:          return "ERR_BAD_SOF";
        case RuleError::TruncatedFrame:  return "ERR_TRUNCATED_FRAME";
        case RuleError::UnknownType:     return "ERR_UNKNOWN_TYPE";
        case RuleError::LengthAlign:     return "ERR_LENGTH_ALIGN";
        case RuleError::CrcMismatch:     return "ERR_CRC_MISMATCH";
        case RuleError::BufferOverflow:  return "ERR_BUFFER_OVERFLOW";
        case RuleError::BadOpcode:       return "ERR_BAD_OPCODE";
        case RuleError::RegOutOfRange:   return "ERR_REG_OUT_OF_RANGE";
        case RuleError::BadReserved:     return "ERR_BAD_RESERVED";
        case RuleError::BadFlags:        return "ERR_BAD_FLAGS";
        case RuleError::BadRuleId:       return "ERR_BAD_RULE_ID";
        case RuleError::DuplicateId:     return "ERR_DUPLICATE_ID";
        case RuleError::SafetyViolation: return "ERR_SAFETY_VIOLATION";
        case RuleError::RegReadOnly:     return "ERR_REG_READ_ONLY";
        case RuleError::RemoteInhibited: return "ERR_REMOTE_INHIBITED";
    }
    return "ERR_UNKNOWN";
}

RuleEngine::RuleEngine(std::uint32_t hubLeaseMs, Timestamp now) noexcept
    : hubLeaseMs_{hubLeaseMs}, lastEval_{now} {
    hubHeartbeat(now);
}

// ── доступ до регістрів ─────────────────────────────────────────────────

std::int32_t RuleEngine::read(std::uint8_t reg) const noexcept {
    return isValidReg(reg) ? regs_[reg] : 0;
}

void RuleEngine::setSensor(std::uint8_t reg, std::int32_t value) noexcept {
    if (isSensorReg(reg)) { regs_[reg] = value; }
}

bool RuleEngine::writeRegister(std::uint8_t reg, std::int32_t value) noexcept {
    if (!isValidReg(reg)) { return false; }
    if (isSensorReg(reg)) {
        // смуга давачів для правил Read-Only
        regs_[kErrorWord] |= static_cast<std::int32_t>(ErrorBit::ReadOnlyWrite);
        return false;
    }
    regs_[reg] = value;
    return true;
}

std::expected<void, RuleError> RuleEngine::remoteWrite(std::uint8_t reg,
                                                       std::int32_t value) noexcept {
    if (!isValidReg(reg)) { return std::unexpected(RuleError::RegOutOfRange); }
    if (isSensorReg(reg) || isTimerReg(reg)) { return std::unexpected(RuleError::RegReadOnly); }
    if (inhibited_[reg]) {
        regs_[kErrorWord] |= static_cast<std::int32_t>(ErrorBit::RemoteBlocked);
        return std::unexpected(RuleError::RemoteInhibited);
    }
    regs_[reg] = value;
    return {};
}

// ── таймери ─────────────────────────────────────────────────────────────

std::optional<std::size_t> RuleEngine::timerSlot(std::uint8_t reg) noexcept {
    if (!isTimerReg(reg)) {
        regs_[kErrorWord] |= static_cast<std::int32_t>(ErrorBit::BadTimer);
        return std::nullopt;
    }
    return static_cast<std::size_t>(reg - kTimerFirst);
}

void RuleEngine::mirrorTimers(Timestamp now) noexcept {
    for (std::size_t i = 0; i < kTimerCount; ++i) {
        const SoftTimer& t = timers_[i];
        std::uint32_t left = 0;
        if (t.armed) {
            const std::uint32_t gone = now.since(t.start);
            left = (gone >= t.durationMs) ? 0u : t.durationMs - gone;
        }
        regs_[kTimerFirst + i] = static_cast<std::int32_t>(left);
    }
}

void RuleEngine::hubHeartbeat(Timestamp now) noexcept {
    timers_[kHubLeaseSlot] = SoftTimer{true, now, hubLeaseMs_};
}

// ── умови ───────────────────────────────────────────────────────────────

bool RuleEngine::evalCondition(const RuleDescriptor& r, Timestamp now) noexcept {
    if (r.condOp == ConditionOp::TimerExpired) {
        const auto slot = timerSlot(r.inputReg);
        if (!slot) { return false; }
        const SoftTimer& t = timers_[*slot];
        if (!t.armed) { return false; }
        return now.since(t.start) > static_cast<std::uint32_t>(r.threshold);
    }

    const std::int32_t v = regs_[r.inputReg];
    switch (r.condOp) {
        case ConditionOp::Always:      return true;
        case ConditionOp::LessThan:    return v < r.threshold;
        case ConditionOp::GreaterThan: return v > r.threshold;
        case ConditionOp::Equal:       return v == r.threshold;
        case ConditionOp::NotEqual:    return v != r.threshold;
        case ConditionOp::BitSet:      return (v & r.threshold) == r.threshold;
        case ConditionOp::BitClear:    return (v & r.threshold) == 0;
        default:                       return false;   // валідація такого не пропускає
    }
}

// ── дії ─────────────────────────────────────────────────────────────────

void RuleEngine::enterEmergency() noexcept {
    // Знеструмлюємо всю смугу виконавців; на залізі тут же гасне MOE в TIM1->BDTR.
    for (std::uint8_t reg = kActuatorFirst; reg <= kActuatorLast; ++reg) { regs_[reg] = 0; }
    emergency_ = true;
}

void RuleEngine::applyAction(const RuleDescriptor& r) noexcept {
    switch (r.actionOp) {
        case ActionOp::OutputSet:
            writeRegister(r.outputTarget, r.actionParam != 0 ? 1 : 0);
            break;

        case ActionOp::SetSetpoint:
            // уставка приходить цілими одиницями величини — розгортаємо в Q16.16
            writeRegister(r.outputTarget, static_cast<std::int32_t>(r.actionParam) << 16);
            break;

        case ActionOp::ArmTimer:
            if (const auto slot = timerSlot(r.outputTarget)) {
                SoftTimer& t = timers_[*slot];
                if (t.armed) { break; }   // повторний завод не зсуває мітку запуску
                t = SoftTimer{true, lastEval_,
                              r.actionParam > 0 ? static_cast<std::uint32_t>(r.actionParam) : 0u};
            }
            break;

        case ActionOp::DisarmTimer:
            if (const auto slot = timerSlot(r.outputTarget)) {
                timers_[*slot].armed = false;
                regs_[kTimerFirst + *slot] = 0;
            }
            break;

        case ActionOp::EmergencyStop:
            enterEmergency();
            break;

        case ActionOp::InhibitRemote:
            if (isValidReg(r.outputTarget)) { inhibited_[r.outputTarget] = true; }
            break;
    }
}

// Автоскидання: умова стала хибною — знімаємо те, що поставило це правило.
void RuleEngine::undoAction(const RuleDescriptor& r) noexcept {
    switch (r.actionOp) {
        case ActionOp::OutputSet:
            writeRegister(r.outputTarget, r.actionParam != 0 ? 0 : 1);
            break;
        case ActionOp::ArmTimer:
            if (const auto slot = timerSlot(r.outputTarget)) {
                timers_[*slot].armed = false;
                regs_[kTimerFirst + *slot] = 0;
            }
            break;
        case ActionOp::InhibitRemote:
            if (isValidReg(r.outputTarget)) { inhibited_[r.outputTarget] = false; }
            break;
        default:
            break;   // аварійний стоп зворотної дії не має
    }
}

// ── такт ────────────────────────────────────────────────────────────────

void RuleEngine::evalRule(std::size_t slot, Timestamp now) noexcept {
    const RuleDescriptor& r = rules_[slot];
    if (r.id == 0 || !r.flags.has(RuleFlag::Enabled)) { return; }

    const bool critical = r.flags.has(RuleFlag::SafetyCritical);
    if (emergency_ && !critical) { return; }   // у блокуванні живі лише інваріанти

    const std::uint32_t bit = 1u << slot;

    if ((latched_ & bit) != 0) {   // зафіксоване тримає дію до скидання аварії
        applyAction(r);
        return;
    }

    const bool fallbackOnly = r.flags.has(RuleFlag::FallbackActive);
    const bool cond = (fallbackOnly && !fallback_) ? false : evalCondition(r, now);

    if (cond) {
        applyAction(r);
        fired_ |= bit;
        if (r.flags.has(RuleFlag::Latching)) { latched_ |= bit; }
    } else {
        if ((fired_ & bit) != 0 && r.flags.has(RuleFlag::InvertAction)) { undoAction(r); }
        fired_ &= ~bit;
    }
}

void RuleEngine::tick(Timestamp now) noexcept {
    lastEval_ = now;

    const SoftTimer& lease = timers_[kHubLeaseSlot];
    fallback_ = !lease.armed || now.since(lease.start) > lease.durationMs;

    mirrorTimers(now);

    // Два проходи: спершу критичні інваріанти, далі решта.
    for (int pass = 0; pass < 2; ++pass) {
        for (std::size_t i = 0; i < count_; ++i) {
            const bool critical = rules_[i].flags.has(RuleFlag::SafetyCritical);
            if ((pass == 0) != critical) { continue; }
            evalRule(i, now);
        }
    }

    std::int32_t status = 0;
    if (fallback_)  { status |= static_cast<std::int32_t>(StatusBit::Fallback); }
    if (emergency_) { status |= static_cast<std::int32_t>(StatusBit::Emergency); }
    if (latched_)   { status |= static_cast<std::int32_t>(StatusBit::Latched); }
    regs_[kStatusWord] = status;
}

void RuleEngine::resetAlarm() noexcept {
    latched_ = 0;
    fired_ = 0;
    emergency_ = false;
    regs_[kStatusWord] &= ~static_cast<std::int32_t>(
        static_cast<std::int32_t>(StatusBit::Emergency) | static_cast<std::int32_t>(StatusBit::Latched));
    regs_[kErrorWord] = 0;
    // Причина аварії нікуди не дінеться: критичне правило спрацює знову.
}

// ── верифікація й фіксація таблиці ──────────────────────────────────────

namespace {

std::expected<void, RuleError> checkTargets(const RuleDescriptor& r) noexcept {
    if (!isValidReg(r.inputReg) || !isValidReg(r.outputTarget)) {
        return std::unexpected(RuleError::RegOutOfRange);
    }
    if (r.condOp == ConditionOp::TimerExpired && !isTimerReg(r.inputReg)) {
        return std::unexpected(RuleError::RegOutOfRange);
    }
    switch (r.actionOp) {
        case ActionOp::OutputSet:
            if (!isActuatorReg(r.outputTarget)) { return std::unexpected(RuleError::RegOutOfRange); }
            break;
        case ActionOp::SetSetpoint:
            if (!isSetpointReg(r.outputTarget)) { return std::unexpected(RuleError::RegOutOfRange); }
            break;
        case ActionOp::ArmTimer:
        case ActionOp::DisarmTimer:
            // гніздо оренди хаба правилам не належить
            if (!isTimerReg(r.outputTarget) || r.outputTarget == kHubLeaseReg) {
                return std::unexpected(RuleError::RegOutOfRange);
            }
            break;
        case ActionOp::InhibitRemote:
            if (!isActuatorReg(r.outputTarget) && !isSetpointReg(r.outputTarget)) {
                return std::unexpected(RuleError::RegOutOfRange);
            }
            break;
        default:
            break;
    }
    return {};
}

}  // namespace

std::expected<void, RuleError> RuleEngine::validate(
        std::span<const RuleDescriptor> table) const noexcept {
    if (table.size() > kMaxRules) { return std::unexpected(RuleError::BufferOverflow); }

    for (std::size_t i = 0; i < table.size(); ++i) {
        const RuleDescriptor& r = table[i];
        if (r.id == 0)              { return std::unexpected(RuleError::BadRuleId); }
        if (r.reserved != 0)        { return std::unexpected(RuleError::BadReserved); }
        if (r.flags.unknownBits())  { return std::unexpected(RuleError::BadFlags); }
        if (!isKnown(r.condOp) || !isKnown(r.actionOp)) {
            return std::unexpected(RuleError::BadOpcode);
        }
        if (auto ok = checkTargets(r); !ok) { return ok; }

        const auto head = table.first(i);
        if (std::any_of(head.begin(), head.end(),
                        [&](const RuleDescriptor& o) { return o.id == r.id; })) {
            return std::unexpected(RuleError::DuplicateId);
        }
    }

    // Чинні критичні правила мають дійти до нової таблиці слово в слово.
    for (std::size_t i = 0; i < count_; ++i) {
        const RuleDescriptor& cur = rules_[i];
        if (!cur.flags.has(RuleFlag::SafetyCritical)) { continue; }

        const auto same = std::find_if(table.begin(), table.end(),
                                       [&](const RuleDescriptor& o) { return o.id == cur.id; });
        if (same == table.end() || *same != cur) {
            return std::unexpected(RuleError::SafetyViolation);
        }
    }
    return {};
}

std::expected<void, RuleError> RuleEngine::install(
        std::span<const RuleDescriptor> table) noexcept {
    if (auto ok = validate(table); !ok) { return ok; }

    InterruptLock lock;   // атомарне перемикання: такт не побачить півтаблиці
    std::copy(table.begin(), table.end(), rules_.begin());
    std::fill(rules_.begin() + static_cast<std::ptrdiff_t>(table.size()), rules_.end(),
              RuleDescriptor{});
    count_ = table.size();
    fired_ = 0;      // гнізда перенумерувалися — старі маски вже не про ці правила
    latched_ = 0;
    return {};
}

}  // namespace rules
