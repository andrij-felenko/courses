#include "dispatcher.hpp"

namespace mission {
namespace {

// Ціль аварійного відходу: фіксований ідентифікатор, найвищий пріоритет
// і точка збору над домом.
constexpr GoalItem kEmergencyReturn{
    .id = 9999,
    .action = GoalAction::EmergencyReturn,
    .priority = 255,
    .target = Vec3{0.0f, 0.0f, -30.0f},
    .tolerance_m = 2.0f,
    .timeout_s = 120.0f
};

}  // namespace

void MissionDispatcher::emit(std::size_t idx, GoalState state) noexcept {
    outbox_.push(make_event(items_[idx], state));
}

// Прибирає завершені слоти, зсуваючи живі до початку масиву.
// Індекс активної цілі переїжджає разом з нею.
void MissionDispatcher::compact() noexcept {
    std::size_t dst = 0;
    std::optional<std::size_t> new_active{};

    for (std::size_t src = 0; src < count_; ++src) {
        if (states_[src] == GoalState::Empty || is_terminal(states_[src])) {
            continue;
        }
        if (active_ && *active_ == src) {
            new_active = dst;
        }
        items_[dst] = items_[src];
        states_[dst] = states_[src];
        elapsed_s_[dst] = elapsed_s_[src];
        ++dst;
    }

    for (std::size_t i = dst; i < kMaxGoals; ++i) {
        states_[i] = GoalState::Empty;
        elapsed_s_[i] = 0.0f;
    }
    count_ = dst;
    active_ = new_active;
}

// Місця немає навіть після прибирання: віддаємо слот найслабшого завдання,
// що лише чекає або призупинене. Активну ціль не чіпаємо ніколи.
bool MissionDispatcher::evict_weakest(std::uint8_t priority) noexcept {
    std::optional<std::size_t> victim{};

    for (std::size_t i = 0; i < count_; ++i) {
        if (states_[i] != GoalState::Pending && states_[i] != GoalState::Preempted) {
            continue;
        }
        if (items_[i].priority >= priority) {
            continue;
        }
        if (!victim || items_[i].priority < items_[*victim].priority) {
            victim = i;
        }
    }

    if (!victim) {
        return false;
    }

    states_[*victim] = GoalState::Aborted;
    emit(*victim, GoalState::Aborted);
    compact();
    return true;
}

std::optional<std::size_t> MissionDispatcher::enqueue(const GoalItem& item) noexcept {
    if (count_ >= kMaxGoals) {
        compact();
    }
    if (count_ >= kMaxGoals && !evict_weakest(item.priority)) {
        // Усі, хто в черзі, важливіші за новачка — відмовляємо вголос, щоб
        // оператор побачив причину, а не мовчазну втрату команди.
        outbox_.push(make_no_space_event(item));
        return std::nullopt;
    }

    const std::size_t idx = count_;
    items_[idx] = item;
    states_[idx] = GoalState::Pending;
    elapsed_s_[idx] = 0.0f;
    emit(idx, GoalState::Pending);
    ++count_;
    return idx;
}

// Передстартова перевірка: чи взагалі можна вмикати цю ціль зараз.
bool MissionDispatcher::preconditions_met(const GoalItem& item,
                                          const VehicleTelemetry& telem) noexcept {
    if (!telem.ekf_healthy || !telem.geofence_valid) {
        return false;
    }
    // Повернення додому дозволене й на майже порожній батареї — воно єдине,
    // що ще має сенс у такому стані.
    if (item.action != GoalAction::EmergencyReturn && telem.battery_v < kBatteryMinV) {
        return false;
    }
    return true;
}

// Найпріоритетніший кандидат серед тих, хто чекає або був призупинений.
// Ті, що не проходять передстартову перевірку, відсіюються тут-таки: інакше
// диспетчер щотакту повертався б до завідомо неможливої цілі.
std::optional<std::size_t> MissionDispatcher::select_candidate(const VehicleTelemetry& telem) noexcept {
    for (;;) {
        std::optional<std::size_t> best{};

        for (std::size_t i = 0; i < count_; ++i) {
            if (states_[i] != GoalState::Pending && states_[i] != GoalState::Preempted) {
                continue;
            }
            if (!best || items_[i].priority > items_[*best].priority) {
                best = i;
            }
        }

        if (!best) {
            return std::nullopt;
        }
        if (preconditions_met(items_[*best], telem)) {
            return best;
        }

        states_[*best] = GoalState::Rejected;
        emit(*best, GoalState::Rejected);
    }
}

void MissionDispatcher::activate(std::size_t idx) noexcept {
    active_ = idx;
    states_[idx] = GoalState::Active;
    // elapsed_s_ НЕ скидаємо: витіснена ціль повертається з накопиченим часом,
    // інакше довге завдання можна було б безкінечно перезапускати з нуля.
    emit(idx, GoalState::Active);
}

bool MissionDispatcher::has_live_emergency() const noexcept {
    for (std::size_t i = 0; i < count_; ++i) {
        if (items_[i].action != GoalAction::EmergencyReturn) {
            continue;
        }
        if (states_[i] != GoalState::Empty && !is_terminal(states_[i])) {
            return true;
        }
    }
    return false;
}

DispatcherOutput MissionDispatcher::step(const VehicleTelemetry& telem, float dt_s) noexcept {
    DispatcherOutput out{};

    // 1. Навігація втрачена. Просторова ціль без достовірної позиції — це політ
    //    у невідомість: активну знімаємо (зберігши прогрес), нових не вмикаємо,
    //    апарат тримає висоту або сідає на місці.
    if (!telem.ekf_healthy) {
        if (active_) {
            states_[*active_] = GoalState::Preempted;
            emit(*active_, GoalState::Preempted);
            active_.reset();
        }
        out.mode = (telem.battery_v < kBatteryMinV) ? OutputMode::Land : OutputMode::Hold;
        return out;
    }

    // 2. Хто має право на керування цього такту.
    if (const auto candidate = select_candidate(telem); candidate) {
        if (!active_) {
            activate(*candidate);
        } else if (static_cast<int>(items_[*candidate].priority) >=
                   static_cast<int>(items_[*active_].priority) + kPreemptHysteresis) {
            const std::size_t old_idx = *active_;
            states_[old_idx] = GoalState::Preempted;
            emit(old_idx, GoalState::Preempted);
            activate(*candidate);
        }
    }

    // 3. Ведення активної цілі: спершу час, потім відстань.
    if (active_) {
        const std::size_t idx = *active_;
        const GoalItem& goal = items_[idx];
        elapsed_s_[idx] += dt_s;

        if (goal.timeout_s > 0.0f && elapsed_s_[idx] > goal.timeout_s) {
            // Ціль зависла: далі її тримати — значить блокувати чергу назавжди.
            states_[idx] = GoalState::Aborted;
            emit(idx, GoalState::Aborted);
            active_.reset();
        } else if (goal.target.distance_to(telem.position) <= goal.tolerance_m) {
            states_[idx] = GoalState::Completed;
            emit(idx, GoalState::Completed);
            active_.reset();
        } else {
            out.mode = OutputMode::Track;
            out.goal_id = goal.id;
            out.setpoint = goal.target;
        }
    }

    // 4. Реактивний шар. Далекомір побачив перешкоду — ставимо в чергу ціль
    //    аварійного відходу. Керування вона дістане наступного такту, пройшовши
    //    ту саму передстартову перевірку, що й планові: жодних чорних ходів.
    if (telem.obstacle_detected && !has_live_emergency()) {
        enqueue(kEmergencyReturn);
    }

    return out;
}

GoalState MissionDispatcher::state_of(std::uint32_t goal_id) const noexcept {
    for (std::size_t i = 0; i < count_; ++i) {
        if (items_[i].id == goal_id) {
            return states_[i];
        }
    }
    return GoalState::Empty;
}

}  // namespace mission
