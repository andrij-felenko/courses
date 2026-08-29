#include "qequeue.h"

void QEQueue_init(QEQueue *me, QEvt *storage, uint16_t capacity) {
    Q_ASSERT(me != NULL);
    Q_ASSERT(storage != NULL);
    Q_ASSERT(capacity >= 2U);

    me->buf = storage;
    me->capacity = capacity;
    me->head = 0U;
    me->tail = 0U;
    me->used = 0U;
    me->maxUsed = 0U;
    me->dropped = 0U;
}

bool QEQueue_post(QEQueue *me, QSignal sig, uintptr_t param) {
    bool ok;

    Q_ASSERT(me != NULL);
    Q_ASSERT(sig >= Q_USER_SIG); /* службові сигнали в чергу не потрапляють */

    Q_CRIT_ENTRY();
    if (me->used < me->capacity) {
        me->buf[me->tail].sig = sig;
        me->buf[me->tail].param = param;
        me->tail = (uint16_t)((me->tail + 1U) % me->capacity);
        ++me->used;
        if (me->used > me->maxUsed) {
            me->maxUsed = me->used;
        }
        ok = true;
    } else {
        /* Черга переповнена. Мовчки затирати найстарішу подію не можна:
         * саме там може лежати сигнал аварії. Фіксуємо втрату і кажемо
         * джерелу правду. */
        ++me->dropped;
        ok = false;
    }
    Q_CRIT_EXIT();

    return ok;
}

bool QEQueue_get(QEQueue *me, QEvt *out) {
    bool ok;

    Q_ASSERT(me != NULL);
    Q_ASSERT(out != NULL);

    Q_CRIT_ENTRY();
    if (me->used > 0U) {
        *out = me->buf[me->head];
        me->head = (uint16_t)((me->head + 1U) % me->capacity);
        --me->used;
        ok = true;
    } else {
        ok = false;
    }
    Q_CRIT_EXIT();

    return ok;
}

uint16_t QEQueue_used(const QEQueue *me) {
    Q_ASSERT(me != NULL);
    return me->used;
}

uint16_t QEQueue_maxUsed(const QEQueue *me) {
    Q_ASSERT(me != NULL);
    return me->maxUsed;
}

uint16_t QEQueue_dropped(const QEQueue *me) {
    Q_ASSERT(me != NULL);
    return me->dropped;
}
