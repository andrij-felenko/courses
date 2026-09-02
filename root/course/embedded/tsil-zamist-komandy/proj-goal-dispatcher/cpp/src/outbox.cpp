#include "outbox.hpp"

namespace mission {

MissionEvent make_event(const GoalItem& goal, GoalState state) noexcept {
    MissionEvent ev{};
    ev.id = goal.id;
    ev.state = state;
    ev.target = goal.target;

    switch (state) {
    case GoalState::Active:
        // Наземна станція малює цю точку як поточну ціль місії.
        ev.msg = MavlinkMsg::MissionCurrent;
        ev.result = MavMissionResult::Accepted;
        break;
    case GoalState::Completed:
        ev.msg = MavlinkMsg::MissionItemReached;
        ev.result = MavMissionResult::Accepted;
        break;
    case GoalState::Pending:
        ev.msg = MavlinkMsg::MissionAck;
        ev.result = MavMissionResult::Accepted;
        break;
    case GoalState::Preempted:
        // Не помилка: завдання призупинили, воно ще повернеться.
        ev.msg = MavlinkMsg::MissionAck;
        ev.result = MavMissionResult::Cancelled;
        break;
    case GoalState::Rejected:
        ev.msg = MavlinkMsg::MissionAck;
        ev.result = MavMissionResult::Denied;
        break;
    case GoalState::Aborted:
    case GoalState::Empty:
        ev.msg = MavlinkMsg::MissionAck;
        ev.result = MavMissionResult::Error;
        break;
    }
    return ev;
}

MissionEvent make_no_space_event(const GoalItem& goal) noexcept {
    MissionEvent ev = make_event(goal, GoalState::Rejected);
    ev.result = MavMissionResult::NoSpace;
    return ev;
}

bool Outbox::push(const MissionEvent& ev) noexcept {
    // head рухаємо тільки ми, тому читаємо його без бар'єра;
    // tail пише споживач — його забираємо з acquire.
    const std::uint32_t head = head_.load(std::memory_order_relaxed);
    const std::uint32_t tail = tail_.load(std::memory_order_acquire);

    if (head - tail >= kCapacity) {
        // Споживач не встигає. Подію втрачаємо, але рахуємо: зупиняти
        // керування через зайнятий канал зв'язку не можна.
        dropped_.fetch_add(1, std::memory_order_relaxed);
        return false;
    }

    slots_[head & (kCapacity - 1)] = ev;
    // release: запис у слот мусить стати видимим раніше за новий head.
    head_.store(head + 1, std::memory_order_release);
    return true;
}

std::optional<MissionEvent> Outbox::pop() noexcept {
    const std::uint32_t tail = tail_.load(std::memory_order_relaxed);
    const std::uint32_t head = head_.load(std::memory_order_acquire);

    if (tail == head) {
        return std::nullopt;
    }

    const MissionEvent ev = slots_[tail & (kCapacity - 1)];
    tail_.store(tail + 1, std::memory_order_release);
    return ev;
}

}  // namespace mission
