#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ANTI_REPLAY_WIN_SIZE 64ULL

typedef struct {
    uint64_t max_seq;
    uint64_t bitmap;
    uint64_t packets_accepted;
    uint64_t packets_rejected_duplicate;
    uint64_t packets_rejected_stale;
} anti_replay_filter_t;

void anti_replay_init(anti_replay_filter_t *filter) {
    if (!filter) return;
    filter->max_seq = 0;
    filter->bitmap = 0;
    filter->packets_accepted = 0;
    filter->packets_rejected_duplicate = 0;
    filter->packets_rejected_stale = 0;
}

/*
 * Перевірка та оновлення стану фільтра за один крок.
 * Повертає true, якщо пакет валідний і прийнятий; false, якщо це повтор або застарілий пакет.
 */
bool anti_replay_process(anti_replay_filter_t *filter, uint64_t seq) {
    if (!filter) return false;

    /* Перший пакет у системі */
    if (filter->packets_accepted == 0 && filter->max_seq == 0 && filter->bitmap == 0) {
        filter->max_seq = seq;
        filter->bitmap = 1ULL;
        filter->packets_accepted++;
        return true;
    }

    /* Випадок 1: Номер більший за поточний максимум (рух вікна вперед) */
    if (seq > filter->max_seq) {
        uint64_t diff = seq - filter->max_seq;
        if (diff < ANTI_REPLAY_WIN_SIZE) {
            filter->bitmap = (filter->bitmap << diff) | 1ULL;
        } else {
            /* Стрибок номера перевищив розмір усього вікна: історія повністю витісняється */
            filter->bitmap = 1ULL;
        }
        filter->max_seq = seq;
        filter->packets_accepted++;
        return true;
    }

    /* Випадок 2: Номер застарілий і випав за межі лівого краю вікна */
    uint64_t diff = filter->max_seq - seq;
    if (diff >= ANTI_REPLAY_WIN_SIZE) {
        filter->packets_rejected_stale++;
        return false;
    }

    /* Випадок 3: Номер потрапляє всередину поточного вікна */
    uint64_t mask = 1ULL << diff;
    if (filter->bitmap & mask) {
        /* Біт уже встановлено — це повторне перегравання */
        filter->packets_rejected_duplicate++;
        return false;
    }

    /* Пакет легітимний, встановлюємо відповідний біт */
    filter->bitmap |= mask;
    filter->packets_accepted++;
    return true;
}
