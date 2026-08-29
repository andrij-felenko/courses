#ifndef EVSE_EVENTS_H
#define EVSE_EVENTS_H

#include <stdint.h>

/*
 * Словник подій системи. Ідентифікатори до EVT_USER_FIRST службові: їх ніхто
 * не кладе в чергу, вони існують лише для викликів on_enter/on_exit усередині
 * автомата.
 */
typedef enum {
    EVT_ENTRY = 0, /* службовий: вхід у стан */
    EVT_EXIT,      /* службовий: вихід зі стану */

    EVT_USER_FIRST,

    /* Лінія Control Pilot: клас напруги змінився. */
    EVT_CP_STATE_A = EVT_USER_FIRST, /* +12 В, кабель від'єднано */
    EVT_CP_STATE_B,                  /* +9 В, автомобіль підключено */
    EVT_CP_STATE_C,                  /* +6 В, автомобіль просить енергію */
    EVT_CP_INVALID,                  /* обрив, пробій, зникнення діода */

    /* Зчитувач RFID: param — молодші 16 біт номера картки. */
    EVT_RFID_TAG,
    EVT_AUTH_DENIED, /* картки немає у списку дозволених */

    /* Аварійні джерела. */
    EVT_EMERGENCY_STOP, /* кнопка «Грибок» */
    EVT_OVERCURRENT,    /* компаратор струму, param — виміряні ампери */
    EVT_LEAKAGE_TRIP,   /* диференційний захист, param — мА витоку */

    EVT_RESET_BUTTON,

    EVT_TIMEOUT,   /* param — soft_timer_id_t */
    EVT_TICK_10MS, /* періодичний такт для повільних опитувань */

    EVT_ID_COUNT
} evse_event_id_t;

/*
 * Запис події — рівно 8 байтів: він копіюється в кільцеву чергу з обробника
 * переривання, тож мусить лишатися дешевим і не тягти за собою покажчиків на
 * дані, чий час життя переживе диспетчеризацію.
 */
typedef struct {
    uint16_t id;    /* evse_event_id_t */
    uint16_t param; /* уточнення, залежить від id */
    uint32_t t_ms;  /* мітка часу постановки в чергу */
} event_t;

#endif /* EVSE_EVENTS_H */
