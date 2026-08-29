#include "safety.h"
#include "safety_hal.h"

#define EDM_CLOSE_MS   250U   /* дзеркальні NC мусять зійтися після знеструмлення */
#define EDM_OPEN_MS    250U   /* і розійтися після втягування контакторів */

void safety_init(safety_t *s)
{
    s->state         = SAFETY_IDLE;
    s->contactors_on = false;
    s->edm_watch     = false;
    s->edm_timer_ms  = 0;
    s->reset_prev    = false;
    s->last_ms       = hal_now_ms();

    estop_channels_init(&s->channels);
    deadman_init(&s->deadman);

    hal_set_contactors(false);
    hal_set_lamp(false);
    hal_set_buzzer(false);
}

bool safety_is_fault(safety_state_t st)
{
    return st >= SAFETY_FAULT_SHORT_TO_SUPPLY;
}

const char *safety_state_name(safety_state_t st)
{
    switch (st) {
    case SAFETY_IDLE:                  return "очікування пуску";
    case SAFETY_RUNNING:               return "РОБОТА";
    case SAFETY_STOPPED_ESTOP:         return "стоп: контур E-Stop розірвано";
    case SAFETY_STOPPED_ENABLE:        return "стоп: немає дозволу мертвої руки";
    case SAFETY_FAULT_SHORT_TO_SUPPLY: return "ПОМИЛКА: замикання лінії на +24 В";
    case SAFETY_FAULT_CROSS_CIRCUIT:   return "ПОМИЛКА: міжканальне замикання";
    case SAFETY_FAULT_DISCORDANCE:     return "ПОМИЛКА: розбіжність каналів E-Stop";
    case SAFETY_FAULT_ENABLE_CONTACTS: return "ПОМИЛКА: розбіжність контактів дозволу";
    case SAFETY_FAULT_EDM:             return "ПОМИЛКА: контактор не відпустив (EDM)";
    default:                           return "?";
    }
}

safety_state_t safety_state(const safety_t *s)   { return s->state; }
bool           safety_outputs_on(const safety_t *s) { return s->contactors_on; }

/* Зупинка Категорії 0: струм із котушок знімається негайно, зворотні
   пружини розводять силові контакти. Одразу починаємо стежити за петлею. */
static void deenergize(safety_t *s)
{
    if (!s->contactors_on) {
        return;
    }
    hal_set_contactors(false);
    s->contactors_on = false;
    s->edm_watch     = true;
    s->edm_timer_ms  = 0;
}

/* Нагляд за дзеркальними контактами. Петля мусить перекинутися слідом за
   котушками за час механіки; не перекинулася — силовий контакт зварився
   або обірвано діагностичний шлейф. */
static void supervise_edm(safety_t *s, uint32_t dt_ms)
{
    if (!s->edm_watch) {
        return;
    }

    const bool loop_closed = hal_read_edm_loop();
    const bool expected    = !s->contactors_on;

    if (loop_closed == expected) {
        s->edm_watch    = false;
        s->edm_timer_ms = 0;
        return;
    }

    s->edm_timer_ms += dt_ms;
    const uint32_t limit = s->contactors_on ? EDM_OPEN_MS : EDM_CLOSE_MS;
    if (s->edm_timer_ms >= limit) {
        s->edm_watch = false;
        s->state     = SAFETY_FAULT_EDM;
        hal_set_contactors(false);
        s->contactors_on = false;
    }
}

/* Перенесення дефекту ліній і контактів дозволу в стан наглядача. */
static void latch_faults(safety_t *s)
{
    if (safety_is_fault(s->state)) {
        return;
    }

    switch (estop_channels_fault(&s->channels)) {
    case CH_FAULT_SHORT_TO_SUPPLY: s->state = SAFETY_FAULT_SHORT_TO_SUPPLY; return;
    case CH_FAULT_CROSS_CIRCUIT:   s->state = SAFETY_FAULT_CROSS_CIRCUIT;   return;
    case CH_FAULT_DISCORDANCE:     s->state = SAFETY_FAULT_DISCORDANCE;     return;
    case CH_FAULT_NONE:            break;
    }

    if (deadman_grip(&s->deadman) == GRIP_FAULT) {
        s->state = SAFETY_FAULT_ENABLE_CONTACTS;
    }
}

void safety_process(safety_t *s)
{
    const uint32_t now = hal_now_ms();
    const uint32_t dt  = now - s->last_ms;   /* різниця беззнакових переживає переповнення */
    s->last_ms = now;

    const bool channels_ok = estop_channels_update(&s->channels, dt);
    deadman_update(&s->deadman, dt);

    hal_set_lamp(s->deadman.lamp);
    hal_set_buzzer(s->deadman.buzzer);

    latch_faults(s);

    const bool demand = channels_ok
                     && deadman_ready(&s->deadman)
                     && !safety_is_fault(s->state);

    if (!demand) {
        deenergize(s);
        if (!safety_is_fault(s->state)) {
            s->state = channels_ok ? SAFETY_STOPPED_ENABLE : SAFETY_STOPPED_ESTOP;
        }
    }

    supervise_edm(s, dt);

    /* Пуск тільки по ФРОНТУ кнопки: залипла або перемкнута стяжкою кнопка
       пуску не має піднімати машину сама. */
    const bool reset_now  = hal_read_reset_button();
    const bool reset_edge = reset_now && !s->reset_prev;
    s->reset_prev = reset_now;

    if (!s->contactors_on && demand && reset_edge) {
        if (!hal_read_edm_loop()) {
            /* Петля розімкнена при знеструмлених котушках — приварений
               силовий контакт. Пуск заборонено до обслуговування. */
            s->state = SAFETY_FAULT_EDM;
            return;
        }
        hal_set_contactors(true);
        s->contactors_on = true;
        s->edm_watch     = true;
        s->edm_timer_ms  = 0;
        s->state         = SAFETY_RUNNING;
    }
}
