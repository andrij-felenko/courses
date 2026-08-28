#include <array>
#include <cmath>
#include <cstdint>
#include <optional>
#include <span>

enum class GoalType : uint8_t {
    Waypoint,
    SurveyArea,
    HoldPosition,
    EmergencyRth
};

enum class GoalState : uint8_t {
    Idle,
    Pending,
    Active,
    Preempted,
    Completed,
    Aborted,
    Rejected
};

struct Goal {
    uint32_t id{0};
    GoalType type{GoalType::Waypoint};
    uint8_t priority{0};        // 0 (найнижчий) .. 255 (найвищий)
    float target_x{0.0f};       // метри у світовій системі координат NED
    float target_y{0.0f};
    float target_z{0.0f};
    float acceptance_radius{1.0f};
    float timeout_sec{60.0f};
};

struct SystemState {
    float pos_x{0.0f};
    float pos_y{0.0f};
    float pos_z{0.0f};
    float battery_voltage{24.0f};
    bool is_geofence_ok{true};
    bool is_ekf_healthy{true};
};

template <size_t QueueCapacity = 8>
class GoalDispatcher {
public:
    constexpr GoalDispatcher() = default;

    bool push_goal(const Goal& new_goal) noexcept {
        if (count_ >= QueueCapacity) {
            return false;
        }
        queue_[count_] = new_goal;
        states_[count_] = GoalState::Pending;
        ++count_;
        return true;
    }

    void tick(const SystemState& sys, float dt_sec) noexcept {
        // 1. Пошук найвищого пріоритету серед PENDING або поточної ACTIVE
        int8_t best_index = -1;
        uint8_t highest_priority = 0;

        if (active_index_ >= 0) {
            highest_priority = queue_[static_cast<size_t>(active_index_)].priority;
            best_index = active_index_;
        }

        for (size_t i = 0; i < count_; ++i) {
            if (states_[i] == GoalState::Pending) {
                if (active_index_ < 0 || queue_[i].priority > highest_priority) {
                    highest_priority = queue_[i].priority;
                    best_index = static_cast<int8_t>(i);
                }
            }
        }

        // 2. Механізм витіснення (Preemption)
        if (best_index >= 0 && best_index != active_index_) {
            if (active_index_ >= 0) {
                states_[static_cast<size_t>(active_index_)] = GoalState::Preempted;
            }

            if (validate_goal(queue_[static_cast<size_t>(best_index)], sys)) {
                active_index_ = best_index;
                states_[static_cast<size_t>(best_index)] = GoalState::Active;
                active_elapsed_time_ = 0.0f;
            } else {
                states_[static_cast<size_t>(best_index)] = GoalState::Rejected;
                active_index_ = -1;
                return;
            }
        }

        // 3. Відпрацювання активної цілі
        if (active_index_ >= 0) {
            auto& cur = queue_[static_cast<size_t>(active_index_)];
            active_elapsed_time_ += dt_sec;

            if (cur.timeout_sec > 0.0f && active_elapsed_time_ > cur.timeout_sec) {
                states_[static_cast<size_t>(active_index_)] = GoalState::Aborted;
                active_index_ = -1;
                return;
            }

            const float dx = cur.target_x - sys.pos_x;
            const float dy = cur.target_y - sys.pos_y;
            const float dz = cur.target_z - sys.pos_z;
            const float dist_sq = dx * dx + dy * dy + dz * dz;

            if (dist_sq <= (cur.acceptance_radius * cur.acceptance_radius)) {
                states_[static_cast<size_t>(active_index_)] = GoalState::Completed;
                active_index_ = -1;
            }
        }
    }

    [[nodiscard]] std::optional<Goal> get_active_goal() const noexcept {
        if (active_index_ >= 0) {
            return queue_[static_cast<size_t>(active_index_)];
        }
        return std::nullopt;
    }

    [[nodiscard]] std::span<const GoalState> get_states() const noexcept {
        return std::span<const GoalState>(states_.data(), count_);
    }

private:
    [[nodiscard]] static bool validate_goal(const Goal& g, const SystemState& sys) noexcept {
        if (!sys.is_ekf_healthy || !sys.is_geofence_ok) {
            return false;
        }
        if (g.type != GoalType::EmergencyRth && sys.battery_voltage < 21.0f) {
            return false;
        }
        return true;
    }

    std::array<Goal, QueueCapacity> queue_{};
    std::array<GoalState, QueueCapacity> states_{};
    size_t count_{0};
    int8_t active_index_{-1};
    float active_elapsed_time_{0.0f};
};
