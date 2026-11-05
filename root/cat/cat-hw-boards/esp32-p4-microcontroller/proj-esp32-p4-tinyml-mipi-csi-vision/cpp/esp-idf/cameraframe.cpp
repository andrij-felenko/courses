#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_timer.h"
#include "esp_cache.h"

struct CameraFrame {
    uint8_t* buffer;
    size_t size;
    uint64_t timestamp;
};

class VisionPipeline {
private:
    QueueHandle_t frame_queue_;

    static void inference_task_entry(void* arg) {
        auto* self = static_cast<VisionPipeline*>(arg);
        CameraFrame frame;
        while (true) {
            if (xQueueReceive(self->frame_queue_, &frame, portMAX_DELAY) == pdTRUE) {
                // Інвалідація кешу пам'яті для когерентності даних
                esp_cache_msync(frame.buffer, frame.size, ESP_CACHE_MSYNC_FLAG_DIR_M2C);
                
                int64_t start_time = esp_timer_get_time();
                // Виконання інференсу нейронної мережі на Core 1
                int64_t latency = esp_timer_get_time() - start_time;
                (void)latency;
            }
        }
    }

public:
    void init() {
        frame_queue_ = xQueueCreate(2, sizeof(CameraFrame));
        xTaskCreatePinnedToCore(inference_task_entry, "nn_task", 8192, this, 5, nullptr, 1);
    }
};
