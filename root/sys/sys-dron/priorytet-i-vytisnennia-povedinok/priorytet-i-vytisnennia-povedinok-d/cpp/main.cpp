#include <cstdint>
#include <string_view>
#include <array>
#include <optional>
#include <algorithm>
#include <span>

namespace autopilot::autonomy {

enum class BehaviorState : uint8_t {
    Inactive = 0,
    Running,
    Suspended,
    Failed
};

enum class PreemptReason : uint8_t {
    None = 0,
    SafetyOverride,
    Failsafe,
    OperatorAbort
};

struct MotionSetpoint {
    float vx{0.0F};       // м/с
    float vy{0.0F};       // м/с
    float vz{0.0F};       // м/с
    float yaw_rate{0.0F}; // рад/с
};

struct BehaviorCheckpoint {
    uint16_t waypoint_index{0};
    float spline_progress{0.0F};
    uint32_t survey_grid_mask{0};
    float accumulated_energy_mah{0.0F};
};

class IBehavior {
public:
    virtual ~IBehavior() = default;

    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
    [[nodiscard]] virtual uint8_t priority() const noexcept = 0;
    [[nodiscard]] virtual BehaviorState state() const noexcept = 0;
    virtual void set_state(BehaviorState state) noexcept = 0;
    
    virtual bool initialize() noexcept = 0;
    virtual void update(float dt, MotionSetpoint& out_sp) noexcept = 0;
    virtual bool halt(PreemptReason reason) noexcept = 0;
    virtual bool resume(const BehaviorCheckpoint& cp) noexcept = 0;
    [[nodiscard]] virtual const BehaviorCheckpoint& checkpoint() const noexcept = 0;
};

class BehaviorDispatcher {
public:
    static constexpr size_t MaxBehaviors = 8;

    explicit BehaviorDispatcher(float max_accel, float max_jerk) noexcept
        : max_accel_{max_accel}, max_jerk_{max_jerk} {}

    bool register_behavior(IBehavior* behavior) noexcept {
        if (count_ >= MaxBehaviors || behavior == nullptr) {
            return false;
        }
        behaviors_[count_++] = behavior;
        behavior->initialize();
        behavior->set_state(BehaviorState::Inactive);
        return true;
    }

    void tick(float dt, MotionSetpoint& out_sp) noexcept {
        const int8_t best_index = select_highest_priority();

        if (best_index != active_index_) {
            handle_preemption_transition(best_index);
            active_index_ = best_index;
        }

        MotionSetpoint raw_sp{};
        if (active_index_ >= 0 && active_index_ < static_cast<int8_t>(count_)) {
            behaviors_[active_index_]->update(dt, raw_sp);
        }

        apply_bumpless_filter(raw_sp, dt);
        out_sp = current_smoothed_sp_;
    }

    [[nodiscard]] const MotionSetpoint& current_setpoint() const noexcept {
        return current_smoothed_sp_;
    }

private:
    [[nodiscard]] int8_t select_highest_priority() const noexcept {
        int8_t best = -1;
        uint8_t highest_prio = 0;
        for (size_t i = 0; i < count_; ++i) {
            const auto* b = behaviors_[i];
            if (b->state() == BehaviorState::Running || b->state() == BehaviorState::Suspended) {
                if (b->priority() > highest_prio) {
                    highest_prio = b->priority();
                    best = static_cast<int8_t>(i);
                }
            }
        }
        return best;
    }

    void handle_preemption_transition(int8_t next_index) noexcept {
        if (active_index_ >= 0 && active_index_ < static_cast<int8_t>(count_)) {
            auto* current = behaviors_[active_index_];
            if (current->state() == BehaviorState::Running) {
                current->halt(PreemptReason::SafetyOverride);
                current->set_state(BehaviorState::Suspended);
            }
        }

        if (next_index >= 0 && next_index < static_cast<int8_t>(count_)) {
            auto* next = behaviors_[next_index];
            if (next->state() == BehaviorState::Suspended) {
                next->resume(next->checkpoint());
            }
            next->set_state(BehaviorState::Running);
        }
    }

    void apply_bumpless_filter(const MotionSetpoint& target, float dt) noexcept {
        constexpr float kp = 2.5F;
        const float des_ax = std::clamp((target.vx - current_smoothed_sp_.vx) * kp, -max_accel_, max_accel_);
        const float des_ay = std::clamp((target.vy - current_smoothed_sp_.vy) * kp, -max_accel_, max_accel_);
        const float des_az = std::clamp((target.vz - current_smoothed_sp_.vz) * kp, -max_accel_, max_accel_);

        const float jx = std::clamp((des_ax - current_accel_.vx) / dt, -max_jerk_, max_jerk_);
        const float jy = std::clamp((des_ay - current_accel_.vy) / dt, -max_jerk_, max_jerk_);
        const float jz = std::clamp((des_az - current_accel_.vz) / dt, -max_jerk_, max_jerk_);

        current_accel_.vx += jx * dt;
        current_accel_.vy += jy * dt;
        current_accel_.vz += jz * dt;

        current_smoothed_sp_.vx += current_accel_.vx * dt;
        current_smoothed_sp_.vy += current_accel_.vy * dt;
        current_smoothed_sp_.vz += current_accel_.vz * dt;
        current_smoothed_sp_.yaw_rate = target.yaw_rate;
    }

    std::array<IBehavior*, MaxBehaviors> behaviors_{};
    size_t count_{0};
    int8_t active_index_{-1};
    MotionSetpoint current_smoothed_sp_{};
    MotionSetpoint current_accel_{};
    float max_accel_{4.0F};
    float max_jerk_{12.0F};
};

} // namespace autopilot::autonomy
