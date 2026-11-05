#include <stdio.h>
#include <stdbool.h>
#include <stdatomic.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Структура джерела та токена скасування для вбудованих систем
typedef struct {
    atomic_bool is_cancelled;
} cancellation_token_t;

// Ініціалізація атомарного токена
void cancellation_token_init(cancellation_token_t *token) {
    atomic_init(&token->is_cancelled, false);
}

// Виставляння сигналу скасування джерелом
void cancellation_token_cancel(cancellation_token_t *token) {
    atomic_store_explicit(&token->is_cancelled, true, memory_order_release);
}

// Перевірка стану токена у робочій задачі
bool cancellation_token_is_requested(const cancellation_token_t *token) {
    return atomic_load_explicit(&token->is_cancelled, memory_order_acquire);
}

// Фонова задача RTOS з контролем скасування
void worker_task(void *pvParameters) {
    cancellation_token_t *token = (cancellation_token_t *)pvParameters;
    printf("[RTOS Task] Запуск обробки периферії...\n");

    for (int step = 0; step < 100; step++) {
        // Контрольна точка перевірки прапорця
        if (cancellation_token_is_requested(token)) {
            printf("[RTOS Task] Сигнал скасування виявлено! Зупинка DMA...\n");
            // Детерміноване очищення апаратного стану периферії
            vTaskDelay(pdMS_TO_TICKS(10));
            printf("[RTOS Task] Ресурси очищено, задачу завершено безпечно.\n");
            vTaskDelete(NULL);
            return;
        }

        // Виконання порції обчислень
        vTaskDelay(pdMS_TO_TICKS(20));
    }

    printf("[RTOS Task] Обробку повністю завершено без скасування.\n");
    vTaskDelete(NULL);
}
