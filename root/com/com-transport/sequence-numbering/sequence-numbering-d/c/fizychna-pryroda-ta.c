#include <stdint.h>
#include <stdlib.h>

typedef struct {
    uint32_t last_s;      /* Час відправлення попереднього пакета (TX) */
    uint32_t last_r;      /* Час отримання попереднього пакета (RX) */
    uint32_t jitter_q4;   /* Джиттер у форматі Q28.4 (значення, помножене на 16) */
    bool     initialized;
} jitter_estimator_t;

void jitter_init(jitter_estimator_t *je) {
    je->last_s = 0;
    je->last_r = 0;
    je->jitter_q4 = 0;
    je->initialized = false;
}

/* Оновлення джиттера на кожен отриманий пакет. Часові мітки в мілісекундах або відліках кодека */
void jitter_update(jitter_estimator_t *je, uint32_t send_time, uint32_t recv_time) {
    if (!je->initialized) {
        je->last_s = send_time;
        je->last_r = recv_time;
        je->initialized = true;
        return;
    }

    int32_t d = (int32_t)((recv_time - send_time) - (je->last_r - je->last_s));
    if (d < 0) {
        d = -d; /* Абсолютне значення |D| */
    }

    je->last_s = send_time;
    je->last_r = recv_time;

    /* Рекурсивний фільтр RFC 3550: J = J + (|D| - J) / 16 */
    /* У цілочисельному форматі Q4: jitter_q4 += (d * 16 - jitter_q4) / 16 */
    je->jitter_q4 += (uint32_t)d - (je->jitter_q4 >> 4);
}

/* Отримання поточного згладженого джиттера в цілих одиницях */
uint32_t jitter_get(const jitter_estimator_t *je) {
    return je->jitter_q4 >> 4;
}
