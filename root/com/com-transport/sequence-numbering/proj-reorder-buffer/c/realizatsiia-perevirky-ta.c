#include <stdint.h>
#include <stdbool.h>

#define ANTI_REPLAY_WIN_SIZE 64ULL

typedef struct {
    uint64_t top_seq;     /* Найбільший валідний отриманий номер */
    uint64_t bitmap;      /* Бітова маска: біт k відповідає номеру (top_seq - k) */
    bool is_initialized;  /* Прапорець отримання першого пакета */
} anti_replay_t;

/* Ініціалізація вікна */
void anti_replay_init(anti_replay_t *ar) {
    ar->top_seq = 0;
    ar->bitmap = 0;
    ar->is_initialized = false;
}

/* Перевірка прийнятності номера seq (true = валідний новий пакет, false = дублікат або застарілий) */
bool anti_replay_check(const anti_replay_t *ar, uint64_t seq) {
    if (!ar->is_initialized) {
        return true; /* Перший пакет завжди валідний */
    }

    if (seq > ar->top_seq) {
        return true; /* Новий більший номер — випередження вікна */
    }

    uint64_t diff = ar->top_seq - seq;
    if (diff >= ANTI_REPLAY_WIN_SIZE) {
        return false; /* Пакет занадто старий (лівіше за ліву межу вікна) */
    }

    /* Перевіряємо біт на позиції diff: якщо 1 — дублікат, якщо 0 — очікуваний запізнілий */
    return (ar->bitmap & (1ULL << diff)) == 0;
}

/* Оновлення стану вікна після успішної автентифікації пакета */
void anti_replay_update(anti_replay_t *ar, uint64_t seq) {
    if (!ar->is_initialized) {
        ar->top_seq = seq;
        ar->bitmap = 1ULL;
        ar->is_initialized = true;
        return;
    }

    if (seq > ar->top_seq) {
        uint64_t shift = seq - ar->top_seq;
        if (shift < ANTI_REPLAY_WIN_SIZE) {
            ar->bitmap = (ar->bitmap << shift) | 1ULL;
        } else {
            /* Стрибок більше за розмір вікна — старі дані повністю витісняються */
            ar->bitmap = 1ULL;
        }
        ar->top_seq = seq;
    } else {
        uint64_t diff = ar->top_seq - seq;
        if (diff < ANTI_REPLAY_WIN_SIZE) {
            ar->bitmap |= (1ULL << diff);
        }
    }
}
