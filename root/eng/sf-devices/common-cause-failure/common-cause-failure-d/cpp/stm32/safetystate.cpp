#include <cstdint>
#include <cstddef>

namespace Diagnostics {

enum class SafetyState : uint8_t {
    Nominal,
    DegradedFiltering,
    LimpHome,
    SafeShutdown
};

class FaultDiagnosticStateMachine {
public:
    static constexpr uint32_t MaxGlitchCount = 5U;

    constexpr FaultDiagnosticStateMachine() noexcept
        : state_(SafetyState::Nominal), mismatch_counter_(0), total_faults_(0) {}

    SafetyState update(bool is_sample_valid) noexcept {
        switch (state_) {
        case SafetyState::Nominal:
            if (!is_sample_valid) {
                if (++mismatch_counter_ >= MaxGlitchCount) {
                    state_ = SafetyState::DegradedFiltering;
                    ++total_faults_;
                }
            } else {
                mismatch_counter_ = 0;
            }
            break;

        case SafetyState::DegradedFiltering:
            if (!is_sample_valid) {
                if (++mismatch_counter_ >= (MaxGlitchCount * 2)) {
                    state_ = SafetyState::LimpHome;
                }
            } else {
                mismatch_counter_ = 0;
                state_ = SafetyState::Nominal;
            }
            break;

        case SafetyState::LimpHome:
            if (!is_sample_valid) {
                if (++mismatch_counter_ >= (MaxGlitchCount * 3)) {
                    state_ = SafetyState::SafeShutdown;
                }
            }
            break;

        case SafetyState::SafeShutdown:
            // Апаратне замикання в безпечний стан
            break;
        }

        return state_;
    }

    [[nodiscard]] SafetyState getState() const noexcept { return state_; }
    [[nodiscard]] uint32_t getTotalFaults() const noexcept { return total_faults_; }

private:
    SafetyState state_;
    uint32_t mismatch_counter_;
    uint32_t total_faults_;
};

} // namespace Diagnostics
