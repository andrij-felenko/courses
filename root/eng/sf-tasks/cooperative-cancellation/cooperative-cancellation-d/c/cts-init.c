#include <stdbool.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>

// Токен скасування в C — містить вказівник на атомарний прапорець тільки для читання
typedef struct {
    const atomic_bool *is_cancelled;
} CancellationToken;

// Джерело скасування в C — володіє атомарним прапорцем та керує його станом
typedef struct {
    atomic_bool cancelled_flag;
} CancellationTokenSource;

// Ініціалізація джерела скасування
void cts_init(CancellationTokenSource *cts) {
    atomic_init(&cts->cancelled_flag, false);
}

// Атомарна генерація сигналу скасування
void cts_cancel(CancellationTokenSource *cts) {
    atomic_store_explicit(&cts->cancelled_flag, true, memory_order_release);
}

// Отримання токена скасування для передачі робочій задачі
CancellationToken cts_get_token(CancellationTokenSource *cts) {
    CancellationToken token = { .is_cancelled = &cts->cancelled_flag };
    return token;
}

// Перевірка стану токена в точці скасування (checkpoint)
bool token_is_cancellation_requested(CancellationToken token) {
    if (token.is_cancelled == NULL) {
        return false;
    }
    return atomic_load_explicit(token.is_cancelled, memory_order_acquire);
}

// Обчислювальна задача з точками перевірки в циклі
bool execute_computation(CancellationToken token, int total_steps) {
    for (int step = 0; step < total_steps; ++step) {
        // Точка скасування (checkpoint)
        if (token_is_cancellation_requested(token)) {
            // Безпечний вихід зі збереженням цілісності
            printf("Обчислення скасовано на кроці %d\n", step);
            return false;
        }

        // Виконання порції корисних обчислень
    }
    return true;
}
