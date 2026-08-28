#include <stdint.h>
#include <stdbool.h>

typedef enum {
    PKT_IN_ORDER,    /* Пакет прибув строго за чергою */
    PKT_GAP_LOSS,    /* Випередження черги: виявлено втрату або затримку пакетів */
    PKT_REORDERED,   /* Запізнілий пакет: заповнення дірки в черзі */
    PKT_DUPLICATE,   /* Точний дублікат уже отриманого пакета */
    PKT_STALE_DROP   /* Застарілий пакет поза межами вікна прийому */
} packet_status_t;

typedef struct {
    uint16_t seq_expected;  /* Очікуваний наступний номер */
    uint16_t seq_max;       /* Найбільший зафіксований номер */
    uint64_t recv_mask;     /* 64-бітна маска отриманих пакетів */
    bool     initialized;   /* Прапорець первинного старту */
} seq_tracker_t;

void seq_tracker_init(seq_tracker_t *tr) {
    tr->seq_expected = 0;
    tr->seq_max = 0;
    tr->recv_mask = 0;
    tr->initialized = false;
}

packet_status_t seq_tracker_process(seq_tracker_t *tr, uint16_t seq, uint16_t *out_lost_count) {
    *out_lost_count = 0;

    if (!tr->initialized) {
        tr->seq_expected = (uint16_t)(seq + 1);
        tr->seq_max = seq;
        tr->recv_mask = 1ULL;
        tr->initialized = true;
        return PKT_IN_ORDER;
    }

    int16_t diff_exp = (int16_t)(seq - tr->seq_expected);

    /* Випадок 1: Очікуваний пакет за чергою */
    if (diff_exp == 0) {
        tr->seq_expected++;
        if ((int16_t)(seq - tr->seq_max) > 0) {
            uint16_t shift = (uint16_t)(seq - tr->seq_max);
            tr->recv_mask = (shift < 64) ? ((tr->recv_mask << shift) | 1ULL) : 1ULL;
            tr->seq_max = seq;
        }
        return PKT_IN_ORDER;
    }

    /* Випадок 2: Випередження (пропуск у потоці) */
    if (diff_exp > 0) {
        *out_lost_count = (uint16_t)diff_exp;
        int16_t diff_max = (int16_t)(seq - tr->seq_max);
        if (diff_max > 0) {
            uint16_t shift = (uint16_t)diff_max;
            tr->recv_mask = (shift < 64) ? ((tr->recv_mask << shift) | 1ULL) : 1ULL;
            tr->seq_max = seq;
        }
        return PKT_GAP_LOSS;
    }

    /* Випадок 3: Минулий пакет (diff_exp < 0) */
    int16_t diff_max = (int16_t)(tr->seq_max - seq);
    if (diff_max >= 64 || diff_max < 0) {
        return PKT_STALE_DROP; /* Поза межами 64-бітного вікна */
    }

    /* Перевіряємо дублікат за бітовою маскою */
    if (tr->recv_mask & (1ULL << diff_max)) {
        return PKT_DUPLICATE;
    }

    /* Запізнілий пакет, якого ще не було */
    tr->recv_mask |= (1ULL << diff_max);
    return PKT_REORDERED;
}
