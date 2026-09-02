#ifndef BRIDGE_H
#define BRIDGE_H

#include <stdatomic.h>

#include "goal_types.h"

/* Номери повідомлень MAVLink Mission Protocol — сталі самого протоколу. */
#define MAVLINK_MSG_ID_MISSION_CURRENT      42
#define MAVLINK_MSG_ID_MISSION_ITEM_REACHED 46
#define MAVLINK_MSG_ID_MISSION_ACK          47

/* MAV_MISSION_RESULT — код у полі type пакета MISSION_ACK. */
#define MAV_MISSION_ACCEPTED             0
#define MAV_MISSION_ERROR                1
#define MAV_MISSION_NO_SPACE             4
#define MAV_MISSION_DENIED              13
#define MAV_MISSION_OPERATION_CANCELLED 14

/* Місткість черги подій. Степінь двійки — щоб індекс брався маскою,
   а не діленням: на Cortex-M ділення коштує десятки тактів. */
#define OUTBOX_CAPACITY 16u

/* Готовий до пакування зріз переходу скінченного автомата.
   Саме пакування робить згенерована бібліотека MAVLink уже в потоці зв'язку. */
typedef struct {
    uint32_t goal_id;
    GoalState_e state;
    uint16_t msg_id;   /* яке повідомлення піде в ефір */
    uint8_t result;    /* MAV_MISSION_RESULT для MISSION_ACK */
    float x;
    float y;
    float z;
} MissionEvent_t;

/* Односторонній міст диспетчер → потік телеметрії. Один виробник, один
   споживач, жодного м'ютекса: крок диспетчера не має права заблокуватися
   на зайнятому радіоканалі. */
typedef struct {
    MissionEvent_t slots[OUTBOX_CAPACITY];
    atomic_uint head;    /* рухає лише виробник */
    atomic_uint tail;    /* рухає лише споживач */
    atomic_uint dropped; /* скільки подій не влізло */
} MissionOutbox_t;

void outbox_init(MissionOutbox_t *box);
bool outbox_push(MissionOutbox_t *box, const MissionEvent_t *ev);
bool outbox_pop(MissionOutbox_t *box, MissionEvent_t *out);
uint32_t outbox_dropped(const MissionOutbox_t *box);

MissionEvent_t bridge_event(const GoalItem_t *goal, GoalState_e state);
MissionEvent_t bridge_event_no_space(const GoalItem_t *goal);

const char *goal_state_name(GoalState_e state);

#endif /* BRIDGE_H */
