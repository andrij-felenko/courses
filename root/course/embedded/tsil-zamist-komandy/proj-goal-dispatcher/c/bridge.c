#include "bridge.h"

#define OUTBOX_MASK (OUTBOX_CAPACITY - 1u)

static const char *const kStateNames[] = {
    "EMPTY", "PENDING", "ACTIVE", "PREEMPTED", "COMPLETED", "ABORTED", "REJECTED"
};

const char *goal_state_name(GoalState_e state) {
    const unsigned idx = (unsigned)state;
    if (idx >= sizeof kStateNames / sizeof kStateNames[0]) {
        return "?";
    }
    return kStateNames[idx];
}

MissionEvent_t bridge_event(const GoalItem_t *goal, GoalState_e state) {
    MissionEvent_t ev;
    ev.goal_id = goal->id;
    ev.state = state;
    ev.x = goal->target_x;
    ev.y = goal->target_y;
    ev.z = goal->target_z;

    switch (state) {
    case STATE_ACTIVE:
        /* Наземна станція малює цю точку як поточну ціль місії. */
        ev.msg_id = MAVLINK_MSG_ID_MISSION_CURRENT;
        ev.result = MAV_MISSION_ACCEPTED;
        break;
    case STATE_COMPLETED:
        ev.msg_id = MAVLINK_MSG_ID_MISSION_ITEM_REACHED;
        ev.result = MAV_MISSION_ACCEPTED;
        break;
    case STATE_PENDING:
        ev.msg_id = MAVLINK_MSG_ID_MISSION_ACK;
        ev.result = MAV_MISSION_ACCEPTED;
        break;
    case STATE_PREEMPTED:
        /* Не помилка: завдання призупинили, воно ще повернеться. */
        ev.msg_id = MAVLINK_MSG_ID_MISSION_ACK;
        ev.result = MAV_MISSION_OPERATION_CANCELLED;
        break;
    case STATE_REJECTED:
        ev.msg_id = MAVLINK_MSG_ID_MISSION_ACK;
        ev.result = MAV_MISSION_DENIED;
        break;
    case STATE_ABORTED:
    case STATE_EMPTY:
    default:
        ev.msg_id = MAVLINK_MSG_ID_MISSION_ACK;
        ev.result = MAV_MISSION_ERROR;
        break;
    }
    return ev;
}

MissionEvent_t bridge_event_no_space(const GoalItem_t *goal) {
    MissionEvent_t ev = bridge_event(goal, STATE_REJECTED);
    ev.result = MAV_MISSION_NO_SPACE;
    return ev;
}

void outbox_init(MissionOutbox_t *box) {
    atomic_init(&box->head, 0u);
    atomic_init(&box->tail, 0u);
    atomic_init(&box->dropped, 0u);
}

bool outbox_push(MissionOutbox_t *box, const MissionEvent_t *ev) {
    /* head рухаємо тільки ми, тому читаємо його без бар'єра;
       tail пише споживач — його забираємо з acquire. */
    const unsigned head = atomic_load_explicit(&box->head, memory_order_relaxed);
    const unsigned tail = atomic_load_explicit(&box->tail, memory_order_acquire);

    if ((unsigned)(head - tail) >= OUTBOX_CAPACITY) {
        /* Споживач не встигає. Подію втрачаємо, але рахуємо: зупиняти
           керування через зайнятий канал зв'язку не можна. */
        atomic_fetch_add_explicit(&box->dropped, 1u, memory_order_relaxed);
        return false;
    }

    box->slots[head & OUTBOX_MASK] = *ev;
    /* release: запис у слот мусить стати видимим раніше за новий head. */
    atomic_store_explicit(&box->head, head + 1u, memory_order_release);
    return true;
}

bool outbox_pop(MissionOutbox_t *box, MissionEvent_t *out) {
    const unsigned tail = atomic_load_explicit(&box->tail, memory_order_relaxed);
    const unsigned head = atomic_load_explicit(&box->head, memory_order_acquire);

    if (tail == head) {
        return false;
    }

    *out = box->slots[tail & OUTBOX_MASK];
    atomic_store_explicit(&box->tail, tail + 1u, memory_order_release);
    return true;
}

uint32_t outbox_dropped(const MissionOutbox_t *box) {
    /* Читання лічильника нікого не синхронізує — доречний relaxed. */
    return atomic_load_explicit((atomic_uint *)&box->dropped, memory_order_relaxed);
}
