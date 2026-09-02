#include "goal_dispatcher.hpp"

#include <utility>

namespace autonomy {
namespace {

// Ліки від гойдалки пріоритетів (Goal Thrashing): нова ціль мусить перевищити
// активну щонайменше на цю дельту, а щойно активовану ціль не витісняємо перші
// три секунди. Виняток один — аварійний пріоритет 255.
constexpr int kPreemptHysteresis = 10;
constexpr Seconds kHoldDown = 3.0F;

// Скільки разів локальний контролер має право попросити обхід.
constexpr std::uint8_t kMaxReplans = 3;

// У скільки разів дисперсія EKF має перевищити допуск, щоб політ по
// координатах вважався безглуздим.
constexpr float kEkfPanicFactor = 4.0F;

[[nodiscard]] constexpr bool is_terminal(GoalState s) noexcept
{
    return s == GoalState::Completed || s == GoalState::Aborted || s == GoalState::Rejected;
}

// Витіснена ціль повертається в конкуренцію нарівні з тими, що чекають.
[[nodiscard]] constexpr bool is_waiting(GoalState s) noexcept
{
    return s == GoalState::Pending || s == GoalState::Preempted;
}

} // namespace

std::optional<std::size_t> GoalDispatcher::allocate_slot(Priority priority) noexcept
{
    for (std::size_t i = 0; i < kCapacity; ++i) {
        if (slots_[i].state == GoalState::Free) {
            return i;
        }
    }
    for (std::size_t i = 0; i < kCapacity; ++i) {
        if (is_terminal(slots_[i].state)) {
            return i; // завершену ціль тримаємо лише заради звіту
        }
    }
    if (priority != Priority::Emergency) {
        return std::nullopt;
    }
    // Аварійній цілі поступається найменш пріоритетна з тих, що ще чекають.
    std::optional<std::size_t> victim;
    for (std::size_t i = 0; i < kCapacity; ++i) {
        if (!is_waiting(slots_[i].state)) {
            continue;
        }
        if (!victim || raw(slots_[i].goal.priority) < raw(slots_[*victim].goal.priority)) {
            victim = i;
        }
    }
    return victim;
}

std::expected<GoalId, SubmitError> GoalDispatcher::submit(const Goal& g) noexcept
{
    const auto idx = allocate_slot(g.priority);
    if (!idx) {
        return std::unexpected(SubmitError::QueueFull);
    }

    Slot fresh{};
    fresh.goal = g;
    fresh.goal.id = static_cast<GoalId>(next_id_++);
    fresh.state = GoalState::Pending;
    slots_[*idx] = fresh;
    return fresh.goal.id;
}

std::optional<GoalDispatcher::Status> GoalDispatcher::status_of(GoalId id) const noexcept
{
    if (id == GoalId::None) {
        return std::nullopt;
    }
    for (const Slot& s : slots_) {
        if (s.state != GoalState::Free && s.goal.id == id) {
            return Status{s.goal.id, s.state, s.goal.priority, s.elapsed, s.verdict};
        }
    }
    return std::nullopt;
}

std::optional<Goal> GoalDispatcher::active_goal() const noexcept
{
    if (!active_) {
        return std::nullopt;
    }
    return slots_[*active_].goal;
}

void GoalDispatcher::finish_active(GoalState state, std::optional<RejectReason> verdict) noexcept
{
    Slot& s = slots_[*active_];
    s.state = state;
    s.verdict = verdict;
    s.replan_pending = false;
    active_.reset();
    hold_ = 0.0F;
}

bool GoalDispatcher::cancel(GoalId id) noexcept
{
    for (std::size_t i = 0; i < kCapacity; ++i) {
        Slot& s = slots_[i];
        if (s.state == GoalState::Free || s.goal.id != id) {
            continue;
        }
        if (s.state == GoalState::Active) {
            finish_active(GoalState::Aborted, RejectReason::Cancelled);
        } else if (is_waiting(s.state)) {
            s.state = GoalState::Rejected;
            s.verdict = RejectReason::Cancelled;
        } else {
            return false; // ціль уже завершена, скасовувати нічого
        }
        return true;
    }
    return false;
}

void GoalDispatcher::handle_failures(const Vehicle& v) noexcept
{
    if (!active_) {
        return;
    }
    // Критична відмова на ходу знімає поточну ціль: летіти далі по зіпсованих
    // давачах гірше, ніж зупинитися. Аварійну ціль не знімає ніщо.
    if (slots_[*active_].goal.priority == Priority::Emergency) {
        return;
    }
    if (!v.sensors_ok) {
        finish_active(GoalState::Aborted, RejectReason::SensorFailure);
    } else if (!v.motors_ok) {
        finish_active(GoalState::Aborted, RejectReason::MotorFailure);
    }
}

void GoalDispatcher::arm_emergency(const Vehicle& v) noexcept
{
    if (emergency_armed_) {
        return;
    }

    Goal g{};
    const bool nav_broken = v.ekf_pos_variance > env_.ekf_variance_limit * kEkfPanicFactor;

    if (!v.sensors_ok || !v.motors_ok || nav_broken) {
        // Летіти додому по зламаній оцінці позиції нікуди: тримаємо точку
        // й віддаємо рішення операторові.
        g.type = GoalType::HoldPosition;
        g.target = v.pos;
        g.timeout = 30.0F;
    } else if (v.battery_voltage < env_.rth_voltage) {
        g.type = GoalType::EmergencyRth;
        g.target = env_.home;
        g.timeout = 0.0F;
    } else {
        return;
    }

    g.priority = Priority::Emergency;
    g.acceptance_radius = 2.0F;
    g.cruise_airspeed = env_.rth_airspeed;
    emergency_armed_ = submit(g).has_value();
}

std::optional<std::size_t> GoalDispatcher::pick_candidate() const noexcept
{
    // Рівні пріоритети розводить порядок у черзі — інакше два однакові
    // завдання мінялися б місцями щотакту.
    std::optional<std::size_t> best;
    for (std::size_t i = 0; i < kCapacity; ++i) {
        if (!is_waiting(slots_[i].state)) {
            continue;
        }
        if (!best || raw(slots_[i].goal.priority) > raw(slots_[*best].goal.priority)) {
            best = i;
        }
    }
    return best;
}

bool GoalDispatcher::may_preempt(std::size_t candidate) const noexcept
{
    if (!active_) {
        return true;
    }
    const Slot& current = slots_[*active_];
    const Slot& cand = slots_[candidate];

    if (cand.goal.priority == Priority::Emergency) {
        return true; // аварію не стримує ні гістерезис, ні таймер утримання
    }
    if (hold_ < kHoldDown) {
        return false;
    }
    return raw(cand.goal.priority) >= raw(current.goal.priority) + kPreemptHysteresis;
}

void GoalDispatcher::consider_candidate(const Vehicle& v) noexcept
{
    const auto candidate = pick_candidate();
    if (!candidate || candidate == active_ || !may_preempt(*candidate)) {
        return;
    }

    Slot& cand = slots_[*candidate];
    cand.state = GoalState::Validating;

    // Валідація ДО витіснення. Якщо зробити навпаки (спершу зняти активну,
    // потім перевіряти нову), невдалий допуск лишить апарат узагалі без цілі —
    // з місією в Preempted і без заміни.
    const auto verdict = preflight(cand.goal, v, env_);
    if (!verdict) {
        cand.verdict = verdict.error();
        cand.state = is_critical(verdict.error()) ? GoalState::Aborted : GoalState::Rejected;
        return; // активну ціль не чіпаємо
    }
    cand.verdict.reset();

    if (active_) {
        Slot& old = slots_[*active_];
        old.state = GoalState::Preempted;
        old.resume_from = v.pos; // прогрес і точка переривання лишаються в слоті
        old.replan_pending = false;
    }

    active_ = candidate;
    cand.state = GoalState::Active;
    cand.replan_pending = true; // нова активна ціль — новий глобальний маршрут
    hold_ = 0.0F;
}

std::optional<GoalDispatcher::Command> GoalDispatcher::advance_active(const Vehicle& v,
                                                                      Seconds dt) noexcept
{
    if (!active_) {
        return std::nullopt;
    }
    Slot& s = slots_[*active_];
    s.elapsed += dt;
    hold_ += dt;

    if (s.goal.timeout > 0.0F && s.elapsed > s.goal.timeout) {
        finish_active(GoalState::Aborted, RejectReason::Timeout);
        return std::nullopt;
    }

    // Утримання точки не «досягається» — його знімає таймаут або витіснення.
    if (s.goal.type != GoalType::HoldPosition &&
        norm(s.goal.target - v.pos) <= s.goal.acceptance_radius) {
        finish_active(GoalState::Completed, std::nullopt);
        return std::nullopt;
    }

    return Command{s.goal.id, s.goal.type, s.goal.target, std::exchange(s.replan_pending, false)};
}

std::optional<GoalDispatcher::Command> GoalDispatcher::tick(const Vehicle& v, Seconds dt) noexcept
{
    if (dt < 0.0F) {
        return std::nullopt;
    }
    handle_failures(v);
    arm_emergency(v);
    consider_candidate(v);
    return advance_active(v, dt);
}

void GoalDispatcher::report_path_blocked() noexcept
{
    if (!active_) {
        return;
    }
    Slot& s = slots_[*active_];
    ++s.replans;
    if (s.replans > kMaxReplans) {
        // Тричі шукали обхід і не знайшли: ціль недосяжна, знімаємо її й
        // віддаємо чергу наступній. Штурмувати стіну апарат не буде.
        finish_active(GoalState::Aborted, RejectReason::PathBlocked);
        return;
    }
    s.replan_pending = true; // глобальний планувальник перерахує в обхід
}

} // namespace autonomy
