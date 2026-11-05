#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_timer.h"
#include "esp_cache.h"

typedef struct {
    uint8_t *frame_buffer;
    size_t buffer_size;
    uint64_t timestamp;
} camera_frame_t;

static QueueHandle_t frame_queue;

void IRAM_ATTR isp_finish_callback(uint8_t *buf, size_t len) {
    camera_frame_t frame = { 
        .frame_buffer = buf, 
        .buffer_size = len, 
        .timestamp = esp_timer_get_time() 
    };
    xQueueSendFromISR(frame_queue, &frame, NULL);
}

void inference_task(void *pvParameters) {
    camera_frame_t frame;
    for (;;) {
        if (xQueueReceive(frame_queue, &frame, portMAX_DELAY) == pdTRUE) {
            // Інвалідація кешу для збереження когерентності даних DMA
            esp_cache_msync(frame.frame_buffer, frame.buffer_size, ESP_CACHE_MSYNC_FLAG_DIR_M2C);
            
            int64_t start_time = esp_timer_get_time();
            // Виконання інференсу нейронної мережі на Core 1
            int64_t latency = esp_timer_get_time() - start_time;
            (void)latency;
        }
    }
}

void start_pipeline(void) {
    frame_queue = xQueueCreate(2, sizeof(camera_frame_t));
    xTaskCreatePinnedToCore(inference_task, "nn_task", 8192, NULL, 5, NULL, 1);
}
