#include <stdint.h>
#include <stdbool.h>

#define SRTP_REPLAY_WINDOW_SIZE 64

typedef enum {
    SRTP_REPLAY_OK = 0,
    SRTP_REPLAY_DUPLICATE = 1,
    SRTP_REPLAY_OLD = 2
} srtp_replay_status_t;

typedef struct {
    uint64_t max_index;    /* Найвищий успішно автентифікований індекс */
    uint64_t window_mask;  /* Бітова маска (біт 0 = max_index - 63) */
    bool initialized;
} srtp_replay_window_t;

srtp_replay_status_t srtp_check_replay(const srtp_replay_window_t *w, uint64_t index) {
    if (!w->initialized) {
        return SRTP_REPLAY_OK;
    }

    if (index > w->max_index) {
        return SRTP_REPLAY_OK; /* Новий пакет випереджає вікно */
    }

    uint64_t diff = w->max_index - index;
    if (diff >= SRTP_REPLAY_WINDOW_SIZE) {
        return SRTP_REPLAY_OLD; /* Занадто старий пакет поза межами вікна */
    }

    if ((w->window_mask & (1ULL << diff)) != 0) {
        return SRTP_REPLAY_DUPLICATE; /* Цей пакет уже було оброблено */
    }

    return SRTP_REPLAY_OK;
}

void srtp_update_replay(srtp_replay_window_t *w, uint64_t index) {
    if (!w->initialized) {
        w->max_index = index;
        w->window_mask = 1ULL;
        w->initialized = true;
        return;
    }

    if (index > w->max_index) {
        uint64_t shift = index - w->max_index;
        if (shift < SRTP_REPLAY_WINDOW_SIZE) {
            w->window_mask <<= shift;
        } else {
            w->window_mask = 0;
        }
        w->window_mask |= 1ULL;
        w->max_index = index;
    } else {
        uint64_t diff = w->max_index - index;
        if (diff < SRTP_REPLAY_WINDOW_SIZE) {
            w->window_mask |= (1ULL << diff);
        }
    }
}
