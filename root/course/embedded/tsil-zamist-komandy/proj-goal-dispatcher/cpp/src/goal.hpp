#pragma once

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace mission {

// Розмір бортової черги. Пам'ять під неї відводить компонувальник:
// купи на борту немає взагалі, тож немає й пауз менеджера пам'яті.
inline constexpr std::size_t kMaxGoals = 8;

// Нижня межа напруги акумулятора: під нею дозволено лише повернення додому.
inline constexpr float kBatteryMinV = 21.0f;

// Гістерезис витіснення (ΔP): нова ціль мусить бути щонайменше на стільки
// пріоритетнішою за активну, інакше два сусідні за вагою завдання
// перекидатимуть керування одне одному кожен такт.
inline constexpr int kPreemptHysteresis = 5;

// Точка у світовій системі NED, метри.
struct Vec3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] float distance_to(const Vec3& other) const noexcept {
        const float dx = x - other.x;
        const float dy = y - other.y;
        const float dz = z - other.z;
        return std::sqrt(dx * dx + dy * dy + dz * dz);
    }
};

enum class GoalAction : std::uint8_t {
    NavigateWaypoint,
    SurveyPolygon,
    LoiterPosition,
    EmergencyReturn
};

enum class GoalState : std::uint8_t {
    Empty,
    Pending,
    Active,
    Preempted,
    Completed,
    Aborted,
    Rejected
};

// Стани, з яких ціль уже не повернеться в роботу.
[[nodiscard]] constexpr bool is_terminal(GoalState state) noexcept {
    return state == GoalState::Completed || state == GoalState::Aborted ||
           state == GoalState::Rejected;
}

[[nodiscard]] constexpr std::string_view to_string(GoalState state) noexcept {
    switch (state) {
    case GoalState::Empty:     return "EMPTY";
    case GoalState::Pending:   return "PENDING";
    case GoalState::Active:    return "ACTIVE";
    case GoalState::Preempted: return "PREEMPTED";
    case GoalState::Completed: return "COMPLETED";
    case GoalState::Aborted:   return "ABORTED";
    case GoalState::Rejected:  return "REJECTED";
    }
    return "?";
}

// Незмінний дескриптор цілі: диспетчер його лише читає.
struct GoalItem {
    std::uint32_t id{0};
    GoalAction action{GoalAction::NavigateWaypoint};
    std::uint8_t priority{0};  // 0..255
    Vec3 target{};
    float tolerance_m{2.0f};   // радіус, у якому ціль вважається досягнутою
    float timeout_s{0.0f};     // ліміт часу; 0 — без ліміту
};

// Миттєвий зріз стану апарата: навігаційний фільтр, батарея, далекоміри.
struct VehicleTelemetry {
    Vec3 position{};
    float battery_v{24.0f};
    bool geofence_valid{true};
    bool ekf_healthy{true};
    bool obstacle_detected{false};
};

// Що диспетчер віддає планувальнику траєкторії цього такту.
enum class OutputMode : std::uint8_t {
    Idle,   // активної цілі немає — тримати позицію
    Track,  // вести апарат у точку setpoint
    Hold,   // аварійне зависання: навігація недостовірна
    Land    // посадка на місці: навігації немає й батарея на межі
};

struct DispatcherOutput {
    OutputMode mode{OutputMode::Idle};
    std::uint32_t goal_id{0};
    Vec3 setpoint{};
};

}  // namespace mission
