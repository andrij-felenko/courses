#include <cstdint>
#include <array>
#include <span>

namespace embedded::rules {

enum class RuleFlag : uint16_t {
    Enabled        = 1 << 0,
    SafetyCritical = 1 << 1,
    Latching       = 1 << 2,
    InvertAction   = 1 << 3,
    FallbackActive = 1 << 4
};

enum class ConditionOp : uint8_t {
    Always       = 0x01,
    LessThan     = 0x02,
    GreaterThan  = 0x03,
    Equal        = 0x04,
    NotEqual     = 0x05,
    BitSet       = 0x06,
    BitClear     = 0x07,
    TimerExpired = 0x08
};

enum class ActionOp : uint8_t {
    OutputSet       = 0x10,
    SetSetpoint     = 0x11,
    ArmTimer        = 0x12,
    DisarmTimer     = 0x13,
    EmergencyStop   = 0x14,
    InhibitRemote   = 0x15
};

struct alignas(4) RuleDescriptor {
    uint16_t ruleId{};
    uint16_t flags{};
    ConditionOp condOp{ConditionOp::Always};
    uint8_t inputReg{};
    uint16_t reserved{};
    int32_t threshold{};
    ActionOp actionOp{ActionOp::OutputSet};
    uint8_t outputTarget{};
    int16_t actionParam{};

    [[nodiscard]] constexpr bool isEnabled() const noexcept {
        return (flags & static_cast<uint16_t>(RuleFlag::Enabled)) != 0;
    }

    [[nodiscard]] constexpr bool isSafetyCritical() const noexcept {
        return (flags & static_cast<uint16_t>(RuleFlag::SafetyCritical)) != 0;
    }

    [[nodiscard]] constexpr bool isFallbackActive() const noexcept {
        return (flags & static_cast<uint16_t>(RuleFlag::FallbackActive)) != 0;
    }
};

template <std::size_t MaxRules = 32, std::size_t MaxRegs = 64>
struct RuleEngineStorage {
    std::array<int32_t, MaxRegs> registers{};
    std::array<RuleDescriptor, MaxRules> rules{};
    std::size_t activeRules{0};
    bool fallbackActive{false};
    uint32_t lastEvalTimestampMs{0};

    [[nodiscard]] std::span<const RuleDescriptor> activeRuleSpan() const noexcept {
        return std::span<const RuleDescriptor>(rules.data(), activeRules);
    }
};

} // namespace embedded::rules
