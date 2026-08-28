#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
#include <assert.h>

#define WINDOW_WORDS 2
#define BITS_PER_WORD 64
#define WINDOW_BITS (WINDOW_WORDS * BITS_PER_WORD)

typedef enum {
    REPLAY_OK = 0,
    REPLAY_DUPLICATE = 1,
    REPLAY_TOO_OLD = 2
} replay_status_t;

typedef struct {
    uint64_t seq_max;                       // найбільший підтверджений номер
    uint64_t bitmap[WINDOW_WORDS];          // бітова маска вікна
} replay_window_t;

// Ініціалізація або повне скидання стану вікна
void replay_window_init(replay_window_t *w) {
    w->seq_max = 0;
    memset(w->bitmap, 0, sizeof(w->bitmap));
}

// 1. Попередня перевірка без зміни стану (виконується ДО розшифрування/HMAC)
replay_status_t replay_window_check(const replay_window_t *w, uint64_t seq) {
    if (seq == 0) {
        return REPLAY_TOO_OLD;              // порядковий номер 0 заборонено стандартами
    }

    if (seq > w->seq_max) {
        return REPLAY_OK;                   // новий пакет попереду вікна
    }

    uint64_t diff = w->seq_max - seq;
    if (diff >= WINDOW_BITS) {
        return REPLAY_TOO_OLD;              // пакет занадто старий, лівіше вікна
    }

    size_t word_idx = (size_t)(diff / BITS_PER_WORD);
    size_t bit_idx = (size_t)(diff % BITS_PER_WORD);

    if ((w->bitmap[word_idx] & ((uint64_t)1 << bit_idx)) != 0) {
        return REPLAY_DUPLICATE;            // пакет уже був успішно отриманий
    }

    return REPLAY_OK;
}

// 2. Фіксація номера у вікні (виконується ТІЛЬКИ ПІСЛЯ успішної перевірки криптографії)
void replay_window_commit(replay_window_t *w, uint64_t seq) {
    if (seq > w->seq_max) {
        uint64_t diff = seq - w->seq_max;
        if (diff < WINDOW_BITS) {
            // Зсув бітової маски вліво на diff бітів через межі 64-бітних слів
            size_t word_shift = (size_t)(diff / BITS_PER_WORD);
            size_t bit_shift = (size_t)(diff % BITS_PER_WORD);

            for (int i = WINDOW_WORDS - 1; i >= 0; --i) {
                int src = i - (int)word_shift;
                uint64_t val = (src >= 0) ? (w->bitmap[src] << bit_shift) : 0;
                if (src > 0 && bit_shift > 0) {
                    val |= (w->bitmap[src - 1] >> (BITS_PER_WORD - bit_shift));
                }
                w->bitmap[i] = val;
            }
        } else {
            // Стрибок більше або дорівнює ширині вікна: очищаємо всю стару маску
            memset(w->bitmap, 0, sizeof(w->bitmap));
        }

        w->seq_max = seq;
        w->bitmap[0] |= (uint64_t)1;        // позначаємо біт 0 для нового seq_max
    } else {
        uint64_t diff = w->seq_max - seq;
        if (diff < WINDOW_BITS) {
            size_t word_idx = (size_t)(diff / BITS_PER_WORD);
            size_t bit_idx = (size_t)(diff % BITS_PER_WORD);
            w->bitmap[word_idx] |= ((uint64_t)1 << bit_idx);
        }
    }
}
