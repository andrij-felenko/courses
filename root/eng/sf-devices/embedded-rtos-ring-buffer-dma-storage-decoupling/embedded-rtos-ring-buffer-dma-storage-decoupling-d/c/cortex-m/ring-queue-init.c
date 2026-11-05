#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Заголовні файли FreeRTOS та CMSIS ядра ARM Cortex-M */
#include "FreeRTOS.h"
#include "task.h"
#include "core_cm7.h"

/* Конфігурація розмірів: ємність черги обов'язково є степенем двійки */
#define QUEUE_CAPACITY           16U
#define QUEUE_MASK               (QUEUE_CAPACITY - 1U)
#define DMA_HALF_BUFFER_SIZE     1024U
#define CACHE_LINE_SIZE          32U

/* Вирівнювання пам'яті за розміром рядка кешу D-Cache */
#define ALIGNED_DMA_BUFFER       __attribute__((aligned(CACHE_LINE_SIZE)))

/* Дескриптор заповненого блоку даних */
typedef struct {
    uint8_t *p_buffer;
    uint32_t size_bytes;
    uint32_t sequence_id;
    uint32_t timestamp_ticks;
} block_descriptor_t;

/* Структура SPSC lock-free кільцевої черги дескрипторів */
typedef struct {
    block_descriptor_t descriptors[QUEUE_CAPACITY];
    volatile uint32_t head;
    volatile uint32_t tail;
    volatile uint32_t dropped_blocks;
    volatile uint32_t peak_watermark;
} spsc_ring_queue_t;

/* Апаратний подвійний буфер DMA та системна черга дескрипторів */
static ALIGNED_DMA_BUFFER uint8_t g_dma_ping_pong[2][DMA_HALF_BUFFER_SIZE];
static spsc_ring_queue_t g_block_queue;
static TaskHandle_t g_storage_task_handle = NULL;
static volatile uint32_t g_sequence_counter = 0;

/* Ініціалізація кільцевої черги */
void ring_queue_init(void) {
    memset(&g_block_queue, 0, sizeof(g_block_queue));
    g_sequence_counter = 0;
}

/* Обробник завершення передачі половини або повного буфера DMA */
void dma_half_full_transfer_isr(uint8_t active_buffer_idx) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    uint32_t current_head = g_block_queue.head;
    uint32_t current_tail = g_block_queue.tail;

    /* Обчислення поточної зайнятості черги дескрипторів */
    uint32_t occupancy = current_head - current_tail;

    /* Перевірка граничного стану переповнення черги */
    if (occupancy >= QUEUE_CAPACITY) {
        /* Стратегія drop-new: відкидаємо новий блок, фіксуючи помилку */
        g_block_queue.dropped_blocks++;
    } else {
        /* Запис дескриптора у поточну позицію виробника */
        uint32_t slot = current_head & QUEUE_MASK;
        g_block_queue.descriptors[slot].p_buffer        = g_dma_ping_pong[active_buffer_idx];
        g_block_queue.descriptors[slot].size_bytes      = DMA_HALF_BUFFER_SIZE;
        g_block_queue.descriptors[slot].sequence_id     = g_sequence_counter++;
        g_block_queue.descriptors[slot].timestamp_ticks = xTaskGetTickCountFromISR();

        /* Оновлення пікової ватерлінії заповнення для моніторингу */
        if (occupancy + 1U > g_block_queue.peak_watermark) {
            g_block_queue.peak_watermark = occupancy + 1U;
        }

        /* Апаратний бар'єр пам'яті: завершити запис дескриптора перед оновленням head */
        __DMB();

        /* Атомарне просування індексу виробника */
        g_block_queue.head = current_head + 1U;

        /* Пряме сповіщення задачі збереження без важких м'ютексів */
        if (g_storage_task_handle != NULL) {
            vTaskNotifyGiveFromISR(g_storage_task_handle, &xHigherPriorityTaskWoken);
        }
    }

    /* Запит негайного перемикання контексту за необхідності */
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

/* Зовнішній драйвер запису блоків у накопичувач (наприклад, SDMMC/FatFs) */
extern bool storage_driver_write_blocks(const uint8_t *data, uint32_t size_bytes);

/* Окремий потік-виконавець збереження даних у накопичувач */
void storage_worker_task(void *pvParameters) {
    (void)pvParameters;
    g_storage_task_handle = xTaskGetCurrentTaskHandle();

    for (;;) {
        /* Очікування сповіщення від переривання DMA */
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        /* Пакетна вичитка всіх доступних дескрипторів */
        while (g_block_queue.head != g_block_queue.tail) {
            uint32_t current_tail = g_block_queue.tail;
            uint32_t slot = current_tail & QUEUE_MASK;
            block_descriptor_t *p_desc = &g_block_queue.descriptors[slot];

            /* Інвалідація D-Cache перед читанням даних, записаних DMA контролером */
            SCB_InvalidateDCache_by_Addr((uint32_t *)p_desc->p_buffer, (int32_t)p_desc->size_bytes);

            /* Запис блоку в носій (операція може мати затримку до кількох сотень мс) */
            storage_driver_write_blocks(p_desc->p_buffer, p_desc->size_bytes);

            /* Бар'єр пам'яті перед оновленням індексу зчитування */
            __DMB();

            /* Звільнення слота в кільцевій черзі для виробника */
            g_block_queue.tail = current_tail + 1U;
        }
    }
}
