#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <pthread.h>

#define BITS_PER_WORD 64
#define NUM_WORDS     4
#define TOTAL_TAGS    (BITS_PER_WORD * NUM_WORDS)
#define NUM_THREADS   4
#define OPS_PER_THREAD 100000

/* Структура одного слова бітової карти sbitmap */
typedef struct {
    _Atomic uint64_t map;
} sbitmap_word_t;

/* Головна структура масштабованої бітової карти */
typedef struct {
    sbitmap_word_t words[NUM_WORDS];
    size_t depth;
} sbitmap_t;

static void sbitmap_init(sbitmap_t *sb, size_t depth) {
    sb->depth = depth;
    for (size_t i = 0; i < NUM_WORDS; i++) {
        atomic_init(&sb->words[i].map, 0);
    }
}

/* 
 * Атомарне виділення тегу з використанням локальної підказки (hint).
 * Повертає номер тегу (0..TOTAL_TAGS-1) або -1, якщо всі теги зайняті.
 */
static int sbitmap_get(sbitmap_t *sb, unsigned int *hint) {
    size_t start_word = (*hint / BITS_PER_WORD) % NUM_WORDS;
    
    for (size_t i = 0; i < NUM_WORDS; i++) {
        size_t w_idx = (start_word + i) % NUM_WORDS;
        sbitmap_word_t *w = &sb->words[w_idx];
        
        uint64_t val = atomic_load_explicit(&w->map, memory_order_relaxed);
        while (val != ~0ULL) {
            /* Пошук першого нульового біта через інструкцію ctz */
            int bit = __builtin_ctzll(~val);
            if (bit >= BITS_PER_WORD) break;
            
            uint64_t mask = 1ULL << bit;
            if (!(val & mask)) {
                /* Атомарна спроба забронювати біт з Acquire-семантикою */
                if (atomic_compare_exchange_weak_explicit(&w->map, &val, val | mask,
                                                           memory_order_acquire,
                                                           memory_order_relaxed)) {
                    unsigned int tag = (unsigned int)(w_idx * BITS_PER_WORD + bit);
                    *hint = tag + 1; /* Оновлюємо локальну підказку */
                    return tag;
                }
            }
        }
    }
    return -1; /* Всі теги вичерпано */
}

/* 
 * Повернення тегу у пул із Release-семантикою 
 */
static void sbitmap_clear(sbitmap_t *sb, unsigned int tag) {
    size_t w_idx = tag / BITS_PER_WORD;
    unsigned int bit = tag % BITS_PER_WORD;
    uint64_t mask = ~(1ULL << bit);
    
    atomic_fetch_and_explicit(&sb->words[w_idx].map, mask, memory_order_release);
}

typedef struct {
    sbitmap_t *sb;
    int thread_id;
} worker_args_t;

static void *worker_func(void *arg) {
    worker_args_t *wargs = (worker_args_t *)arg;
    sbitmap_t *sb = wargs->sb;
    unsigned int hint = wargs->thread_id * 16;
    size_t allocated_count = 0;

    for (int i = 0; i < OPS_PER_THREAD; i++) {
        int tag = sbitmap_get(sb, &hint);
        if (tag >= 0) {
            allocated_count++;
            /* Імітація передачі команди та виконання I/O */
            sbitmap_clear(sb, (unsigned int)tag);
        }
    }
    printf("Потік C [%d] успішно обробив %zu операцій тегування.\n", wargs->thread_id, allocated_count);
    return NULL;
}

int main(void) {
    sbitmap_t sb;
    sbitmap_init(&sb, TOTAL_TAGS);

    pthread_t threads[NUM_THREADS];
    worker_args_t args[NUM_THREADS];

    printf("Запуск sbitmap C-симулятора (%d тегів, %d потоків)...\n", TOTAL_TAGS, NUM_THREADS);

    for (int i = 0; i < NUM_THREADS; i++) {
        args[i].sb = &sb;
        args[i].thread_id = i;
        pthread_create(&threads[i], NULL, worker_func, &args[i]);
    }

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("Тестування C-алокатора sbitmap завершено успішно.\n");
    return 0;
}
