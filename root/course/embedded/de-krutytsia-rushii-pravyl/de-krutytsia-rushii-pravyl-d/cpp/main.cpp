#include <cstdint>
#include <array>
#include <span>

namespace embedded::engine {

enum class RuleFlag : uint16_t {
    Enabled        = 1 << 0,
    SafetyCritical = 1 << 1,
    Latched        = 1 << 2
};

enum class OpCode : uint8_t {
    Nop         = 0,
    LessThan    = 1,
    GreaterThan = 2,
    Equal       = 3
};

enum class ActionCode : uint8_t {
    None        = 0,
    SetOutput   = 1,
    ClearOutput = 2,
    Emergency   = 3
};

struct alignas(4) RuleEntry {
    uint16_t id{};
    uint16_t flags{};
    OpCode op{OpCode::Nop};
    uint8_t inReg{};
    int32_t threshold{};
    ActionCode action{ActionCode::None};
    uint8_t outReg{};
    int16_t param{};

    [[nodiscard]] constexpr bool isEnabled() const noexcept {
        return (flags & static_cast<uint16_t>(RuleFlag::Enabled)) != 0;
    }
};

template <std::size_t MaxRules = 16, std::size_t MaxRegs = 32>
class EdgeRuleEngine {
public:
    constexpr EdgeRuleEngine() = default;

    void setRegister(std::size_t reg, int32_t val) noexcept {
        if (reg < MaxRegs) {
            registers_[reg] = val;
        }
    }

    [[nodiscard]] int32_t getRegister(std::size_t reg) const noexcept {
        return (reg < MaxRegs) ? registers_[reg] : 0;
    }

    [[nodiscard]] bool isEmergencyLatched() const noexcept {
        return emergencyLatched_;
    }

    bool addRule(const RuleEntry& rule) noexcept {
        if (ruleCount_ >= MaxRules) {
            return false;
        }
        rules_[ruleCount_++] = rule;
        return true;
    }

    void evaluate() noexcept {
        for (std::size_t i = 0; i < ruleCount_; ++i) {
            const auto& r = rules_[i];
            if (!r.isEnabled()) {
                continue;
            }

            const int32_t val = registers_[r.inReg];
            bool conditionMet = false;

            switch (r.op) {
                case OpCode::LessThan:    conditionMet = (val < r.threshold); break;
                case OpCode::GreaterThan: conditionMet = (val > r.threshold); break;
                case OpCode::Equal:       conditionMet = (val == r.threshold); break;
                default: break;
            }

            if (conditionMet) {
                switch (r.action) {
                    case ActionCode::SetOutput:
                        registers_[r.outReg] = r.param;
                        break;
                    case ActionCode::ClearOutput:
                        registers_[r.outReg] = 0;
                        break;
                    case ActionCode::Emergency:
                        emergencyLatched_ = true;
                        registers_[r.outReg] = 0;
                        break;
                    default: break;
                }
            }
        }
    }

private:
    std::array<int32_t, MaxRegs> registers_{};
    std::array<RuleEntry, MaxRules> rules_{};
    std::size_t ruleCount_{0};
    bool emergencyLatched_{false};
};

} // namespace embedded::engine
