#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <inttypes.h>
#include <pthread.h>
#include <time.h>

#define HLC_MAX_DRIFT_MS 500ULL
#define HLC_SUCCESS 0
#define HLC_ERR_DRIFT 1
#define HLC_ERR_OVERFLOW 2

/* Структура мітки часу HLC */
typedef struct {
    uint64_t physical_ms; /* Фізична компонента l (мілісекунди Unix Epoch) */
    uint32_t logical;     /* Логічний лічильник c */
    uint32_t node_id;     /* Ідентифікатор вузла для повного порядку */
} hlc_timestamp_t;

/* Стан годинника вузла */
typedef struct {
    uint64_t l;
    uint32_t c;
    uint32_t node_id;
    uint64_t max_drift_ms;
    pthread_mutex_t lock;
} hlc_clock_t;

/* Отримання поточного системного фізичного часу в мілісекундах */
static uint64_t get_system_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

/* Ініціалізація годинника */
void hlc_init(hlc_clock_t *clk, uint32_t node_id, uint64_t max_drift_ms) {
    clk->l = get_system_time_ms();
    clk->c = 0;
    clk->node_id = node_id;
    clk->max_drift_ms = (max_drift_ms > 0) ? max_drift_ms : HLC_MAX_DRIFT_MS;
    pthread_mutex_init(&clk->lock, NULL);
}

void hlc_destroy(hlc_clock_t *clk) {
    pthread_mutex_destroy(&clk->lock);
}

/* Генерація мітки для локальної події або Send */
int hlc_now(hlc_clock_t *clk, hlc_timestamp_t *out_ts) {
    pthread_mutex_lock(&clk->lock);

    uint64_t pt = get_system_time_ms();
    uint64_t l_old = clk->l;

    if (pt > clk->l) {
        clk->l = pt;
        clk->c = 0;
    } else {
        clk->l = l_old;
        if (clk->c == UINT32_MAX) {
            pthread_mutex_unlock(&clk->lock);
            return HLC_ERR_OVERFLOW;
        }
        clk->c++;
    }

    out_ts->physical_ms = clk->l;
    out_ts->logical = clk->c;
    out_ts->node_id = clk->node_id;

    pthread_mutex_unlock(&clk->lock);
    return HLC_SUCCESS;
}

/* Оновлення при отриманні повідомлення (Receive) */
int hlc_update(hlc_clock_t *clk, const hlc_timestamp_t *remote_ts, hlc_timestamp_t *out_ts) {
    pthread_mutex_lock(&clk->lock);

    uint64_t pt = get_system_time_ms();

    /* Захист від аномального стрибка часу у віддаленому вузлі */
    if (remote_ts->physical_ms > pt + clk->max_drift_ms) {
        pthread_mutex_unlock(&clk->lock);
        return HLC_ERR_DRIFT;
    }

    uint64_t l_old = clk->l;
    uint64_t max_l = (l_old > remote_ts->physical_ms) ? l_old : remote_ts->physical_ms;
    if (pt > max_l) {
        max_l = pt;
    }

    if (max_l == l_old && max_l == remote_ts->physical_ms) {
        uint32_t max_c = (clk->c > remote_ts->logical) ? clk->c : remote_ts->logical;
        if (max_c == UINT32_MAX) {
            pthread_mutex_unlock(&clk->lock);
            return HLC_ERR_OVERFLOW;
        }
        clk->c = max_c + 1;
    } else if (max_l == l_old) {
        if (clk->c == UINT32_MAX) {
            pthread_mutex_unlock(&clk->lock);
            return HLC_ERR_OVERFLOW;
        }
        clk->c++;
    } else if (max_l == remote_ts->physical_ms) {
        if (remote_ts->logical == UINT32_MAX) {
            pthread_mutex_unlock(&clk->lock);
            return HLC_ERR_OVERFLOW;
        }
        clk->c = remote_ts->logical + 1;
    } else {
        clk->c = 0;
    }

    clk->l = max_l;

    out_ts->physical_ms = clk->l;
    out_ts->logical = clk->c;
    out_ts->node_id = clk->node_id;

    pthread_mutex_unlock(&clk->lock);
    return HLC_SUCCESS;
}

/* Лексикографічне порівняння двох міток (повний порядок) */
int hlc_compare(const hlc_timestamp_t *a, const hlc_timestamp_t *b) {
    if (a->physical_ms < b->physical_ms) return -1;
    if (a->physical_ms > b->physical_ms) return 1;
    if (a->logical < b->logical) return -1;
    if (a->logical > b->logical) return 1;
    if (a->node_id < b->node_id) return -1;
    if (a->node_id > b->node_id) return 1;
    return 0;
}

/* Пакування в 64-бітне значення: 48 бітів фізичного часу + 16 бітів лічильника */
uint64_t hlc_pack64(const hlc_timestamp_t *ts) {
    return ((ts->physical_ms & 0x0000FFFFFFFFFFFFULL) << 16) | (ts->logical & 0xFFFFULL);
}

void hlc_unpack64(uint64_t packed, uint32_t node_id, hlc_timestamp_t *out_ts) {
    out_ts->physical_ms = (packed >> 16) & 0x0000FFFFFFFFFFFFULL;
    out_ts->logical = (uint32_t)(packed & 0xFFFFULL);
    out_ts->node_id = node_id;
}

int main(void) {
    hlc_clock_t node_a, node_b;
    hlc_init(&node_a, 1, 500);
    hlc_init(&node_b, 2, 500);

    hlc_timestamp_t ts_send, ts_recv;

    /* Вузол A генерує подію відправки */
    hlc_now(&node_a, &ts_send);
    printf("Node A [Send]: l=%" PRIu64 ", c=%" PRIu32 ", node=%" PRIu32 "\n",
           ts_send.physical_ms, ts_send.logical, ts_send.node_id);

    /* Вузол B отримує повідомлення від A */
    int res = hlc_update(&node_b, &ts_send, &ts_recv);
    if (res == HLC_SUCCESS) {
        printf("Node B [Recv]: l=%" PRIu64 ", c=%" PRIu32 ", node=%" PRIu32 "\n",
               ts_recv.physical_ms, ts_recv.logical, ts_recv.node_id);
    }

    int cmp = hlc_compare(&ts_send, &ts_recv);
    printf("Causality verified: %s (ts_send < ts_recv)\n", (cmp < 0) ? "YES" : "NO");

    uint64_t packed = hlc_pack64(&ts_recv);
    printf("Packed 64-bit representation: 0x%016" PRIX64 "\n", packed);

    hlc_destroy(&node_a);
    hlc_destroy(&node_b);
    return 0;
}
