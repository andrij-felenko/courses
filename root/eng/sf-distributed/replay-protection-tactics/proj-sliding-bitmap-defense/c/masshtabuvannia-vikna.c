#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define WORDS_COUNT 16
#define TOTAL_WINDOW_BITS (WORDS_COUNT * 64)

typedef struct {
    uint64_t max_seq;
    uint64_t window[WORDS_COUNT];
} multiword_anti_replay_t;

void multiword_init(multiword_anti_replay_t *filter) {
    if (!filter) return;
    filter->max_seq = 0;
    memset(filter->window, 0, sizeof(filter->window));
}

bool multiword_check_and_update(multiword_anti_replay_t *filter, uint64_t seq) {
    if (seq > filter->max_seq) {
        uint64_t diff = seq - filter->max_seq;
        if (diff < TOTAL_WINDOW_BITS) {
            uint64_t words_shift = diff / 64;
            uint64_t bits_shift = diff % 64;
            
            // Зсув слів у буфері при необхідності
            for (int i = WORDS_COUNT - 1; i >= 0; --i) {
                uint64_t src = (i >= (int)words_shift) ? filter->window[i - words_shift] : 0ULL;
                uint64_t prev = (i > (int)words_shift && bits_shift > 0) ? filter->window[i - words_shift - 1] : 0ULL;
                filter->window[i] = (src << bits_shift) | (bits_shift > 0 ? (prev >> (64 - bits_shift)) : 0ULL);
            }
            filter->window[0] |= 1ULL;
        } else {
            memset(filter->window, 0, sizeof(filter->window));
            filter->window[0] = 1ULL;
        }
        filter->max_seq = seq;
        return true;
    }

    uint64_t diff = filter->max_seq - seq;
    if (diff >= TOTAL_WINDOW_BITS) {
        return false; // Застарілий пакет
    }

    uint64_t word_idx = diff / 64;
    uint64_t bit_idx = diff % 64;
    uint64_t mask = 1ULL << bit_idx;

    if (filter->window[word_idx] & mask) {
        return false; // Дублікат
    }

    filter->window[word_idx] |= mask;
    return true;
}
