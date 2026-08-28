#include <array>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <optional>
#include <span>

enum class GoalAction : uint8_t {
    NavigateWaypoint,
    SurveyPolygon,
    LoiterPosition,
    EmergencyReturn
};

enum class GoalState : uint8_t {
    Empty,
    Pending,
    Active,
    Preempted,
    Completed,
    Aborted,
    Rejected
};

struct GoalItem {
    uint32_t id{0};
    GoalAction action{GoalAction::NavigateWaypoint};
    uint8_t priority{0};
    float target_x{0.0f};
    float target_y{0.0f};
    float target_z{0.0f};
    float tolerance_m{2.0f};
    float timeout_s{60.0f};
};

struct VehicleTelemetry {
    float pos_x{0.0f};
    float pos_y{0.0f};
    float pos_z{0.0f};
    float battery_v{24.0f};
    bool geofence_valid{true};
    bool ekf_healthy{true};
    bool obstacle_detected{false};
};

template <size_t MaxGoals = 8>
class MissionDispatcher {
public:
    constexpr MissionDispatcher() = default;

    bool enqueue(const GoalItem& item) noexcept {
        if (count_ >= MaxGoals) {
            return false;
        }
        items_[count_] = item;
        states_[count_] = GoalState::Pending;
        ++count_;
        return true;
    }

    void step(VehicleTelemetry& telem, float dt_s) noexcept {
        // 1. Екстрене реагування на раптову перешкоду
        if (telem.obstacle_detected && (active_idx_ >= 0)) {
            if (items_[static_cast<size_t>(active_idx_)].action != GoalAction::EmergencyReturn) {
                GoalItem emergency{
                    .id = 9999,
                    .action = GoalAction::EmergencyReturn,
                    .priority = 255,
                    .target_x = 0.0f,
                    .target_y = 0.0f,
                    .target_z = -30.0f,
                    .tolerance_m = 2.0f,
                    .timeout_s = 120.0f
                };
                enqueue(emergency);
            }
        }

        // 2. Пошук найпріоритетнішого кандидата
        int8_t candidate_idx = -1;
        uint8_t highest_prio = 0;

        if (active_idx_ >= 0) {
            highest_prio = items_[static_cast<size_t>(active_idx_)].priority;
            candidate_idx = active_idx_;
        }

        for (size_t i = 0; i < count_; ++i) {
            if (states_[i] == GoalState::Pending) {
                if (active_idx_ < 0 || items_[i].priority > highest_prio) {
                    highest_prio = items_[i].priority;
                    candidate_idx = static_cast<int8_t>(i);
                }
            }
        }

        // 3. Перемикання станів і витіснення
        if (candidate_idx >= 0 && candidate_idx != active_idx_) {
            if (active_idx_ >= 0) {
                states_[static_cast<size_t>(active_idx_)] = GoalState::Preempted;
                std::cout << "[DISPATCHER] Goal #" << items_[static_cast<size_t>(active_idx_)].id
                          << " PREEMPTED by higher priority goal #"
                          << items_[static_cast<size_t>(candidate_idx)].id << "\n";
            }

            if (check_preconditions(items_[static_cast<size_t>(candidate_idx)], telem)) {
                active_idx_ = candidate_idx;
                states_[static_cast<size_t>(candidate_idx)] = GoalState::Active;
                active_timer_s_ = 0.0f;
                std::cout << "[DISPATCHER] Goal #" << items_[static_cast<size_t>(candidate_idx)].id
                          << " ACTIVE (Priority: " << static_cast<int>(items_[static_cast<size_t>(candidate_idx)].priority)
                          << ", Target: [" << items_[static_cast<size_t>(candidate_idx)].target_x
                          << ", " << items_[static_cast<size_t>(candidate_idx)].target_y
                          << ", " << items_[static_cast<size_t>(candidate_idx)].target_z << "])\n";
            } else {
                states_[static_cast<size_t>(candidate_idx)] = GoalState::Rejected;
                std::cout << "[DISPATCHER] Goal #" << items_[static_cast<size_t>(candidate_idx)].id
                          << " REJECTED by pre-condition check\n";
                active_idx_ = -1;
                return;
            }
        }

        // 4. Оновлення та контроль завершення активного завдання
        if (active_idx_ >= 0) {
            auto& active_goal = items_[static_cast<size_t>(active_idx_)];
            active_timer_s_ += dt_s;

            if (active_goal.timeout_s > 0.0f && active_timer_s_ > active_goal.timeout_s) {
                states_[static_cast<size_t>(active_idx_)] = GoalState::Aborted;
                std::cout << "[DISPATCHER] Goal #" << active_goal.id
                          << " ABORTED due to timeout (" << active_timer_s_ << " s)\n";
                active_idx_ = -1;
                return;
            }

            const float dx = active_goal.target_x - telem.pos_x;
            const float dy = active_goal.target_y - telem.pos_y;
            const float dz = active_goal.target_z - telem.pos_z;
            const float dist_sq = dx * dx + dy * dy + dz * dz;

            if (dist_sq <= (active_goal.tolerance_m * active_goal.tolerance_m)) {
                states_[static_cast<size_t>(active_idx_)] = GoalState::Completed;
                std::cout << "[DISPATCHER] Goal #" << active_goal.id
                          << " COMPLETED successfully (Distance: " << std::sqrt(dist_sq) << " m)\n";
                active_idx_ = -1;
            }
        }
    }

    [[nodiscard]] std::span<const GoalState> states() const noexcept {
        return std::span<const GoalState>(states_.data(), count_);
    }

private:
    [[nodiscard]] static bool check_preconditions(const GoalItem& item, const VehicleTelemetry& telem) noexcept {
        if (!telem.ekf_healthy || !telem.geofence_valid) {
            return false;
        }
        if (item.action != GoalAction::EmergencyReturn && telem.battery_v < 21.0f) {
            return false;
        }
        return true;
    }

    std::array<GoalItem, MaxGoals> items_{};
    std::array<GoalState, MaxGoals> states_{};
    size_t count_{0};
    int8_t active_idx_{-1};
    float active_timer_s_{0.0f};
};

int main() {
    MissionDispatcher dispatcher;

    VehicleTelemetry telemetry{
        .pos_x = 0.0f,
        .pos_y = 0.0f,
        .pos_z = -10.0f,
        .battery_v = 24.2f,
        .geofence_valid = true,
        .ekf_healthy = true,
        .obstacle_detected = false
    };

    GoalItem survey_goal{
        .id = 101,
        .action = GoalAction::SurveyPolygon,
        .priority = 50,
        .target_x = 100.0f,
        .target_y = 50.0f,
        .target_z = -50.0f,
        .tolerance_m = 3.0f,
        .timeout_s = 60.0f
    };

    dispatcher.enqueue(survey_goal);

    std::cout << "=== СИМУЛЯЦІЯ АВТОНОМНОГО ДИСПЕТЧЕРА (C++) ===\n";
    const float dt = 1.0f;

    for (int step = 0; step < 10; ++step) {
        telemetry.pos_x += 10.0f;
        telemetry.pos_y += 5.0f;
        telemetry.pos_z -= 4.0f;

        if (step == 3) {
            std::cout << "\n--- ПОДІЯ: Сенсор виявив перешкоду на курсі! ---\n";
            telemetry.obstacle_detected = true;
        }

        dispatcher.step(telemetry, dt);
    }

    return 0;
}
