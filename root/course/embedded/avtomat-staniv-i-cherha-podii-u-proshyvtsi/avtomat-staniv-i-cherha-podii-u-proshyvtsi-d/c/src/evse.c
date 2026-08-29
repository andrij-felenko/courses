#include "evse.h"

#include <stddef.h>

#include "cp_monitor.h"
#include "event_queue.h"
#include "hal.h"
#include "isr_sources.h"
#include "soft_timer.h"

evse_t g_evse;

/* Скільки чекати картку в стані «підключено», перш ніж повернутися в спокій. */
#define AUTH_WINDOW_MS 60000u

/* Вікно перехідних процесів після замикання контактора: іскрогасіння та вихід
 * лічильника енергії на робочу точку. Колишній delay(3000) — тепер таймер. */
#define CONTACTOR_SETTLE_MS 3000u

/* Мінімальне утримання в аварії, щоб станція не «моргала» реле по колу. */
#define FAULT_LOCKOUT_MS 5000u

#define CURRENT_LIMIT_A 32u

/* Пусковий струм контактора й самого автомобіля вчетверо перевищує робочий,
 * тому під час перехідних процесів поріг компаратора вважаємо піднятим. */
#define INRUSH_TOLERANCE_A 90u

#define LEAKAGE_TRIP_MA 30u

/* Список дозволених карток. У серійній станції його місце — у flash-сховищі
 * або в відповіді сервера OCPP; для прикладу досить сталої таблиці. */
static const uint32_t k_allowed_cards[] = {
    0x04A1B2C3u,
    0x04FE1122u,
    0x0455AA01u,
};

/* Коди аварій — потрапляють у fault_code й у журнал. */
enum {
    FAULT_NONE = 0,
    FAULT_EMERGENCY_BUTTON,
    FAULT_OVERCURRENT,
    FAULT_LEAKAGE,
    FAULT_PILOT_INVALID,
    FAULT_QUEUE_OVERFLOW
};

static void state_standby(evse_t *me, const event_t *e);
static void state_connected(evse_t *me, const event_t *e);
static void state_charging(evse_t *me, const event_t *e);
static void state_fault(evse_t *me, const event_t *e);

/* ---------------------------------------------------------------- дії ---- */

/*
 * Шпаруватість пілота за J1772: для 6…51 А дозволений струм дорівнює
 * duty × 0,6 А. Отже duty = I / 0,6 — цілочисельно це (I * 10 + 3) / 6.
 */
static uint8_t duty_for_current(uint8_t amperes)
{
    if (amperes < 6u) {
        return 0u;
    }
    if (amperes > 51u) {
        amperes = 51u;
    }
    return (uint8_t)(((uint16_t)amperes * 10u + 3u) / 6u);
}

static void set_leds(bool green, bool blue, bool red)
{
    hal_led_set(HAL_LED_GREEN, green);
    hal_led_set(HAL_LED_BLUE, blue);
    hal_led_set(HAL_LED_RED, red);
}

static bool card_is_allowed(uint32_t card_id)
{
    for (unsigned i = 0; i < sizeof(k_allowed_cards) / sizeof(k_allowed_cards[0]); ++i) {
        if (k_allowed_cards[i] == card_id) {
            return true;
        }
    }
    return false;
}

/* ------------------------------------------------------------ переходи ---- */

/*
 * Порядок кроків переходу зафіксовано тут і ніде більше: спершу дія виходу
 * старого стану, потім дія самого переходу, потім оновлення покажчика й аж
 * тоді дія входу нового стану. Через це неможливо забути розімкнути реле в
 * котромусь із п'яти обробників аварії: розмикання живе в EVT_EXIT стану
 * CHARGING і виконується завжди, хоч би що спричинило вихід.
 */
typedef void (*evse_action_fn)(evse_t *me, const event_t *e);

static void evse_transition(evse_t *me, evse_state_fn next, evse_action_fn action,
                            const event_t *cause)
{
    static const event_t exit_evt  = { EVT_EXIT, 0u, 0u };
    static const event_t entry_evt = { EVT_ENTRY, 0u, 0u };

    if (me->state != NULL) {
        me->state(me, &exit_evt);
    }
    if (action != NULL) {
        action(me, cause);
    }
    me->state = next;
    if (me->state != NULL) {
        me->state(me, &entry_evt);
    }
}

static void action_latch_fault(evse_t *me, const event_t *e)
{
    switch (e->id) {
        case EVT_EMERGENCY_STOP: me->fault_code = FAULT_EMERGENCY_BUTTON; break;
        case EVT_OVERCURRENT:    me->fault_code = FAULT_OVERCURRENT;      break;
        case EVT_LEAKAGE_TRIP:   me->fault_code = FAULT_LEAKAGE;          break;
        case EVT_CP_INVALID:     me->fault_code = FAULT_PILOT_INVALID;    break;
        default:                 me->fault_code = FAULT_QUEUE_OVERFLOW;   break;
    }
}

/* --------------------------------------------------------------- стани ---- */

static void state_standby(evse_t *me, const event_t *e)
{
    switch (e->id) {
        case EVT_ENTRY:
            /* Інваріант стану: контактор розімкнено, замок відпущено,
             * на пілоті постійні +12 В. */
            hal_relay_set(false);
            hal_lock_actuator(false);
            hal_pilot_set_duty(100u);
            set_leds(true, false, false);
            me->authorized = false;
            me->card_id    = 0u;
            break;

        case EVT_EXIT:
            break;

        case EVT_CP_STATE_B:
            /* Штекер у гнізді: замикаємо замок і оголошуємо доступний струм. */
            evse_transition(me, state_connected, NULL, e);
            break;

        default:
            break;
    }
}

static void state_connected(evse_t *me, const event_t *e)
{
    switch (e->id) {
        case EVT_ENTRY:
            hal_lock_actuator(true);
            hal_pilot_set_duty(duty_for_current(me->current_limit_a));
            set_leds(true, false, false);
            soft_timer_arm(TMR_AUTH_WINDOW, AUTH_WINDOW_MS);
            break;

        case EVT_EXIT:
            soft_timer_disarm(TMR_AUTH_WINDOW);
            break;

        case EVT_RFID_TAG:
            /* Повний номер картки лежить у поштовій скриньці зчитувача; у
             * param приїхали лише молодші 16 біт для журналу. */
            me->card_id = isr_rfid_last_card();
            if (card_is_allowed(me->card_id)) {
                me->authorized = true;
                soft_timer_disarm(TMR_AUTH_WINDOW);
                set_leds(true, true, false);
            } else {
                me->authorized = false;
                (void)event_queue_push(&g_events, EVT_AUTH_DENIED, e->param);
            }
            break;

        case EVT_AUTH_DENIED:
            set_leds(false, false, true);
            break;

        case EVT_CP_STATE_C:
            /* Автомобіль просить енергію. Без авторизації лишаємося на місці:
             * пілот уже показує дозволений струм, автомобіль почекає. */
            if (me->authorized) {
                evse_transition(me, state_charging, NULL, e);
            }
            break;

        case EVT_CP_STATE_A:
            evse_transition(me, state_standby, NULL, e);
            break;

        case EVT_TIMEOUT:
            if (e->param == (uint16_t)TMR_AUTH_WINDOW) {
                /* Картку так і не приклали: знімаємо ШІМ і відпускаємо замок. */
                evse_transition(me, state_standby, NULL, e);
            }
            break;

        default:
            break;
    }
}

static void state_charging(evse_t *me, const event_t *e)
{
    switch (e->id) {
        case EVT_ENTRY:
            hal_relay_set(true);
            set_leds(false, true, false);
            /* Замість delay(3000): станція лишається живою всі три секунди
             * перехідного процесу й реагує на кнопку за десятки мікросекунд. */
            me->settling = true;
            soft_timer_arm(TMR_CONTACTOR_SETTLE, CONTACTOR_SETTLE_MS);
            break;

        case EVT_EXIT:
            /* Єдине місце в прошивці, де розмикається силовий контактор під
             * навантаженням. Виконується на будь-якому виході зі стану. */
            hal_relay_set(false);
            me->settling = false;
            soft_timer_disarm(TMR_CONTACTOR_SETTLE);
            break;

        case EVT_TIMEOUT:
            if (e->param == (uint16_t)TMR_CONTACTOR_SETTLE) {
                me->settling = false; /* пусковий струм ущух, поріг знову робочий */
            }
            break;

        case EVT_CP_STATE_B:
            /* Акумулятор набрався: автомобіль відпустив ключ. */
            evse_transition(me, state_connected, NULL, e);
            break;

        case EVT_CP_STATE_A:
            /* Штекер висмикнули під навантаженням — реле розімкне дія виходу. */
            evse_transition(me, state_standby, NULL, e);
            break;

        default:
            break;
    }
}

static void state_fault(evse_t *me, const event_t *e)
{
    switch (e->id) {
        case EVT_ENTRY:
            /* Пілот притискаємо до нуля: автомобіль зобов'язаний трактувати це
             * як заборону заряджання й розімкнути власний контактор. */
            hal_relay_set(false);
            hal_pilot_force_low();
            hal_lock_actuator(false);
            set_leds(false, false, true);
            me->authorized = false;
            soft_timer_arm(TMR_FAULT_LOCKOUT, FAULT_LOCKOUT_MS);
            break;

        case EVT_EXIT:
            soft_timer_disarm(TMR_FAULT_LOCKOUT);
            me->fault_code = FAULT_NONE;
            break;

        case EVT_RESET_BUTTON:
            /* Скидання приймаємо лише після витримки й лише коли пілот знову
             * показує від'єднаний кабель: інакше ризикуємо подати напругу на
             * несправне з'єднання. */
            if (!soft_timer_is_armed(TMR_FAULT_LOCKOUT) &&
                cp_monitor_class() == CP_A) {
                evse_transition(me, state_standby, NULL, e);
            }
            break;

        default:
            break;
    }
}

/* ---------------------------------------------------------- диспетчер ---- */

/*
 * Аварійні події перехоплюються до того, як подія дійде до поточного стану.
 * Це плоский відповідник суперстану з ієрархічного автомата: один запис
 * замість чотирьох однакових гілок у кожному стані.
 */
static bool is_emergency(uint16_t id)
{
    return id == EVT_EMERGENCY_STOP || id == EVT_LEAKAGE_TRIP ||
           id == EVT_CP_INVALID || id == EVT_OVERCURRENT;
}

void evse_dispatch(evse_t *me, const event_t *e)
{
    if (is_emergency(e->id)) {
        /* Кидок струму в перші мілісекунди після замикання контактора —
         * не аварія, а нормальний пусковий струм. Але лише до розумної межі. */
        const bool inrush_ok = me->settling && e->id == EVT_OVERCURRENT &&
                               e->param < INRUSH_TOLERANCE_A;

        /* Витік нижче порога диференційного захисту теж не тривожимо. */
        const bool leak_ok = e->id == EVT_LEAKAGE_TRIP && e->param < LEAKAGE_TRIP_MA;

        if (!inrush_ok && !leak_ok && me->state != state_fault) {
            evse_transition(me, state_fault, action_latch_fault, e);
            return;
        }
        if (!inrush_ok && !leak_ok) {
            return; /* уже в аварії: код першої причини не затираємо */
        }
    }

    if (me->state != NULL) {
        me->state(me, e);
    }
}

void evse_init(evse_t *me)
{
    me->state           = NULL;
    me->authorized      = false;
    me->settling        = false;
    me->card_id         = 0u;
    me->current_limit_a = CURRENT_LIMIT_A;
    me->fault_code      = FAULT_NONE;

    /* Перехід із порожнього стану: дію виходу пропущено, дію входу виконано —
     * саме вона приводить апаратуру у визначений вигляд після скидання. */
    evse_transition(me, state_standby, NULL, NULL);
}

const char *evse_state_name(const evse_t *me)
{
    if (me->state == state_standby)   return "STANDBY";
    if (me->state == state_connected) return "CONNECTED";
    if (me->state == state_charging)  return "CHARGING";
    if (me->state == state_fault)     return "FAULT";
    return "?";
}

const char *evse_fault_name(uint16_t fault_code)
{
    switch (fault_code) {
        case FAULT_EMERGENCY_BUTTON: return "кнопка аварійної зупинки";
        case FAULT_OVERCURRENT:      return "перевищення струму";
        case FAULT_LEAKAGE:          return "струм витоку";
        case FAULT_PILOT_INVALID:    return "несправність лінії пілота";
        case FAULT_QUEUE_OVERFLOW:   return "переповнення черги подій";
        default:                     return "без аварії";
    }
}
