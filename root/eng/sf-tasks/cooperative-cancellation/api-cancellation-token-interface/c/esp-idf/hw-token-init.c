#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

// Низькорівневе джерело та токен скасування
typedef struct {
    atomic_bool is_cancelled;
} hw_cancellation_token_t;

// Апаратний контекст периферійного модуля (DMA та регістри)
typedef struct {
    uint32_t dma_channel;
    uint32_t buffer_address;
    size_t block_size;
    volatile uint32_t *control_reg;
} hw_peripheral_t;

// Ініціалізація атомарного токена скасування
void hw_token_init(hw_cancellation_token_t *token) {
    atomic_init(&token->is_cancelled, false);
}

// Перевірка стану токена з семантикою acquire
inline static bool hw_token_is_requested(const hw_cancellation_token_t *token) {
    return atomic_load_explicit(&token->is_cancelled, memory_order_acquire);
}

// Виклики з ISR або фонового потоку з семантикою release
void hw_token_cancel_from_isr(hw_cancellation_token_t *token) {
    atomic_store_explicit(&token->is_cancelled, true, memory_order_release);
}

// Апаратне скидання периферії та вивільнення шини DMA
static void hw_peripheral_safe_stop(hw_peripheral_t *dev) {
    printf("[HW Clean] Зупинка DMA каналу %lu...\n", (unsigned long)dev->dma_channel);
    // Маскування переривань та деактивація біта у регістрі керування
    if (dev->control_reg) {
        *(dev->control_reg) &= ~(1U << 0); // Скидаємо біт ENABLE
    }
    // Очікування завершення шинного циклу
    vTaskDelay(pdMS_TO_TICKS(2));
    printf("[HW Clean] Периферію переведено у безпечний стан.\n");
}

// Задача обробки апаратного потоку даних
void hw_dma_processing_task(void *pvParameters) {
    hw_cancellation_token_t *token = (hw_cancellation_token_t *)pvParameters;
    uint32_t dummy_reg = 1U; // Імітація апаратного регістра CR1
    hw_peripheral_t dev = {
        .dma_channel = 1,
        .buffer_address = 0x20001000,
        .block_size = 512,
        .control_reg = &dummy_reg
    };

    printf("[Task] Запуск передачі блоків даних через DMA...\n");

    for (int block = 0; block < 20; block++) {
        // Контрольна точка перевірки токена перед запуском чергового блоку DMA
        if (hw_token_is_requested(token)) {
            printf("[Task] Виявлено сигнал скасування на блоці %d!\n", block);
            hw_peripheral_safe_stop(&dev);
            vTaskDelete(NULL);
            return;
        }

        // Імітація виконання передачі блоку DMA
        vTaskDelay(pdMS_TO_TICKS(15));
    }

    printf("[Task] Усі блоки даних передано успішно.\n");
    vTaskDelete(NULL);
}
