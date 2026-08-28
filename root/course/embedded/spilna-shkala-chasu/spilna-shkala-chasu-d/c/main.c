#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define TIMESYNC_WINDOW_SIZE 16
#define TIMESYNC_MAX_RTT_US  200000ULL /* 200 мс максимальний прийнятний RTT */
#define TIMESYNC_ALPHA_FP    10        /* Коефіцієнт згладжування 0.10 у фіксованій комі (x100) */

typedef struct {
    uint64_t t1_client_us;
    uint64_t t2_server_us;
    uint64_t t3_server_us;
    uint64_t t4_client_us;
    int64_t  offset_us;
    uint64_t rtt_us;
    bool     valid;
} timesync_sample_t;

typedef struct {
    timesync_sample_t samples[TIMESYNC_WINDOW_SIZE];
    size_t   head;
    size_t   count;
    int64_t  filtered_offset_us;
    int64_t  skew_ppm_x1000;      /* Дрейф частоти в ppm, помножений на 1000 */
    uint64_t last_sync_local_us;
    uint64_t min_rtt_us;
    bool     is_synchronized;
} timesync_filter_t;

void timesync_filter_init(timesync_filter_t *filter) {
    if (!filter) return;
    filter->head = 0;
    filter->count = 0;
    filter->filtered_offset_us = 0;
    filter->skew_ppm_x1000 = 0;
    filter->last_sync_local_us = 0;
    filter->min_rtt_us = UINT64_MAX;
    filter->is_synchronized = false;

    for (size_t i = 0; i < TIMESYNC_WINDOW_SIZE; ++i) {
        filter->samples[i].valid = false;
    }
}

bool timesync_filter_update(timesync_filter_t *filter, 
                            uint64_t t1_us, uint64_t t2_us, 
                            uint64_t t3_us, uint64_t t4_us) {
    if (!filter || t4_us < t1_us) return false;

    /* Обчислення RTT та часу обробки */
    uint64_t proc_time_us = (t3_us >= t2_us) ? (t3_us - t2_us) : 0;
    uint64_t total_roundtrip = t4_us - t1_us;
    
    if (total_roundtrip < proc_time_us) return false;
    uint64_t rtt_us = total_roundtrip - proc_time_us;

    /* Відкидання аномальних сплесків затримки мережі */
    if (rtt_us > TIMESYNC_MAX_RTT_US) {
        return false;
    }

    /* Зміщення: θ = ((t2 - t1) + (t3 - t4)) / 2 */
    int64_t diff1 = (int64_t)t2_us - (int64_t)t1_us;
    int64_t diff2 = (int64_t)t3_us - (int64_t)t4_us;
    int64_t raw_offset_us = (diff1 + diff2) / 2;

    /* Запис у кільцевий буфер */
    timesync_sample_t *s = &filter->samples[filter->head];
    s->t1_client_us = t1_us;
    s->t2_server_us = t2_us;
    s->t3_server_us = t3_us;
    s->t4_client_us = t4_us;
    s->offset_us = raw_offset_us;
    s->rtt_us = rtt_us;
    s->valid = true;

    filter->head = (filter->head + 1) % TIMESYNC_WINDOW_SIZE;
    if (filter->count < TIMESYNC_WINDOW_SIZE) {
        filter->count++;
    }

    /* Пошук вибірки з мінімальним RTT у поточному вікні */
    uint64_t best_rtt = UINT64_MAX;
    int64_t  best_offset = 0;

    for (size_t i = 0; i < TIMESYNC_WINDOW_SIZE; ++i) {
        if (filter->samples[i].valid && filter->samples[i].rtt_us < best_rtt) {
            best_rtt = filter->samples[i].rtt_us;
            best_offset = filter->samples[i].offset_us;
        }
    }

    filter->min_rtt_us = best_rtt;

    /* Фільтрація EWMA */
    if (!filter->is_synchronized) {
        /* Перше захоплення: ініціалізація значенням найкращої вибірки */
        filter->filtered_offset_us = best_offset;
        filter->is_synchronized = true;
    } else {
        /* Плавне згладжування фази */
        int64_t delta = best_offset - filter->filtered_offset_us;
        filter->filtered_offset_us += (delta * TIMESYNC_ALPHA_FP) / 100;
    }

    filter->last_sync_local_us = t4_us;
    return true;
}

uint64_t timesync_local_to_server_us(const timesync_filter_t *filter, uint64_t local_now_us) {
    if (!filter || !filter->is_synchronized) {
        return local_now_us;
    }

    /* Базове зміщення */
    int64_t res = (int64_t)local_now_us + filter->filtered_offset_us;

    /* Екстраполяція дрейфу, якщо відомий skew */
    if (filter->last_sync_local_us > 0 && local_now_us > filter->last_sync_local_us) {
        uint64_t dt_us = local_now_us - filter->last_sync_local_us;
        int64_t skew_correction = (int64_t)((dt_us * filter->skew_ppm_x1000) / 1000000000LL);
        res += skew_correction;
    }

    return (res > 0) ? (uint64_t)res : 0ULL;
}

uint64_t timesync_server_to_local_us(const timesync_filter_t *filter, uint64_t server_time_us) {
    if (!filter || !filter->is_synchronized) {
        return server_time_us;
    }

    int64_t res = (int64_t)server_time_us - filter->filtered_offset_us;
    return (res > 0) ? (uint64_t)res : 0ULL;
}
