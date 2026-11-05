#include <stdio.h>
#include <stdbool.h>
#include <stdatomic.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "driver/gpio.h"

#define LATENCY_PROFILE_GPIO_PIN GPIO_NUM_18
#define CANCELLATION_BIT BIT0

// Контекст скасування з Event Group для розбудження з блокуючого сну
typedef struct {
    atomic_bool is_cancelled;
    EventGroupHandle_t event_group;
} async_cancellation_context_t;

// Ініціалізація контексту
void async_context_init(async_cancellation_context_t *ctx) {
    atomic_init(&ctx->is_cancelled, false);
    ctx->event_group = xEventGroupCreate();
}

// Подача сигналу скасування з виставлянням GPIO для профілювання затримки
void async_context_cancel(async_cancellation_context_t *ctx) {
    // Встановлюємо GPIO пин для вимірювання затримки логічним аналізатором
    gpio_set_level(LATENCY_PROFILE_GPIO_PIN, 1);
    atomic_store_explicit(&ctx->is_cancelled, true, memory_order_release);
    // Розбудження блокованого потоку через системний Event Group
    xEventGroupSetBits(ctx->event_group, CANCELLATION_BIT);
}

// Фонова задача з безпечним розбудженням з блокуючого стану
void async_worker_task(void *pvParameters) {
    async_cancellation_context_t *ctx = (async_cancellation_context_t *)pvParameters;
    printf("[Worker] Задача увійшла в цикл обробки подій...\n");

    while (1) {
        // Замість безкінечного блокування очікуємо з таймаутом 50 мс
        EventBits_t uxBits = xEventGroupWaitBits(
            ctx->event_group,
            CANCELLATION_BIT,
            pdFALSE,
            pdFALSE,
            pdMS_TO_TICKS(50)
        );

        // Перевірка атомарного токена скасування після виходу з очікування
        if (atomic_load_explicit(&ctx->is_cancelled, memory_order_acquire) || (uxBits & CANCELLATION_BIT)) {
            printf("[Worker] Сигнал скасування отримано! Вивільнення ресурсів...\n");
            
            // Скидаємо GPIO пин, фіксуючи кінець затримки скасування
            gpio_set_level(LATENCY_PROFILE_GPIO_PIN, 0);
            
            vEventGroupDelete(ctx->event_group);
            printf("[Worker] Задачу детерміновано завершено.\n");
            vTaskDelete(NULL);
            return;
        }

        // Виконання корисного кроку обробки при відсутності скасування
        printf("[Worker] Крок обробки виконано.\n");
    }
}
