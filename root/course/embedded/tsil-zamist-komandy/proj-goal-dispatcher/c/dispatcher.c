#include "dispatcher.h"

/* Ціль аварійного відходу народжується просто тут: у неї фіксований
   ідентифікатор, найвищий пріоритет і точка збору над домом. */
static const GoalItem_t kEmergencyReturn = {
    .id = 9999,
    .action = GOAL_EMERGENCY_RETURN,
    .priority = 255,
    .target_x = 0.0f,
    .target_y = 0.0f,
    .target_z = -30.0f,
    .tolerance_m = 2.0f,
    .timeout_s = 120.0f
};

static void emit(MissionDispatcher_t *disp, uint8_t idx, GoalState_e state) {
    if (disp->outbox == NULL) {
        return;
    }
    const MissionEvent_t ev = bridge_event(&disp->items[idx], state);
    outbox_push(disp->outbox, &ev);
}

void mission_dispatcher_init(MissionDispatcher_t *disp, MissionOutbox_t *outbox) {
    disp->count = 0;
    disp->active_idx = -1;
    disp->outbox = outbox;
    for (uint8_t i = 0; i < MAX_GOALS; i++) {
        disp->states[i] = STATE_EMPTY;
        disp->elapsed_s[i] = 0.0f;
    }
}

/* Прибирає завершені слоти, зсуваючи живі до початку масиву.
   Індекс активної цілі переїжджає разом з нею. */
static void dispatcher_compact(MissionDispatcher_t *disp) {
    uint8_t dst = 0;
    int8_t new_active = -1;

    for (uint8_t src = 0; src < disp->count; src++) {
        if (disp->states[src] == STATE_EMPTY || goal_state_is_terminal(disp->states[src])) {
            continue;
        }
        if (disp->active_idx >= 0 && src == (uint8_t)disp->active_idx) {
            new_active = (int8_t)dst;
        }
        disp->items[dst] = disp->items[src];
        disp->states[dst] = disp->states[src];
        disp->elapsed_s[dst] = disp->elapsed_s[src];
        dst++;
    }

    for (uint8_t i = dst; i < MAX_GOALS; i++) {
        disp->states[i] = STATE_EMPTY;
        disp->elapsed_s[i] = 0.0f;
    }
    disp->count = dst;
    disp->active_idx = new_active;
}

/* Місця немає навіть після прибирання: віддаємо слот найслабшого завдання,
   що лише чекає або призупинене. Активну ціль не чіпаємо ніколи. */
static bool dispatcher_evict_weakest(MissionDispatcher_t *disp, uint8_t priority) {
    int8_t victim = -1;

    for (uint8_t i = 0; i < disp->count; i++) {
        if (disp->states[i] != STATE_PENDING && disp->states[i] != STATE_PREEMPTED) {
            continue;
        }
        if (disp->items[i].priority >= priority) {
            continue;
        }
        if (victim < 0 || disp->items[i].priority < disp->items[victim].priority) {
            victim = (int8_t)i;
        }
    }

    if (victim < 0) {
        return false;
    }

    disp->states[victim] = STATE_ABORTED;
    emit(disp, (uint8_t)victim, STATE_ABORTED);
    dispatcher_compact(disp);
    return true;
}

bool mission_dispatcher_enqueue(MissionDispatcher_t *disp, const GoalItem_t *item) {
    if (disp->count >= MAX_GOALS) {
        dispatcher_compact(disp);
    }
    if (disp->count >= MAX_GOALS && !dispatcher_evict_weakest(disp, item->priority)) {
        /* Усі, хто в черзі, важливіші за новачка — відмовляємо вголос,
           щоб оператор побачив причину, а не мовчазну втрату команди. */
        if (disp->outbox != NULL) {
            const MissionEvent_t ev = bridge_event_no_space(item);
            outbox_push(disp->outbox, &ev);
        }
        return false;
    }

    disp->items[disp->count] = *item;
    disp->states[disp->count] = STATE_PENDING;
    disp->elapsed_s[disp->count] = 0.0f;
    emit(disp, disp->count, STATE_PENDING);
    disp->count++;
    return true;
}

/* Передстартова перевірка: чи взагалі можна вмикати цю ціль зараз. */
static bool check_preconditions(const GoalItem_t *item, const VehicleTelemetry_t *telem) {
    if (!telem->ekf_healthy || !telem->geofence_valid) {
        return false;
    }
    /* Повернення додому дозволене й на майже порожній батареї — воно єдине,
       що ще має сенс у такому стані. */
    if (item->action != GOAL_EMERGENCY_RETURN && telem->battery_v < BATTERY_MIN_V) {
        return false;
    }
    return true;
}

/* Найпріоритетніший кандидат серед тих, хто чекає або був призупинений.
   Ті, що не проходять передстартову перевірку, відсіюються тут-таки:
   інакше диспетчер щотакту повертався б до завідомо неможливої цілі. */
static int8_t dispatcher_select(MissionDispatcher_t *disp, const VehicleTelemetry_t *telem) {
    for (;;) {
        int8_t best = -1;

        for (uint8_t i = 0; i < disp->count; i++) {
            if (disp->states[i] != STATE_PENDING && disp->states[i] != STATE_PREEMPTED) {
                continue;
            }
            if (best < 0 || disp->items[i].priority > disp->items[best].priority) {
                best = (int8_t)i;
            }
        }

        if (best < 0) {
            return -1;
        }
        if (check_preconditions(&disp->items[best], telem)) {
            return best;
        }

        disp->states[best] = STATE_REJECTED;
        emit(disp, (uint8_t)best, STATE_REJECTED);
    }
}

static void dispatcher_activate(MissionDispatcher_t *disp, uint8_t idx) {
    disp->active_idx = (int8_t)idx;
    disp->states[idx] = STATE_ACTIVE;
    /* elapsed_s НЕ скидаємо: витіснена ціль повертається з накопиченим часом,
       інакше довге завдання можна було б безкінечно перезапускати з нуля. */
    emit(disp, idx, STATE_ACTIVE);
}

static bool dispatcher_has_live_emergency(const MissionDispatcher_t *disp) {
    for (uint8_t i = 0; i < disp->count; i++) {
        if (disp->items[i].action != GOAL_EMERGENCY_RETURN) {
            continue;
        }
        if (!goal_state_is_terminal(disp->states[i]) && disp->states[i] != STATE_EMPTY) {
            return true;
        }
    }
    return false;
}

DispatcherOutput_t mission_dispatcher_step(MissionDispatcher_t *disp,
                                           const VehicleTelemetry_t *telem,
                                           float dt_s) {
    DispatcherOutput_t out = { OUTPUT_IDLE, 0u, 0.0f, 0.0f, 0.0f };

    /* 1. Навігація втрачена. Просторова ціль без достовірної позиції — це
          політ у невідомість: активну знімаємо (зберігши прогрес), нових не
          вмикаємо, апарат тримає висоту або сідає на місці. */
    if (!telem->ekf_healthy) {
        if (disp->active_idx >= 0) {
            const uint8_t idx = (uint8_t)disp->active_idx;
            disp->states[idx] = STATE_PREEMPTED;
            emit(disp, idx, STATE_PREEMPTED);
            disp->active_idx = -1;
        }
        out.mode = (telem->battery_v < BATTERY_MIN_V) ? OUTPUT_LAND : OUTPUT_HOLD;
        return out;
    }

    /* 2. Хто має право на керування цього такту. */
    const int8_t candidate = dispatcher_select(disp, telem);
    if (candidate >= 0) {
        if (disp->active_idx < 0) {
            dispatcher_activate(disp, (uint8_t)candidate);
        } else if ((int)disp->items[candidate].priority >=
                   (int)disp->items[disp->active_idx].priority + PREEMPT_HYSTERESIS) {
            const uint8_t old_idx = (uint8_t)disp->active_idx;
            disp->states[old_idx] = STATE_PREEMPTED;
            emit(disp, old_idx, STATE_PREEMPTED);
            dispatcher_activate(disp, (uint8_t)candidate);
        }
    }

    /* 3. Ведення активної цілі: спершу час, потім відстань. */
    if (disp->active_idx >= 0) {
        const uint8_t idx = (uint8_t)disp->active_idx;
        const GoalItem_t *goal = &disp->items[idx];
        disp->elapsed_s[idx] += dt_s;

        if (goal->timeout_s > 0.0f && disp->elapsed_s[idx] > goal->timeout_s) {
            /* Ціль зависла: далі її тримати — значить блокувати чергу назавжди. */
            disp->states[idx] = STATE_ABORTED;
            emit(disp, idx, STATE_ABORTED);
            disp->active_idx = -1;
        } else {
            const float distance = goal_distance(goal->target_x, goal->target_y, goal->target_z,
                                                 telem->pos_x, telem->pos_y, telem->pos_z);
            if (distance <= goal->tolerance_m) {
                disp->states[idx] = STATE_COMPLETED;
                emit(disp, idx, STATE_COMPLETED);
                disp->active_idx = -1;
            } else {
                out.mode = OUTPUT_TRACK;
                out.goal_id = goal->id;
                out.x = goal->target_x;
                out.y = goal->target_y;
                out.z = goal->target_z;
            }
        }
    }

    /* 4. Реактивний шар. Далекомір побачив перешкоду — ставимо в чергу ціль
          аварійного відходу. Керування вона дістане наступного такту, пройшовши
          ту саму передстартову перевірку, що й планові: жодних чорних ходів. */
    if (telem->obstacle_detected && !dispatcher_has_live_emergency(disp)) {
        (void)mission_dispatcher_enqueue(disp, &kEmergencyReturn);
    }

    return out;
}

GoalState_e mission_dispatcher_state_of(const MissionDispatcher_t *disp, uint32_t goal_id) {
    for (uint8_t i = 0; i < disp->count; i++) {
        if (disp->items[i].id == goal_id) {
            return disp->states[i];
        }
    }
    return STATE_EMPTY;
}
