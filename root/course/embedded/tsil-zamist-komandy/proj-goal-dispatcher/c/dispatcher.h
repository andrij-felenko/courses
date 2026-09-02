#ifndef DISPATCHER_H
#define DISPATCHER_H

#include "bridge.h"
#include "goal_types.h"

/* Увесь стан диспетчера — три паралельні масиви фіксованої довжини,
   індекс активної цілі й лічильники часу. Ніяких зв'язних списків:
   під час перегляду черги лінійка кеша тягне весь масив за одне звернення. */
typedef struct {
    GoalItem_t items[MAX_GOALS];
    GoalState_e states[MAX_GOALS];
    float elapsed_s[MAX_GOALS];   /* витіснена ціль зберігає свій прогрес тут */
    uint8_t count;
    int8_t active_idx;            /* -1 — активної цілі немає */
    MissionOutbox_t *outbox;      /* міст телеметрії; NULL допустимий */
} MissionDispatcher_t;

void mission_dispatcher_init(MissionDispatcher_t *disp, MissionOutbox_t *outbox);

/* false — черга насичена й витіснити нікого; про відмову йде MISSION_ACK. */
bool mission_dispatcher_enqueue(MissionDispatcher_t *disp, const GoalItem_t *item);

/* Один такт диспетчера. Викликається з таймерного такту навігації (10–20 Гц),
   містить лише O(N) перевірок масиву й нічого не блокує. */
DispatcherOutput_t mission_dispatcher_step(MissionDispatcher_t *disp,
                                           const VehicleTelemetry_t *telem,
                                           float dt_s);

GoalState_e mission_dispatcher_state_of(const MissionDispatcher_t *disp, uint32_t goal_id);

#endif /* DISPATCHER_H */
