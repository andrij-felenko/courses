#include <iostream>
#include <cstdint>
#include <string_view>
#include <array>
#include <optional>
#include <algorithm>
#include <span>
#include <iomanip>

namespace autopilot::preemption {

enum class BehaviorState : uint8_t {
    Idle = 0,
    Running,
    Suspended,
    Aborted
};

enum class PreemptReason : uint8_t {
    None = 0,
    CollisionAvoidance,
    CriticalBattery,
    GeofenceBreach,
    ManualOverride
};

struct MotionSetpoint {
    float vx{0.0F};       // м/с
    float vy{0.0F};       // м/с
    float vz{0.0F};       // м/с
    float yaw_rate{0.0F}; // рад/с
};

struct BehaviorCheckpoint {
    uint16_t waypoint_id{0};
    float spline_s{0.0F};
    float saved_speed{0.0F};
    uint32_t flags{0};
};

class IBehavior {
public:
    virtual ~IBehavior() = default;

    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
    [[nodiscard]] virtual uint8_t priority() const noexcept = 0;
    [[nodiscard]] virtual BehaviorState state() const noexcept = 0;
    virtual void set_state(BehaviorState state) noexcept = 0;

    virtual bool initialize() noexcept = 0;
    virtual void tick(float dt, MotionSetpoint& out_sp) noexcept = 0;
    virtual bool halt(PreemptReason reason) noexcept = 0;
    virtual bool resume(const BehaviorCheckpoint& cp) noexcept = 0;
    [[nodiscard]] virtual const BehaviorCheckpoint& checkpoint() const noexcept = 0;
};

class BumplessFilter {
public:
    constexpr BumplessFilter(float max_accel, float max_jerk) noexcept
        : max_accel_{max_accel}, max_jerk_{max_jerk} {}

    void update(const MotionSetpoint& target, float dt) noexcept {
        constexpr float kp = 2.5F;

        const float des_ax = std::clamp((target.vx - current_sp_.vx) * kp, -max_accel_, max_accel_);
        const float des_ay = std::clamp((target.vy - current_sp_.vy) * kp, -max_accel_, max_accel_);
        const float des_az = std::clamp((target.vz - current_sp_.vz) * kp, -max_accel_, max_accel_);

        const float jx = std::clamp((des_ax - current_accel_.vx) / dt, -max_jerk_, max_jerk_);
        const float jy = std::clamp((des_ay - current_accel_.vy) / dt, -max_jerk_, max_jerk_);
        const float jz = std::clamp((des_az - current_accel_.vz) / dt, -max_jerk_, max_jerk_);

        current_accel_.vx += jx * dt;
        current_accel_.vy += jy * dt;
        current_accel_.vz += jz * dt;

        current_sp_.vx += current_accel_.vx * dt;
        current_sp_.vy += current_accel_.vy * dt;
        current_sp_.vz += current_accel_.vz * dt;
        current_sp_.yaw_rate = target.yaw_rate;
    }

    [[nodiscard]] const MotionSetpoint& setpoint() const noexcept {
        return current_sp_;
    }

private:
    MotionSetpoint current_sp_{};
    MotionSetpoint current_accel_{};
    float max_accel_{4.0F};
    float max_jerk_{12.0F};
};

class WaypointCruiseBehavior final : public IBehavior {
public:
    [[nodiscard]] std::string_view name() const noexcept override {
        return "WaypointCruise";
    }

    [[nodiscard]] uint8_t priority() const noexcept override {
        return 40; // Стандартний рівень місії
    }

    [[nodiscard]] BehaviorState state() const noexcept override {
        return state_;
    }

    void set_state(BehaviorState state) noexcept override {
        state_ = state;
    }

    bool initialize() noexcept override {
        current_wp_ = 1;
        progress_ = 0.0F;
        cruise_speed_ = 15.0F;
        state_ = BehaviorState::Idle;
        return true;
    }

    void tick(float dt, MotionSetpoint& out_sp) noexcept override {
        progress_ += 0.02F * dt;
        if (progress_ >= 1.0F) {
            progress_ = 0.0F;
            ++current_wp_;
        }
        out_sp.vx = cruise_speed_;
        out_sp.vy = 0.0F;
        out_sp.vz = 0.0F;
        out_sp.yaw_rate = 0.0F;
    }

    bool halt(PreemptReason reason) noexcept override {
        (void)reason;
        checkpoint_.waypoint_id = current_wp_;
        checkpoint_.spline_s = progress_;
        checkpoint_.saved_speed = cruise_speed_;
        return true;
    }

    bool resume(const BehaviorCheckpoint& cp) noexcept override {
        current_wp_ = cp.waypoint_id;
        progress_ = cp.spline_s;
        cruise_speed_ = cp.saved_speed;
        return true;
    }

    [[nodiscard]] const BehaviorCheckpoint& checkpoint() const noexcept override {
        return checkpoint_;
    }

private:
    BehaviorState state_{BehaviorState::Idle};
    uint16_t current_wp_{1};
    float progress_{0.0F};
    float cruise_speed_{15.0F};
    BehaviorCheckpoint checkpoint_{};
};

class CollisionAvoidanceBehavior final : public IBehavior {
public:
    [[nodiscard]] std::string_view name() const noexcept override {
        return "CollisionAvoidance";
    }

    [[nodiscard]] uint8_t priority() const noexcept override {
        return 80; // Високий реактивний пріоритет безпеки
    }

    [[nodiscard]] BehaviorState state() const noexcept override {
        return state_;
    }

    void set_state(BehaviorState state) noexcept override {
        state_ = state;
    }

    bool initialize() noexcept override {
        climb_rate_ = 3.5F;
        lateral_speed_ = -2.0F;
        state_ = BehaviorState::Idle;
        return true;
    }

    void tick(float dt, MotionSetpoint& out_sp) noexcept override {
        (void)dt;
        out_sp.vx = 0.0F;
        out_sp.vy = lateral_speed_;
        out_sp.vz = climb_rate_;
        out_sp.yaw_rate = 0.1F;
    }

    bool halt(PreemptReason reason) noexcept override {
        (void)reason;
        return true;
    }

    bool resume(const BehaviorCheckpoint& cp) noexcept override {
        (void)cp;
        return true;
    }

    [[nodiscard]] const BehaviorCheckpoint& checkpoint() const noexcept override {
        return checkpoint_;
    }

private:
    BehaviorState state_{BehaviorState::Idle};
    float climb_rate_{3.5F};
    float lateral_speed_{-2.0F};
    BehaviorCheckpoint checkpoint_{};
};

class BehaviorManager {
public:
    static constexpr size_t MaxBehaviors = 8;

    explicit BehaviorManager(float max_accel, float max_jerk) noexcept
        : filter_{max_accel, max_jerk} {}

    bool register_behavior(IBehavior* behavior) noexcept {
        if (count_ >= MaxBehaviors || behavior == nullptr) {
            return false;
        }
        registry_[count_++] = behavior;
        behavior->initialize();
        return true;
    }

    void step(float dt, MotionSetpoint& out_sp) noexcept {
        const int candidate_idx = evaluate_highest_priority();

        if (candidate_idx != active_idx_) {
            switch_active_behavior(candidate_idx);
            active_idx_ = candidate_idx;
        }

        MotionSetpoint raw_sp{};
        if (active_idx_ >= 0 && active_idx_ < static_cast<int>(count_)) {
            registry_[active_idx_]->tick(dt, raw_sp);
        }

        filter_.update(raw_sp, dt);
        out_sp = filter_.setpoint();
    }

    [[nodiscard]] int active_index() const noexcept {
        return active_idx_;
    }

    [[nodiscard]] IBehavior* get_behavior(size_t idx) noexcept {
        return (idx < count_) ? registry_[idx] : nullptr;
    }

private:
    [[nodiscard]] int evaluate_highest_priority() const noexcept {
        int best_idx = -1;
        uint8_t highest_prio = 0;

        for (size_t i = 0; i < count_; ++i) {
            const auto* b = registry_[i];
            if (b->state() == BehaviorState::Running || b->state() == BehaviorState::Suspended) {
                if (b->priority() > highest_prio) {
                    highest_prio = b->priority();
                    best_idx = static_cast<int>(i);
                }
            }
        }
        return best_idx;
    }

    void switch_active_behavior(int next_idx) noexcept {
        if (active_idx_ >= 0 && active_idx_ < static_cast<int>(count_)) {
            auto* current = registry_[active_idx_];
            if (current->state() == BehaviorState::Running) {
                current->halt(PreemptReason::CollisionAvoidance);
                current->set_state(BehaviorState::Suspended);
            }
        }

        if (next_idx >= 0 && next_idx < static_cast<int>(count_)) {
            auto* next = registry_[next_idx];
            if (next->state() == BehaviorState::Suspended) {
                next->resume(next->checkpoint());
            }
            next->set_state(BehaviorState::Running);
        }
    }

    std::array<IBehavior*, MaxBehaviors> registry_{};
    size_t count_{0};
    int active_idx_{-1};
    BumplessFilter filter_;
};

} // namespace autopilot::preemption

int main() {
    using namespace autopilot::preemption;

    BehaviorManager manager{4.0F, 12.0F};
    WaypointCruiseBehavior cruise;
    CollisionAvoidanceBehavior avoid;

    manager.register_behavior(&cruise);
    manager.register_behavior(&avoid);

    cruise.set_state(BehaviorState::Running);

    constexpr float dt = 0.02F;
    MotionSetpoint sp{};

    std::cout << "=== СТАРТ СИМУЛЯЦІЇ ВИТІСНЕННЯ C++ (50 Гц) ===\n";
    for (int step = 0; step <= 250; ++step) {
        const float t = static_cast<float>(step) * dt;

        if (step == 50) {
            std::cout << "\n[t=" << std::fixed << std::setprecision(2) << t 
                      << " с] ПОДІЯ: Зафіксовано перешкоду! Активація CollisionAvoidance\n";
            avoid.set_state(BehaviorState::Running);
        }

        if (step == 150) {
            std::cout << "\n[t=" << std::fixed << std::setprecision(2) << t 
                      << " с] ПОДІЯ: Перешкоду оминуто! Деактивація CollisionAvoidance\n";
            avoid.set_state(BehaviorState::Idle);
        }

        manager.step(dt, sp);

        if (step % 25 == 0 || step == 51 || step == 151) {
            const auto* active = manager.get_behavior(manager.active_index());
            std::string_view name = (active != nullptr) ? active->name() : "NONE";
            std::cout << "[t=" << std::setw(5) << t << " с] Активна: " 
                      << std::setw(18) << std::left << name 
                      << " | vx=" << std::setw(6) << sp.vx 
                      << " | vy=" << std::setw(6) << sp.vy 
                      << " | vz=" << std::setw(5) << sp.vz << " м/с\n";
        }
    }

    std::cout << "\n=== ТЕСТ C++ ЗАВЕРШЕНО УСПІШНО ===\n";
    return 0;
}
