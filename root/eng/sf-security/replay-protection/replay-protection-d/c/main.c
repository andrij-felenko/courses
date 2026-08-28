#include <stdint.h>
#include <stdbool.h>

#define REPLAY_WIN_SIZE 64

typedef struct {
    uint64_t seq_max;
    uint64_t bitmap;
} replay_filter_t;

bool replay_filter_check(const replay_filter_t *f, uint64_t seq) {
    if (seq == 0) return false;
    if (seq > f->seq_max) return true; // новий пакет
    uint64_t diff = f->seq_max - seq;
    if (diff >= REPLAY_WIN_SIZE) return false; // занадто старий
    return (f->bitmap & ((uint64_t)1 << diff)) == 0; // true якщо ще не бачили
}

void replay_filter_commit(replay_filter_t *f, uint64_t seq) {
    if (seq > f->seq_max) {
        uint64_t diff = seq - f->seq_max;
        f->bitmap = (diff < REPLAY_WIN_SIZE) ? ((f->bitmap << diff) | 1) : 1;
        f->seq_max = seq;
    } else {
        uint64_t diff = f->seq_max - seq;
        if (diff < REPLAY_WIN_SIZE) {
            f->bitmap |= ((uint64_t)1 << diff);
        }
    }
}
