#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"

#define DMA_BUFFER_SIZE         256
#define DMA_CACHE_LINE_SIZE     32
#define DMA_BUFFER_COUNT        4
#define WORKER_QUEUE_LENGTH     16

// Перелік типів апаратних транзакцій
typedef enum {
    HW_TRANSACTION_SPI_FLASH_WRITE,
    HW_TRANSACTION_UART_BURST_PARSE,
    HW_TRANSACTION_SHUTDOWN
} hw_transaction_type_t;

// Дескриптор повідомлення черги (zero-copy передача)
typedef struct {
    hw_transaction_type_t type;
    uint8_t *dma_buffer;
    size_t length;
    uint32_t hardware_status;
    SemaphoreHandle_t sync_token;
} dma_descriptor_msg_t;

// Структура буфера з апаратним вирівнюванням під рядок кешу
typedef struct {
    uint8_t data[DMA_BUFFER_SIZE] __attribute__((aligned(DMA_CACHE_LINE_SIZE)));
    bool is_in_use;
} dma_aligned_buffer_t;

// Контекст апаратного потоку-виконавця
typedef struct {
    QueueHandle_t queue_handle;
    TaskHandle_t task_handle;
    dma_aligned_buffer_t pool[DMA_BUFFER_COUNT];
    uint32_t dropped_packets;
} hardware_worker_t;

static hardware_worker_t g_hw_worker;

// Апаратна інвалідація кешу для усунення застарілих даних (stale data)
static inline void hardware_cache_invalidate(void *addr, size_t size) {
    #if defined(__arm__)
    uint32_t start_addr = (uint32_t)addr & ~(DMA_CACHE_LINE_SIZE - 1);
    uint32_t end_addr = ((uint32_t)addr + size + DMA_CACHE_LINE_SIZE - 1) & ~(DMA_CACHE_LINE_SIZE - 1);
    for (uint32_t p = start_addr; p < end_addr; p += DMA_CACHE_LINE_SIZE) {
        asm volatile("mcr p15, 0, %0, c7, c6, 1" : : "r"(p) : "memory");
    }
    #endif
    asm volatile("" : : : "memory"); // Бар'єр компілятора
}

// Обробка корисного навантаження у потоці-виконавці
static void process_hardware_payload(const dma_descriptor_msg_t *desc) {
    // Інвалідуємо кеш перед читанням даних від контролера DMA
    hardware_cache_invalidate(desc->dma_buffer, desc->length);

    // Імітація обробки: розрахунок контрольної суми
    if (desc->length > 0) {
        volatile uint8_t checksum = 0;
        for (size_t i = 0; i < desc->length; ++i) {
            checksum ^= desc->dma_buffer[i];
        }
        (void)checksum;
    }
}

// Головний цикл подій потоку-виконавця
static void hardware_worker_task(void *pvParameters) {
    hardware_worker_t *worker = (hardware_worker_t *)pvParameters;
    dma_descriptor_msg_t msg;

    for (;;) {
        // Потік блокується на черзі дескрипторів
        if (xQueueReceive(worker->queue_handle, &msg, portMAX_DELAY) == pdTRUE) {
            if (msg.type == HW_TRANSACTION_SHUTDOWN) {
                if (msg.sync_token != NULL) {
                    xSemaphoreGive(msg.sync_token);
                }
                break;
            }

            process_hardware_payload(&msg);

            // Сигналізація клієнтському потоку при синхронній взаємодії
            if (msg.sync_token != NULL) {
                xSemaphoreGive(msg.sync_token);
            }

            // Повернення вирівняного буфера назад у вільний пул
            for (int i = 0; i < DMA_BUFFER_COUNT; ++i) {
                if (worker->pool[i].data == msg.dma_buffer) {
                    worker->pool[i].is_in_use = false;
                    break;
                }
            }
        }
    }

    vTaskDelete(NULL);
}

// Обробник переривання DMA (ISR контекст)
void IRAM_ATTR dma_transfer_complete_isr(void) {
    BaseType_t high_task_woken = pdFALSE;
    hardware_worker_t *worker = &g_hw_worker;

    // Отримання заповненого буфера від апаратури
    uint8_t *completed_buf = worker->pool[0].data;
    size_t rx_len = DMA_BUFFER_SIZE;

    dma_descriptor_msg_t msg = {
        .type = HW_TRANSACTION_UART_BURST_PARSE,
        .dma_buffer = completed_buf,
        .length = rx_len,
        .hardware_status = 0x00,
        .sync_token = NULL
    };

    // Неблокуюча передача повідомлення у чергу воркера
    if (xQueueSendFromISR(worker->queue_handle, &msg, &high_task_woken) != pdTRUE) {
        worker->dropped_packets++; // Фіксація переповнення черги
    }

    // Негайне перемикання на високопріоритетний потік-виконавець
    portYIELD_FROM_ISR(high_task_woken);
}

// Ініціалізація модуля
bool hardware_worker_init(void) {
    memset(&g_hw_worker, 0, sizeof(g_hw_worker));

    g_hw_worker.queue_handle = xQueueCreate(WORKER_QUEUE_LENGTH, sizeof(dma_descriptor_msg_t));
    if (g_hw_worker.queue_handle == NULL) {
        return false;
    }

    BaseType_t ret = xTaskCreate(
        hardware_worker_task,
        "HwWorker",
        2048,
        &g_hw_worker,
        configMAX_PRIORITIES - 2,
        &g_hw_worker.task_handle
    );

    return (ret == pdPASS);
}
