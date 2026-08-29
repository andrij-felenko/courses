/*
 * qequeue.h — кільцева черга подій між перериваннями і головним циклом.
 *
 * Сховище дає застосунок (статичний масив), черга лише керує індексами.
 * Кладуть у чергу переривання, забирає головний цикл; критична секція
 * коротка й фіксована — кілька інструкцій навколо індексів.
 */
#ifndef QEQUEUE_H
#define QEQUEUE_H

#include "qhsm.h"

/* Порт під конкретний МК перевизначає ці макроси до __disable_irq() /
 * __enable_irq() (Cortex-M) або cli() / sei() (AVR). На хості переривань
 * немає, тож типова реалізація порожня. */
#ifndef Q_CRIT_ENTRY
#define Q_CRIT_ENTRY() ((void)0)
#define Q_CRIT_EXIT()  ((void)0)
#endif

typedef struct {
    QEvt *buf;
    uint16_t capacity;
    volatile uint16_t head;    /* звідки читає головний цикл */
    volatile uint16_t tail;    /* куди пише переривання */
    volatile uint16_t used;    /* скільки подій зараз у черзі */
    volatile uint16_t maxUsed; /* історичний максимум — міряє запас глибини */
    volatile uint16_t dropped; /* скільки подій втрачено через переповнення */
} QEQueue;

void QEQueue_init(QEQueue *me, QEvt *storage, uint16_t capacity);

/* Кладе подію в чергу. Викликається з переривання. Повертає false, якщо
 * черга повна: подію втрачено, і лічильник dropped це зафіксував. */
bool QEQueue_post(QEQueue *me, QSignal sig, uintptr_t param);

/* Забирає найстарішу подію. Викликається з головного циклу.
 * Повертає false, якщо черга порожня. */
bool QEQueue_get(QEQueue *me, QEvt *out);

uint16_t QEQueue_used(const QEQueue *me);
uint16_t QEQueue_maxUsed(const QEQueue *me);
uint16_t QEQueue_dropped(const QEQueue *me);

#endif /* QEQUEUE_H */
