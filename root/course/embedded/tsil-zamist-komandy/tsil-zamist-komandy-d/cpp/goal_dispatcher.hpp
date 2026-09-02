#pragma once

// Диспетчер автономних цілей: черга фіксованого розміру, скінченний автомат
// життєвого циклу, витіснення за пріоритетом і зв'язок із планувальниками.

#include <array>
#include <cstddef>
#include <expected>
#include <optional>

#include "flight_envelope.hpp"

namespace autonomy {

enum class SubmitError : std::uint8_t { QueueFull };

class GoalDispatcher {
public:
    static constexpr std::size_t kCapacity = 8;

    // Що диспетчер каже польотному контуру на цьому такті.
    struct Command {
        GoalId goal{GoalId::None};
        GoalType type{GoalType::Waypoint};
        Vec3 setpoint{};
        bool replan_requested{false}; // глобальному планувальнику: перерахуй маршрут
    };

    // Зріз для телеметрії: що сталося з конкретною ціллю.
    struct Status {
        GoalId id{GoalId::None};
        GoalState state{GoalState::Free};
        Priority priority{Priority::Mission};
        Seconds elapsed{0.0F};
        std::optional<RejectReason> verdict{};
    };

    explicit GoalDispatcher(FlightEnvelope env) noexcept : env_{env} {}

    [[nodiscard]] std::expected<GoalId, SubmitError> submit(const Goal& g) noexcept;

    // Один такт диспетчеризації (0.5–2 Гц вистачає). Порожній результат —
    // активної цілі немає, апарат тримає позицію.
    [[nodiscard]] std::optional<Command> tick(const Vehicle& v, Seconds dt) noexcept;

    // Локальний контролер побачив, що прохід заблоковано наглухо.
    void report_path_blocked() noexcept;

    // Оператор знімає ціль.
    bool cancel(GoalId id) noexcept;

    [[nodiscard]] std::optional<Status> status_of(GoalId id) const noexcept;
    [[nodiscard]] std::optional<Goal> active_goal() const noexcept;

private:
    struct Slot {
        Goal goal{};
        GoalState state{GoalState::Free};
        Seconds elapsed{0.0F};       // переживає витіснення
        Vec3 resume_from{};          // точка, де ціль перервали
        std::uint8_t replans{0};
        bool replan_pending{false};
        std::optional<RejectReason> verdict{};
    };

    [[nodiscard]] std::optional<std::size_t> allocate_slot(Priority priority) noexcept;
    [[nodiscard]] std::optional<std::size_t> pick_candidate() const noexcept;
    [[nodiscard]] bool may_preempt(std::size_t candidate) const noexcept;
    void handle_failures(const Vehicle& v) noexcept;
    void arm_emergency(const Vehicle& v) noexcept;
    void consider_candidate(const Vehicle& v) noexcept;
    [[nodiscard]] std::optional<Command> advance_active(const Vehicle& v, Seconds dt) noexcept;
    void finish_active(GoalState state, std::optional<RejectReason> verdict) noexcept;

    std::array<Slot, kCapacity> slots_{};
    FlightEnvelope env_{};
    std::optional<std::size_t> active_{};
    Seconds hold_{0.0F}; // скільки активна ціль тримається (таймер утримання)
    std::uint32_t next_id_{1};
    bool emergency_armed_{false};
};

} // namespace autonomy
