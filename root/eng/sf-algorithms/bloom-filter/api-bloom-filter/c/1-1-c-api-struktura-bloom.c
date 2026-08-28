#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct {
    uint8_t *bits;       /* Динамічний бітовий масив з 64-байтовим вирівнюванням */
    size_t num_bits;     /* Загальна кількість бітів у векторі (m) */
    size_t num_hashes;   /* Кількість хеш-функцій (k) */
    size_t count;        /* Кількість успішно вставлених у фільтр елементів (n) */
} bloom_filter_t;
