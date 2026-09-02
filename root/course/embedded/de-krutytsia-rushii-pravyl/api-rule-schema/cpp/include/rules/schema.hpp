// Бінарна схема правил: дескриптор, коди операцій, карта регістрів.
// На відміну від C, дескриптор не накладається на буфер, а розбирається
// явно з байтів — порядок полів на шині від розкладки структури не залежить.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

namespace rules {

inline constexpr std::size_t  kMaxRules       = 32;
inline constexpr std::size_t  kDescriptorSize = 16;
inline constexpr std::uint8_t kTotalRegisters = 0x40;

// ── карта регістрів стану ───────────────────────────────────────────────
inline constexpr std::uint8_t kSensorFirst   = 0x00, kSensorLast   = 0x0F;
inline constexpr std::uint8_t kActuatorFirst = 0x10, kActuatorLast = 0x1F;
inline constexpr std::uint8_t kSetpointFirst = 0x20, kSetpointLast = 0x2F;
inline constexpr std::uint8_t kTimerFirst    = 0x30, kTimerLast    = 0x37;
inline constexpr std::uint8_t kStatusWord    = 0x38, kErrorWord    = 0x39;

inline constexpr std::size_t  kTimerCount   = kTimerLast - kTimerFirst + 1;
// Останнє гніздо таймерів належить оренді керування від хаба.
inline constexpr std::size_t  kHubLeaseSlot = kTimerCount - 1;
inline constexpr std::uint8_t kHubLeaseReg  = static_cast<std::uint8_t>(kTimerFirst + kHubLeaseSlot);

constexpr bool isSensorReg(std::uint8_t r) noexcept { return r <= kSensorLast; }
constexpr bool isActuatorReg(std::uint8_t r) noexcept { return r >= kActuatorFirst && r <= kActuatorLast; }
constexpr bool isSetpointReg(std::uint8_t r) noexcept { return r >= kSetpointFirst && r <= kSetpointLast; }
constexpr bool isTimerReg(std::uint8_t r) noexcept { return r >= kTimerFirst && r <= kTimerLast; }
constexpr bool isValidReg(std::uint8_t r) noexcept { return r < kTotalRegisters; }

enum class StatusBit : std::int32_t { Fallback = 1 << 0, Emergency = 1 << 1, Latched = 1 << 2 };
enum class ErrorBit  : std::int32_t { ReadOnlyWrite = 1 << 0, BadTimer = 1 << 1, RemoteBlocked = 1 << 2 };

// ── фіксована точка Q16.16 ──────────────────────────────────────────────
constexpr std::int32_t q16(double v) noexcept { return static_cast<std::int32_t>(v * 65536.0); }
constexpr float fromQ16(std::int32_t v) noexcept { return static_cast<float>(v) / 65536.0f; }

enum class RuleFlag : std::uint16_t {
    Enabled        = 1 << 0,
    SafetyCritical = 1 << 1,
    Latching       = 1 << 2,
    InvertAction   = 1 << 3,
    FallbackActive = 1 << 4,
};

inline constexpr std::uint16_t kKnownFlags = 0x001F;

struct Flags {
    std::uint16_t bits{};

    constexpr bool has(RuleFlag f) const noexcept {
        return (bits & static_cast<std::uint16_t>(f)) != 0;
    }
    constexpr bool unknownBits() const noexcept { return (bits & ~kKnownFlags) != 0; }

    friend constexpr bool operator==(Flags, Flags) noexcept = default;
};

constexpr Flags operator|(RuleFlag a, RuleFlag b) noexcept {
    return Flags{static_cast<std::uint16_t>(static_cast<std::uint16_t>(a) |
                                            static_cast<std::uint16_t>(b))};
}
constexpr Flags operator|(Flags a, RuleFlag b) noexcept {
    return Flags{static_cast<std::uint16_t>(a.bits | static_cast<std::uint16_t>(b))};
}

enum class ConditionOp : std::uint8_t {
    Always       = 0x01,
    LessThan     = 0x02,
    GreaterThan  = 0x03,
    Equal        = 0x04,
    NotEqual     = 0x05,
    BitSet       = 0x06,
    BitClear     = 0x07,
    TimerExpired = 0x08,
};

enum class ActionOp : std::uint8_t {
    OutputSet     = 0x10,
    SetSetpoint   = 0x11,
    ArmTimer      = 0x12,
    DisarmTimer   = 0x13,
    EmergencyStop = 0x14,
    InhibitRemote = 0x15,
};

constexpr bool isKnown(ConditionOp op) noexcept {
    return op >= ConditionOp::Always && op <= ConditionOp::TimerExpired;
}
constexpr bool isKnown(ActionOp op) noexcept {
    return op >= ActionOp::OutputSet && op <= ActionOp::InhibitRemote;
}

enum class RuleError : std::uint8_t {
    None            = 0x00,
    BadSof          = 0x10,
    TruncatedFrame  = 0x11,
    UnknownType     = 0x12,
    LengthAlign     = 0x13,
    CrcMismatch     = 0x14,
    BufferOverflow  = 0x15,
    BadOpcode       = 0x20,
    RegOutOfRange   = 0x21,
    BadReserved     = 0x22,
    BadFlags        = 0x23,
    BadRuleId       = 0x24,
    DuplicateId     = 0x25,
    SafetyViolation = 0x26,
    RegReadOnly     = 0x30,
    RemoteInhibited = 0x31,
};

std::string_view describe(RuleError err) noexcept;

namespace wire {

constexpr std::uint16_t read16(std::span<const std::byte> b, std::size_t off) noexcept {
    return static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(b[off]) |
                                      (std::to_integer<std::uint16_t>(b[off + 1]) << 8));
}
constexpr std::uint32_t read32(std::span<const std::byte> b, std::size_t off) noexcept {
    return static_cast<std::uint32_t>(read16(b, off)) |
           (static_cast<std::uint32_t>(read16(b, off + 2)) << 16);
}
constexpr void write16(std::span<std::byte> b, std::size_t off, std::uint16_t v) noexcept {
    b[off]     = static_cast<std::byte>(v & 0xFF);
    b[off + 1] = static_cast<std::byte>(v >> 8);
}
constexpr void write32(std::span<std::byte> b, std::size_t off, std::uint32_t v) noexcept {
    write16(b, off, static_cast<std::uint16_t>(v & 0xFFFF));
    write16(b, off + 2, static_cast<std::uint16_t>(v >> 16));
}

}  // namespace wire

// 16 байтів на шині, Little-Endian.
struct RuleDescriptor {
    std::uint16_t id{};
    Flags         flags{};
    ConditionOp   condOp{ConditionOp::Always};
    std::uint8_t  inputReg{};
    std::uint16_t reserved{};
    std::int32_t  threshold{};
    ActionOp      actionOp{ActionOp::OutputSet};
    std::uint8_t  outputTarget{};
    std::int16_t  actionParam{};

    friend bool operator==(const RuleDescriptor&, const RuleDescriptor&) noexcept = default;

    static constexpr RuleDescriptor fromWire(std::span<const std::byte> b) noexcept {
        RuleDescriptor d{};
        d.id           = wire::read16(b, 0);
        d.flags        = Flags{wire::read16(b, 2)};
        d.condOp       = static_cast<ConditionOp>(std::to_integer<std::uint8_t>(b[4]));
        d.inputReg     = std::to_integer<std::uint8_t>(b[5]);
        d.reserved     = wire::read16(b, 6);
        d.threshold    = static_cast<std::int32_t>(wire::read32(b, 8));
        d.actionOp     = static_cast<ActionOp>(std::to_integer<std::uint8_t>(b[12]));
        d.outputTarget = std::to_integer<std::uint8_t>(b[13]);
        d.actionParam  = static_cast<std::int16_t>(wire::read16(b, 14));
        return d;
    }

    constexpr void toWire(std::span<std::byte> b) const noexcept {
        wire::write16(b, 0, id);
        wire::write16(b, 2, flags.bits);
        b[4] = static_cast<std::byte>(condOp);
        b[5] = static_cast<std::byte>(inputReg);
        wire::write16(b, 6, reserved);
        wire::write32(b, 8, static_cast<std::uint32_t>(threshold));
        b[12] = static_cast<std::byte>(actionOp);
        b[13] = static_cast<std::byte>(outputTarget);
        wire::write16(b, 14, static_cast<std::uint16_t>(actionParam));
    }
};

// Таблиця фіксованої місткості: жодного динамічного виділення.
struct RuleTable {
    std::array<RuleDescriptor, kMaxRules> rules{};
    std::size_t                           count{};

    std::span<const RuleDescriptor> view() const noexcept { return {rules.data(), count}; }
};

}  // namespace rules
