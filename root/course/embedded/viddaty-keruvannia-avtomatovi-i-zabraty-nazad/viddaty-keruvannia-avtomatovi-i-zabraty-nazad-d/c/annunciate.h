#ifndef ANNUNCIATE_H
#define ANNUNCIATE_H

#include <stdint.h>

#include "takeover.h"

/* Сповіщення про перехоплення: STATUSTEXT на подію, HEARTBEAT раз на секунду
   й потокове значення α. Пульт (EdgeTX) сам розіграє вібро й озвучку за
   отриманим STATUSTEXT — на борту ми формуємо тільки повідомлення. */

#define MAV_SEVERITY_CRITICAL 2u
#define MAV_SEVERITY_WARNING  4u
#define MAV_SEVERITY_INFO     6u

/* STATUSTEXT.text — рівно 50 байтів; якщо текст займає всі 50, завершального
   нуля в полі немає. Саме тому копіюємо вручну, а не strcpy. */
typedef struct {
    uint8_t severity;
    char    text[50];
} mav_statustext_t;

typedef struct {
    uint8_t  base_mode;   /* бітове поле MAV_MODE_FLAG_* */
    uint32_t custom_mode; /* тут — стан нашого автомата перехоплення */
} mav_heartbeat_t;

/* NAMED_VALUE_FLOAT: name[10] без обов'язкового нуля, value, time_boot_ms. */
typedef struct {
    char     name[10];
    float    value;
    uint32_t time_boot_ms;
} mav_named_value_float_t;

typedef struct {
    uint32_t last_heartbeat_ms;
    uint32_t last_named_ms;
    bool     started;
} annunciator_t;

void annunciate_init(annunciator_t *an);
void annunciate_events(annunciator_t *an, takeover_t *t, uint32_t now_ms);
void annunciate_stream(annunciator_t *an, const takeover_status_t *st, uint32_t now_ms);

#endif /* ANNUNCIATE_H */
