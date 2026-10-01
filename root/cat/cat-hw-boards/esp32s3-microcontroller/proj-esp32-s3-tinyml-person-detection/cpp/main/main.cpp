#include <esp_heap_caps.h>
#include <esp_log.h>
#include <esp_system.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#include "camera_stream.hpp"
#include "frame_buffer_queue.hpp"
#include "tinyml_pipeline.hpp"

static const char* TAG = "MainApp";

struct PipelineContext {
    esp32s3::FrameBufferQueue* queue;
    esp32s3::TinyMLPipeline* pipeline;
};

static void inference_task_adapter(void* arg) {
    auto* ctx = static_cast<PipelineContext*>(arg);
    ESP_LOGI(TAG, "Задачу інференсу TinyML запущено на ядрі 1");

    while (true) {
        // Отримуємо кадр із черги (RAII обгортка ScopedFrame автоматично поверне буфер у драйвер)
        auto frame = ctx->queue->pop(portMAX_DELAY);
        if (frame.valid()) {
            auto result = ctx->pipeline->run_inference(frame);
            ESP_LOGI(TAG, "Інференс завершено за %u мс | Клас: %d | Впевненість: %.2f",
                     result.inference_time_ms, result.label_id, result.confidence);
        }
    }
}

extern "C" void app_main() {
    ESP_LOGI(TAG, "Запуск асинхронного конвеєра TinyML детектора на ESP32-S3");

    // Перевірка апаратної Octal PSRAM
    size_t psram_size = heap_caps_get_total_size(MALLOC_CAP_SPIRAM);
    if (psram_size == 0) {
        ESP_LOGE(TAG, "Помилка: Octal PSRAM не виявлено! Для роботи конвеєра потрібна PSRAM");
        return;
    }
    ESP_LOGI(TAG, "Знайдено Octal PSRAM: %u КБ", psram_size / 1024);

    // Створюємо чергу кадрів та модулі конвеєра
    static esp32s3::FrameBufferQueue frame_queue(2);
    static esp32s3::CameraStream camera(frame_queue);
    static esp32s3::TinyMLPipeline pipeline;

    if (!camera.init()) {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати систему камери");
        return;
    }

    if (!pipeline.init(256 * 1024)) {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати двигун TinyML");
        return;
    }

    // Запускаємо задачу захоплення кадрів на ядрі 0
    camera.start_capture_task();

    // Запускаємо задачу нейромережевого інференсу на ядрі 1
    static PipelineContext ctx{&frame_queue, &pipeline};
    xTaskCreatePinnedToCore(
        inference_task_adapter,
        "tinyml_infer_task",
        8192,
        &ctx,
        5,
        nullptr,
        1 // Ядро 1 для векторалізації PIE
    );

    // Головний цикл моніторингу купи пам'яті
    while (true) {
        vTaskDelay(pdMS_TO_TICKS(10000));
        size_t free_sram = heap_caps_get_free_size(MALLOC_CAP_INTERNAL);
        size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
        ESP_LOGI(TAG, "Моніторинг купи: Вільна SRAM: %u КБ, Вільна PSRAM: %u КБ",
                 free_sram / 1024, free_psram / 1024);
    }
}
