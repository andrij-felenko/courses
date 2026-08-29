#ifndef SAFETY_BLACKBOX_H
#define SAFETY_BLACKBOX_H

#include <stdint.h>
#include <stdbool.h>

/* Чорна скринька супервізора: кільцевий буфер подій у статичній памʼяті.
 * Запис — O(1), без malloc: модуль крутиться в задачі жорсткого реального часу,
 * де ні алокатор, ні файлова система недоступні. Коли буфер переповнюється,
 * найстаріша подія затирається, а лічильник dropped показує, скільки саме. */

#define BLACKBOX_CAPACITY 48u

/* Причина, через яку фільтр утрутився в команду планувальника. */
typedef enum {
    BB_REASON_NONE = 0,     /* команда пройшла без змін */
    BB_REASON_ESTOP,        /* апаратна кнопка аварійної зупинки */
    BB_REASON_WATCHDOG,     /* уставка планувальника застаріла */
    BB_REASON_BAD_PLAN,     /* у пакеті уставки нечислове значення */
    BB_REASON_OBSTACLE,     /* гальмівний бар'єр за дистанцією */
    BB_REASON_BATTERY,      /* просідання шини живлення */
    BB_REASON_TILT,         /* наближення до критичного крену */
    BB_REASON_SPEED_LIMIT,  /* абсолютна стеля швидкості приводів */
    BB_REASON_YAW_LIMIT,    /* абсолютна стеля кутової швидкості */
    BB_REASON_ACCEL_LIMIT,  /* обмеження темпу розгону */
    BB_REASON_SENSOR_LOST   /* давач не дає достовірного виміру */
} BbReason;

/* Однакові підряд події зливаються в один запис із лічильником repeats:
 * інакше 200 тактів на секунду затерли б буфер за чверть секунди. */
typedef struct {
    uint32_t tick_begin; /* такт, на якому епізод почався */
    float    t_begin;    /* час початку епізоду, с від старту */
    float    t_end;      /* час останнього такту епізоду, с */
    uint8_t  status;     /* SafetyStatus; тут uint8_t, щоб не тягнути supervisor.h */
    uint8_t  reason;     /* BbReason */
    float    value;      /* значення порушеного інваріанта на останньому такті */
    uint32_t repeats;    /* скільки тактів епізод тривав */
} BbEntry;

typedef struct {
    BbEntry  items[BLACKBOX_CAPACITY];
    uint32_t head;    /* куди ляже наступний запис */
    uint32_t count;   /* скільки записів дійсні, ≤ BLACKBOX_CAPACITY */
    uint32_t dropped; /* скільки затерто через переповнення */
} BlackBox;

void blackbox_init(BlackBox *bb);

/* Записати такт. Якщо (status, reason) збігається з попереднім записом —
 * подовжує його, а не заводить новий. */
void blackbox_record(BlackBox *bb, uint32_t tick, float time_s,
                     uint8_t status, uint8_t reason, float value);

uint32_t blackbox_size(const BlackBox *bb);

/* Доступ у хронологічному порядку: індекс 0 — найстаріший наявний запис. */
const BbEntry *blackbox_at(const BlackBox *bb, uint32_t index);

const char *bb_reason_name(uint8_t reason);
const char *bb_status_name(uint8_t status);

#endif /* SAFETY_BLACKBOX_H */
