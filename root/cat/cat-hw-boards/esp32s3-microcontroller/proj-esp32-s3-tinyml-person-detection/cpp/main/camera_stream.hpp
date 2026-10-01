#ifndef CAMERA_STREAM_HPP
#define CAMERA_STREAM_HPP

#include <esp_camera.h>
#include <esp_heap_caps.h>
#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#include "frame_buffer_queue.hpp"

namespace esp32s3 {

class CameraStream {
public:
    explicit CameraStream(FrameBufferQueue& queue) : queue_(queue) {}

    ~CameraStream() {
        stop();
    }

    bool init() {
        if (initialized_) return true;

        if (!heap_caps_get_total_size(MALLOC_CAP_SPIRAM)) {
            ESP_LOGE(TAG, "Octal PSRAM не знайдено! Кадрові буфери вимагають PSRAM");
            return false;
        }

        camera_config_t config{};
        config.ledc_channel = LEDC_CHANNEL_0;
        config.ledc_timer = LEDC_TIMER_0;
        config.pin_d0 = 11;
        config.pin_d1 = 9;
        config.pin_d2 = 8;
        config.pin_d3 = 10;
        config.pin_d4 = 12;
        config.pin_d5 = 18;
        config.pin_d6 = 17;
        config.pin_d7 = 16;
        config.pin_xclk = 15;
        config.pin_pclk = 13;
        config.pin_vsync = 6;
        config.pin_href = 7;
        config.pin_sccb_sda = 4;
        config.pin_sccb_scl = 5;
        config.pin_pwdn = -1;
        config.pin_reset = -1;
        config.xclk_freq_hz = 20000000;
        config.pixel_format = PIXFORMAT_RGB565;
        config.frame_size = FRAMESIZE_96X96;
        config.jpeg_quality = 12;
        config.fb_count = 2; // Подвійна буферизація в Octal PSRAM
        config.fb_location = CAMERA_FB_IN_PSRAM;
        config.grab_mode = CAMERA_GRAB_LATEST;

        esp_err_t err = esp_camera_init(&config);
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "Не вдалося ініціалізувати камеру: 0x%x", err);
            return false;
        }

        initialized_ = true;
        ESP_LOGI(TAG, "Камеру ініціалізовано (96x96 RGB565 у Octal PSRAM)");
        return true;
    }

    bool start_capture_task() {
        if (!initialized_ || task_handle_) return false;

        BaseType_t ret = xTaskCreatePinnedToCore(
            capture_task_adapter,
            "cam_capture_task",
            4096,
            this,
            5,
            &task_handle_,
            0 // Запускаємо захоплення на ядрі 0
        );

        if (ret != pdPASS) {
            ESP_LOGE(TAG, "Не вдалося створити задачу захоплення кадрів");
            return false;
        }

        ESP_LOGI(TAG, "Задачу захоплення кадрів запущено на ядрі 0");
        return true;
    }

    void stop() {
        if (task_handle_) {
            vTaskDelete(task_handle_);
            task_handle_ = nullptr;
        }
        if (initialized_) {
            esp_camera_deinit();
            initialized_ = false;
        }
    }

private:
    static constexpr const char* TAG = "CameraStream";

    static void capture_task_adapter(void* arg) {
        auto* self = static_cast<CameraStream*>(arg);
        self->capture_loop();
    }

    void capture_loop() {
        while (true) {
            camera_fb_t* fb = esp_camera_fb_get();
            if (fb) {
                if (!queue_.push(fb, pdMS_TO_TICKS(10))) {
                    // Якщо черга заповнена, push сам поверне fb
                }
            } else {
                ESP_LOGW(TAG, "Помилка захоплення кадру");
            }
            vTaskDelay(pdMS_TO_TICKS(20)); // ~50 FPS захоплення
        }
    }

    FrameBufferQueue& queue_;
    bool initialized_{false};
    TaskHandle_t task_handle_{nullptr};
};

} // namespace esp32s3

#endif // CAMERA_STREAM_HPP
