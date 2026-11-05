#include "ff.h"
#include "FreeRTOS.h"
#include "task.h"
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BUFFER_SIZE_BYTES   (32 * 1024) // 32 КіБ (розмір кластера FatFs)
#define CACHE_LINE_SIZE     32

typedef struct {
    // Буфери вирівняні по межі рядка кешу процесора
    uint8_t buf_a[BUFFER_SIZE_BYTES] __attribute__((aligned(CACHE_LINE_SIZE)));
    uint8_t buf_b[BUFFER_SIZE_BYTES] __attribute__((aligned(CACHE_LINE_SIZE)));
    uint8_t *active_write_buf;
    uint8_t *dma_transmit_buf;
    uint32_t bytes_written;
    TaskHandle_t write_task_handle;
    volatile bool dma_in_progress;
} dma_double_buffer_t;

static dma_double_buffer_t g_dma_logger;

// Ініціалізація підсистеми подвійної буферизації
void dma_logger_init(TaskHandle_t consumer_task) {
    g_dma_logger.active_write_buf = g_dma_logger.buf_a;
    g_dma_logger.dma_transmit_buf = g_dma_logger.buf_b;
    g_dma_logger.bytes_written = 0;
    g_dma_logger.write_task_handle = consumer_task;
    g_dma_logger.dma_in_progress = false;
}

// Запис порції даних джерелом (сенсор або задача збору)
bool dma_logger_append(const void *data, uint32_t len) {
    if (len > BUFFER_SIZE_BYTES - g_dma_logger.bytes_written) {
        // Якщо передача попереднього буфера ще триває — переповнення
        if (g_dma_logger.dma_in_progress) {
            return false; // Хвостова затримка переповнила RAM
        }

        // Перемикання вказівників буферів
        uint8_t *temp = g_dma_logger.active_write_buf;
        g_dma_logger.active_write_buf = g_dma_logger.dma_transmit_buf;
        g_dma_logger.dma_transmit_buf = temp;
        g_dma_logger.bytes_written = 0;
        g_dma_logger.dma_in_progress = true;

        // Сповіщення задачі запису на носій
        xTaskNotifyGive(g_dma_logger.write_task_handle);
    }

    memcpy(&g_dma_logger.active_write_buf[g_dma_logger.bytes_written], data, len);
    g_dma_logger.bytes_written += len;
    return true;
}

// Демонічна задача запису вирівняних блоків у FatFs
void dma_storage_task(void *pvParameters) {
    FIL *log_file = (FIL *)pvParameters;
    UINT bw = 0;

    for (;;) {
        // Очікування завершення заповнення чергового буфера
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        // Очищення кешу перед стартом DMA передачі (для Cortex-M7)
        // SCB_CleanDCache_by_Addr((uint32_t *)g_dma_logger.dma_transmit_buf, BUFFER_SIZE_BYTES);

        // Потоковий запис повного вирівняного кластера у попередньо виділений файл
        FRESULT fr = f_write(log_file, g_dma_logger.dma_transmit_buf, BUFFER_SIZE_BYTES, &bw);
        (void)fr;

        // Звільнення буфера для наступного циклу
        g_dma_logger.dma_in_progress = false;
    }
}
