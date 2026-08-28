/* Обчислення паузи перед повторною спробою захоплення блокування */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

long calculate_backoff_delay_ms(int attempt, long base_ms, long max_ms) {
    long delay = base_ms * (1L << attempt);
    if (delay > max_ms) {
        delay = max_ms;
    }
    /* Додавання випадкового джитера від 0 до 50% */
    long jitter = rand() % (delay / 2 + 1);
    return delay + jitter;
}
