#include "dispatcher.h"

#include <stddef.h>

static bool state_is_terminal(goal_state_t s)
{
    return s == GOAL_COMPLETED || s == GOAL_ABORTED || s == GOAL_REJECTED;
}

static bool state_is_waiting(goal_state_t s)
{
    /* Витіснена ціль повертається в конкуренцію нарівні з тими, що чекають. */
    return s == GOAL_PENDING || s == GOAL_PREEMPTED;
}

void dispatcher_init(goal_dispatcher_t *d, const flight_envelope_t *env)
{
    if (d == NULL || env == NULL) {
        return;
    }
    for (uint8_t i = 0; i < GOAL_QUEUE_CAPACITY; i++) {
        goal_slot_t empty = { 0 };
        empty.state = GOAL_SLOT_FREE;
        d->slots[i] = empty;
    }
    d->env = *env;
    d->active = -1;
    d->active_hold_sec = 0.0f;
    d->next_id = 1; /* нуль лишаємо як «недійсний id» */
    d->emergency_armed = false;
}

/* Вільний слот; якщо вільних немає — перезаписуємо завершену ціль; якщо й таких
   немає, аварійна ціль витісняє найменш пріоритетну з тих, що ще чекають. */
static int8_t slot_alloc(goal_dispatcher_t *d, uint8_t priority)
{
    for (uint8_t i = 0; i < GOAL_QUEUE_CAPACITY; i++) {
        if (d->slots[i].state == GOAL_SLOT_FREE) {
            return (int8_t)i;
        }
    }
    for (uint8_t i = 0; i < GOAL_QUEUE_CAPACITY; i++) {
        if (state_is_terminal(d->slots[i].state)) {
            return (int8_t)i;
        }
    }
    if (priority != GOAL_PRIO_EMERGENCY) {
        return -1;
    }
    int8_t victim = -1;
    for (uint8_t i = 0; i < GOAL_QUEUE_CAPACITY; i++) {
        if (!state_is_waiting(d->slots[i].state)) {
            continue;
        }
        if (victim < 0 || d->slots[i].goal.priority < d->slots[victim].goal.priority) {
            victim = (int8_t)i;
        }
    }
    return victim;
}

uint32_t dispatcher_submit(goal_dispatcher_t *d, const goal_t *g)
{
    if (d == NULL || g == NULL) {
        return 0;
    }
    int8_t idx = slot_alloc(d, g->priority);
    if (idx < 0) {
        return 0; /* черга переповнена активною роботою */
    }

    goal_slot_t fresh = { 0 };
    fresh.goal = *g;
    fresh.goal.id = d->next_id++;
    fresh.state = GOAL_PENDING;
    d->slots[idx] = fresh;
    return fresh.goal.id;
}

const goal_slot_t *dispatcher_find(const goal_dispatcher_t *d, uint32_t goal_id)
{
    if (d == NULL || goal_id == 0) {
        return NULL;
    }
    for (uint8_t i = 0; i < GOAL_QUEUE_CAPACITY; i++) {
        if (d->slots[i].state != GOAL_SLOT_FREE && d->slots[i].goal.id == goal_id) {
            return &d->slots[i];
        }
    }
    return NULL;
}

static void finish_active(goal_dispatcher_t *d, goal_state_t st, goal_check_t verdict)
{
    goal_slot_t *s = &d->slots[d->active];
    s->state = st;
    s->verdict = verdict;
    s->replan_pending = false;
    d->active = -1;
    d->active_hold_sec = 0.0f;
}

bool dispatcher_cancel(goal_dispatcher_t *d, uint32_t goal_id)
{
    if (d == NULL) {
        return false;
    }
    for (uint8_t i = 0; i < GOAL_QUEUE_CAPACITY; i++) {
        goal_slot_t *s = &d->slots[i];
        if (s->state == GOAL_SLOT_FREE || s->goal.id != goal_id) {
            continue;
        }
        if (s->state == GOAL_ACTIVE) {
            finish_active(d, GOAL_ABORTED, GOAL_CHECK_OK);
        } else if (state_is_waiting(s->state)) {
            s->state = GOAL_REJECTED;
        } else {
            return false; /* ціль уже завершена, скасовувати нічого */
        }
        return true;
    }
    return false;
}

/* Критична відмова на ходу знімає поточну ціль: летіти далі по зіпсованих
   давачах гірше, ніж зупинитися. Аварійну ціль не знімає ніщо. */
static void handle_failures(goal_dispatcher_t *d, const system_state_t *sys)
{
    if (d->active < 0) {
        return;
    }
    if (d->slots[d->active].goal.priority == GOAL_PRIO_EMERGENCY) {
        return;
    }
    if (!sys->sensors_ok) {
        finish_active(d, GOAL_ABORTED, GOAL_CHECK_SENSOR_FAILURE);
    } else if (!sys->motors_ok) {
        finish_active(d, GOAL_ABORTED, GOAL_CHECK_MOTOR_FAILURE);
    }
}

/* Сама система породжує ціль пріоритету 255, коли просіла напруга або
   розсипалася навігація. Це і є «критерій повернення» з опису цілі. */
static void arm_emergency(goal_dispatcher_t *d, const system_state_t *sys)
{
    if (d->emergency_armed) {
        return;
    }

    goal_t g = { 0 };
    bool nav_broken = (sys->ekf_pos_variance > d->env.ekf_variance_limit * GOAL_EKF_PANIC_FACTOR);

    if (!sys->sensors_ok || !sys->motors_ok || nav_broken) {
        /* Летіти додому по зламаній оцінці позиції нікуди: тримаємо точку
           й віддаємо рішення операторові. */
        g.type = GOAL_HOLD_POSITION;
        g.target = sys->pos;
        g.timeout_sec = 30.0f;
    } else if (sys->battery_voltage < d->env.rth_voltage) {
        g.type = GOAL_EMERGENCY_RTH;
        g.target = d->env.home;
        g.timeout_sec = 0.0f;
    } else {
        return;
    }

    g.priority = GOAL_PRIO_EMERGENCY;
    g.acceptance_radius = 2.0f;
    g.cruise_airspeed = d->env.rth_airspeed;
    d->emergency_armed = (dispatcher_submit(d, &g) != 0);
}

/* Найпріоритетніша ціль серед тих, що чекають. Рівні пріоритети розводить
   порядок у черзі — інакше два однакові завдання мінялися б місцями щотакту. */
static int8_t pick_candidate(const goal_dispatcher_t *d)
{
    int8_t best = -1;
    for (uint8_t i = 0; i < GOAL_QUEUE_CAPACITY; i++) {
        if (!state_is_waiting(d->slots[i].state)) {
            continue;
        }
        if (best < 0 || d->slots[i].goal.priority > d->slots[best].goal.priority) {
            best = (int8_t)i;
        }
    }
    return best;
}

static bool may_preempt(const goal_dispatcher_t *d, int8_t cand)
{
    if (d->active < 0) {
        return true;
    }
    const goal_slot_t *a = &d->slots[d->active];
    const goal_slot_t *c = &d->slots[cand];

    if (c->goal.priority == GOAL_PRIO_EMERGENCY) {
        return true;
    }
    if (d->active_hold_sec < GOAL_HOLD_DOWN_SEC) {
        return false; /* таймер утримання: щойно активована ціль недоторканна */
    }
    /* Гістерезис: рівний або майже рівний пріоритет активну ціль не зрушить. */
    return (uint16_t)c->goal.priority >= (uint16_t)a->goal.priority + GOAL_PREEMPT_HYSTERESIS;
}

static void consider_candidate(goal_dispatcher_t *d, const system_state_t *sys)
{
    int8_t cand = pick_candidate(d);
    if (cand < 0 || cand == d->active || !may_preempt(d, cand)) {
        return;
    }

    goal_slot_t *c = &d->slots[cand];
    c->state = GOAL_VALIDATING;

    /* Валідація ДО витіснення. Якщо зробити навпаки (спершу зняти активну,
       потім перевіряти нову), то невдалий допуск лишить апарат узагалі без
       цілі — з активною місією, переведеною в PREEMPTED, і без заміни. */
    goal_check_t verdict = preflight_check(&c->goal, sys, &d->env);
    c->verdict = verdict;

    if (verdict != GOAL_CHECK_OK) {
        c->state = goal_check_is_critical(verdict) ? GOAL_ABORTED : GOAL_REJECTED;
        return; /* активну ціль не чіпаємо */
    }

    if (d->active >= 0) {
        goal_slot_t *old = &d->slots[d->active];
        old->state = GOAL_PREEMPTED;
        old->resume_from = sys->pos; /* прогрес і точка переривання лишаються в слоті */
        old->replan_pending = false;
    }

    d->active = cand;
    c->state = GOAL_ACTIVE;
    c->replan_pending = true; /* нова активна ціль — новий глобальний маршрут */
    d->active_hold_sec = 0.0f;
}

static void advance_active(goal_dispatcher_t *d, const system_state_t *sys, float dt_sec,
                           dispatch_out_t *out)
{
    if (d->active < 0) {
        return;
    }
    goal_slot_t *s = &d->slots[d->active];
    s->elapsed_sec += dt_sec;
    d->active_hold_sec += dt_sec;

    if (s->goal.timeout_sec > 0.0f && s->elapsed_sec > s->goal.timeout_sec) {
        finish_active(d, GOAL_ABORTED, GOAL_CHECK_TIMEOUT);
        return;
    }

    /* Утримання точки не «досягається» — його знімає таймаут або витіснення. */
    if (s->goal.type != GOAL_HOLD_POSITION) {
        float dist = vec3_norm(vec3_sub(s->goal.target, sys->pos));
        if (dist <= s->goal.acceptance_radius) {
            finish_active(d, GOAL_COMPLETED, GOAL_CHECK_OK);
            return;
        }
    }

    if (out != NULL) {
        out->has_goal = true;
        out->goal_id = s->goal.id;
        out->type = s->goal.type;
        out->setpoint = s->goal.target;
        out->replan_requested = s->replan_pending;
    }
    s->replan_pending = false;
}

void dispatcher_tick(goal_dispatcher_t *d,
                     const system_state_t *sys,
                     float dt_sec,
                     dispatch_out_t *out)
{
    if (out != NULL) {
        dispatch_out_t empty = { 0 };
        *out = empty;
    }
    if (d == NULL || sys == NULL || dt_sec < 0.0f) {
        return;
    }

    handle_failures(d, sys);
    arm_emergency(d, sys);
    consider_candidate(d, sys);
    advance_active(d, sys, dt_sec, out);
}

void dispatcher_report_path_blocked(goal_dispatcher_t *d)
{
    if (d == NULL || d->active < 0) {
        return;
    }
    goal_slot_t *s = &d->slots[d->active];
    s->replans++;
    if (s->replans > GOAL_MAX_REPLANS) {
        /* Тричі шукали обхід і не знайшли: ціль недосяжна, знімаємо її й
           віддаємо чергу наступній. Штурмувати стіну апарат не буде. */
        finish_active(d, GOAL_ABORTED, GOAL_CHECK_PATH_BLOCKED);
        return;
    }
    s->replan_pending = true; /* глобальний планувальник перерахує в обхід */
}
