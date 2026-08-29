#include "fsm_handler.h"

#include <stddef.h>

#define HOLD_TICKS 30u

static void state_filling(pump_t *me, pump_signal_t sig);
static void state_holding(pump_t *me, pump_signal_t sig);
static void state_draining(pump_t *me, pump_signal_t sig);
static void state_dry_fault(pump_t *me, pump_signal_t sig);

/*
 * Увесь рушій патерну. Порядок кроків той самий, що й у великому автоматі:
 * дія виходу старого стану, зміна покажчика, дія входу нового. Стан ніколи не
 * присвоюється повз цю функцію — інакше пара entry/exit розсинхронізується.
 */
static void pump_transition(pump_t *me, pump_state_fn next)
{
    if (me->state != NULL) {
        me->state(me, PUMP_EV_EXIT);
    }
    me->state = next;
    if (me->state != NULL) {
        me->state(me, PUMP_EV_ENTRY);
    }
}

static void state_filling(pump_t *me, pump_signal_t sig)
{
    switch (sig) {
        case PUMP_EV_ENTRY:
            pump_port_valve(true);
            break;

        case PUMP_EV_EXIT:
            /* Клапан закривається на будь-якому виході: і за штатним рівнем,
             * і за сухим ходом. Одне місце замість трьох гілок. */
            pump_port_valve(false);
            break;

        case PUMP_EV_LEVEL_HIGH:
            pump_transition(me, state_holding);
            break;

        case PUMP_EV_DRY_RUN:
            pump_transition(me, state_dry_fault);
            break;

        default:
            break;
    }
}

static void state_holding(pump_t *me, pump_signal_t sig)
{
    switch (sig) {
        case PUMP_EV_ENTRY:
            me->hold_ticks = HOLD_TICKS;
            break;

        case PUMP_EV_EXIT:
            me->hold_ticks = 0u;
            break;

        case PUMP_EV_TIMER:
            if (me->hold_ticks > 0u && --me->hold_ticks == 0u) {
                pump_transition(me, state_draining);
            }
            break;

        case PUMP_EV_DRY_RUN:
            pump_transition(me, state_dry_fault);
            break;

        default:
            break;
    }
}

static void state_draining(pump_t *me, pump_signal_t sig)
{
    switch (sig) {
        case PUMP_EV_ENTRY:
            pump_port_motor(true);
            break;

        case PUMP_EV_EXIT:
            /* Насос зупиняється завжди — це головна гарантія стану. */
            pump_port_motor(false);
            break;

        case PUMP_EV_LEVEL_LOW:
            if (me->cycles != UINT32_MAX) {
                ++me->cycles;
            }
            pump_transition(me, state_filling);
            break;

        case PUMP_EV_DRY_RUN:
            pump_transition(me, state_dry_fault);
            break;

        default:
            break;
    }
}

static void state_dry_fault(pump_t *me, pump_signal_t sig)
{
    switch (sig) {
        case PUMP_EV_ENTRY:
            me->dry_latched = true;
            pump_port_alarm(true);
            break;

        case PUMP_EV_EXIT:
            me->dry_latched = false;
            pump_port_alarm(false);
            break;

        case PUMP_EV_RESET:
            pump_transition(me, state_filling);
            break;

        default:
            break;
    }
}

void pump_init(pump_t *me)
{
    me->state       = NULL;
    me->cycles      = 0u;
    me->hold_ticks  = 0u;
    me->dry_latched = false;

    /* Дії виходу немає — попереднього стану не існує; дія входу є, і саме вона
     * приводить клапан і насос у визначене положення. */
    pump_transition(me, state_filling);
}

void pump_dispatch(pump_t *me, pump_signal_t sig)
{
    /* Службові сигнали ззовні не приймаються: інакше хтось міг би виконати
     * дію входу, не зробивши переходу. */
    if (sig == PUMP_EV_ENTRY || sig == PUMP_EV_EXIT) {
        return;
    }
    if (me->state != NULL) {
        me->state(me, sig);
    }
}

const char *pump_state_name(const pump_t *me)
{
    if (me->state == state_filling)   return "FILLING";
    if (me->state == state_holding)   return "HOLDING";
    if (me->state == state_draining)  return "DRAINING";
    if (me->state == state_dry_fault) return "DRY_FAULT";
    return "?";
}

/* --------------------------------------------------- слабкий порт ------- */

#if defined(__GNUC__) || defined(__clang__)
#define PUMP_WEAK __attribute__((weak))
#else
#define PUMP_WEAK
#endif

PUMP_WEAK void pump_port_valve(bool open) { (void)open; }
PUMP_WEAK void pump_port_motor(bool run)  { (void)run; }
PUMP_WEAK void pump_port_alarm(bool on)   { (void)on; }
