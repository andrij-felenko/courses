#include <stdio.h>
#include <stdbool.h>
#include <stdatomic.h>

// Явне розділення трьох станів результату асинхронної операції
typedef enum {
    ASYNC_SUCCESS = 0,
    ASYNC_ERROR_FAILED = 1,
    ASYNC_CANCELED = 2
} async_status_t;

// Структура токена скасування
typedef struct {
    atomic_bool* is_canceled;
} cancellation_token_t;

// Перевірка стану токена скасування
bool is_cancellation_requested(const cancellation_token_t* token) {
    return token && token->is_canceled && atomic_load_explicit(token->is_canceled, memory_order_acquire);
}

// Низькорівнева функція обчислення
async_status_t compute_subtask_c(int step, const cancellation_token_t* token, int* out_result) {
    if (is_cancellation_requested(token)) {
        return ASYNC_CANCELED; // Повернення статусу скасування
    }
    if (step < 0) {
        return ASYNC_ERROR_FAILED; // Помилка виконання
    }
    *out_result = step * 42;
    return ASYNC_SUCCESS;
}

// Високорівнева функція асинхронного ланцюжка
async_status_t execute_pipeline_c(int steps, const cancellation_token_t* token, int* out_total) {
    int accum = 0;
    for (int i = 0; i < steps; ++i) {
        if (is_cancellation_requested(token)) {
            return ASYNC_CANCELED;
        }

        int sub_res = 0;
        async_status_t status = compute_subtask_c(i, token, &sub_res);

        if (status != ASYNC_SUCCESS) {
            // Передаємо статус (ASYNC_CANCELED або ASYNC_ERROR_FAILED) нагору без витоків
            return status;
        }
        accum += sub_res;
    }
    *out_total = accum;
    return ASYNC_SUCCESS;
}
