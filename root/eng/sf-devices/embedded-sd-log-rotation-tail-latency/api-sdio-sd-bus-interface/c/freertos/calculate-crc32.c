#include "ff.h"
#include "diskio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define LOG_PACKET_MAGIC    0x53444C47U // Сигнатура "SDLG"
#define SECTOR_SIZE         512U
#define BUFFER_SECTORS      32U
#define BUFFER_SIZE_BYTES   (SECTOR_SIZE * BUFFER_SECTORS) // 16384 байти
#define CACHE_LINE_SIZE     32U

// Фізичний бінарний пакет фіксованого розміру (64 байти, рівно 8 пакетів на сектор)
typedef struct {
    uint32_t magic;
    uint64_t seq_num;
    uint32_t timestamp_ms;
    uint16_t sensor_id;
    uint16_t payload_len;
    uint8_t  payload[40];
    uint32_t crc32;
} __attribute__((packed, aligned(4))) sd_log_packet_t;

// Контекст апаратного конвеєра подвійної буферизації
typedef struct {
    uint8_t buffer[2][BUFFER_SIZE_BYTES] __attribute__((aligned(CACHE_LINE_SIZE)));
    volatile uint32_t active_idx;
    volatile uint32_t fill_bytes;
    volatile bool dma_busy;
    TaskHandle_t worker_task;
    uint64_t next_seq;
    uint32_t drop_count;
    uint32_t current_lba;
} sd_dma_streamer_t;

static sd_dma_streamer_t g_streamer;

// Очищення рядків кешу ядра Cortex-M7 перед запуском DMA
extern void SCB_CleanDCache_by_Addr(uint32_t *addr, int32_t dsize);

// Обчислення контрольної суми CRC32 за алгоритмом IEEE 802.3
static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            crc = (crc >> 1) ^ (0xEDB88320U & -(crc & 1U));
        }
    }
    return ~crc;
}

// Ініціалізація апаратного конвеєра
void sd_streamer_init(TaskHandle_t worker_task, uint32_t start_lba) {
    memset(&g_streamer, 0, sizeof(g_streamer));
    g_streamer.worker_task = worker_task;
    g_streamer.current_lba = start_lba;
}

// Додавання телеметричного запису до поточного плеча буфера (викликається з робочих задач)
bool sd_streamer_submit(uint16_t sensor_id, const void *payload, uint16_t payload_len, uint32_t timestamp_ms) {
    if (payload_len > 40) return false;

    // Якщо поточний буфер заповнений, а попередній ще передається через DMA — скидаємо пакет
    if (g_streamer.fill_bytes + sizeof(sd_log_packet_t) > BUFFER_SIZE_BYTES) {
        if (g_streamer.dma_busy) {
            g_streamer.drop_count++;
            return false;
        }

        // Перемикання на сусіднє плече човникового буфера
        uint32_t full_buf_idx = g_streamer.active_idx;
        g_streamer.active_idx ^= 1;
        g_streamer.fill_bytes = 0;

        // Сповіщення фонової задачі про готовність буфера до вивантаження
        xTaskNotify(g_streamer.worker_task, full_buf_idx, eSetValueWithOverwrite);
    }

    sd_log_packet_t pkt;
    pkt.magic = LOG_PACKET_MAGIC;
    pkt.seq_num = ++g_streamer.next_seq;
    pkt.timestamp_ms = timestamp_ms;
    pkt.sensor_id = sensor_id;
    pkt.payload_len = payload_len;
    memset(pkt.payload, 0, sizeof(pkt.payload));
    if (payload && payload_len > 0) {
        memcpy(pkt.payload, payload, payload_len);
    }
    pkt.crc32 = calculate_crc32((const uint8_t *)&pkt, sizeof(pkt) - sizeof(uint32_t));

    uint8_t *dst = &g_streamer.buffer[g_streamer.active_idx][g_streamer.fill_bytes];
    memcpy(dst, &pkt, sizeof(pkt));
    g_streamer.fill_bytes += sizeof(pkt);

    return true;
}

// Обробник переривання завершення транзакції DMA периферії SDMMC
void SDIO_DMA_Complete_IRQHandler(void) {
    BaseType_t higher_priority_task_woken = pdFALSE;
    g_streamer.dma_busy = false;

    // Розблокування фонової задачі після завершення апаратного перенесення блоку
    vTaskNotifyGiveFromISR(g_streamer.worker_task, &higher_priority_task_woken);
    portYIELD_FROM_ISR(higher_priority_task_woken);
}

// Фонова задача вивантаження накопичених секторів у шину SDIO
void sd_streamer_worker_task(void *pvParameters) {
    uint32_t buffer_to_flush = 0;

    for (;;) {
        // Очікування сповіщення про заповнення чергового плеча буфера
        if (xTaskNotifyWait(0, ULONG_MAX, &buffer_to_flush, portMAX_DELAY) == pdTRUE) {
            g_streamer.dma_busy = true;

            uint8_t *flush_ptr = g_streamer.buffer[buffer_to_flush];

            // Примусове вивантаження брудних рядків кешу D-Cache в оперативну пам'ять
            SCB_CleanDCache_by_Addr((uint32_t *)flush_ptr, BUFFER_SIZE_BYTES);

            // Виклик потокового багатосекторного запису disk_write (ACMD23 + CMD25 через DMA)
            DRESULT dr = disk_write(0, flush_ptr, g_streamer.current_lba, BUFFER_SECTORS);
            if (dr == RES_OK) {
                // Очікування апаратного прапорця переривання завершення DMA з тайм-аутом 1000 мс
                if (ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(1000)) == 0) {
                    // Аварійний тайм-аут накопичувача (write stall перевищив 1 секунду)
                    g_streamer.dma_busy = false;
                } else {
                    g_streamer.current_lba += BUFFER_SECTORS;
                }
            } else {
                g_streamer.dma_busy = false;
            }
        }
    }
}
