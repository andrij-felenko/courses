#ifndef USB_UVC_DEVICE_HPP
#define USB_UVC_DEVICE_HPP

#include <esp_log.h>
#include <tinyusb.h>
#include <tusb.h>
#include "camera_driver.hpp"

namespace esp32s3 {

class UsbUvcDevice {
public:
    explicit UsbUvcDevice(CameraDriver& camera) : camera_(camera) {}

    ~UsbUvcDevice() {
        stop();
    }

    bool init() {
        if (initialized_) {
            return true;
        }

        const tinyusb_config_t tusb_cfg = {
            .device_descriptor = nullptr,
            .string_descriptor = nullptr,
            .external_phy = false,
            .configuration_descriptor = nullptr
        };

        esp_err_t err = tinyusb_driver_install(&tusb_cfg);
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "Не вдалося ініціалізувати драйвер TinyUSB: 0x%x", err);
            return false;
        }

        initialized_ = true;
        ESP_LOGI(TAG, "Нативний USB-контролер ESP32-S3 ініціалізовано в режимі USB UVC (веб-камера)");
        return true;
    }

    void start_streaming_task() {
        if (!initialized_ || task_handle_) {
            return;
        }

        xTaskCreatePinnedToCore(
            uvc_task_adapter,
            "usb_uvc_task",
            4096,
            this,
            5,
            &task_handle_,
            1
        );
        ESP_LOGI(TAG, "Задачу передачі кадрів через USB UVC запущено на ядрі 1");
    }

    void stop() {
        if (task_handle_) {
            vTaskDelete(task_handle_);
            task_handle_ = nullptr;
        }

        if (initialized_) {
            tinyusb_driver_uninstall();
            initialized_ = false;
            ESP_LOGI(TAG, "USB UVC пристрій зупинено");
        }
    }

    [[nodiscard]] bool is_connected() const {
        return tud_mounted();
    }

private:
    static constexpr const char* TAG = "UsbUvcDevice";

    static void uvc_task_adapter(void* arg) {
        auto* self = static_cast<UsbUvcDevice*>(arg);
        self->uvc_task_loop();
    }

    void uvc_task_loop() {
        while (true) {
            if (tud_mounted()) {
                auto frame = camera_.capture();
                if (frame && frame->data() && frame->size() > 0) {
                    // Надсилаємо JPEG-кадр у зворотному конвеєрі ізохронного USB епоінту
                    tud_video_n_frame_xfer(0, 0, (void*)frame->data(), frame->size());
                }
            }
            vTaskDelay(pdMS_TO_TICKS(33)); // ~30 FPS по USB
        }
    }

    CameraDriver& camera_;
    bool initialized_{false};
    TaskHandle_t task_handle_{nullptr};
};

} // namespace esp32s3

#endif // USB_UVC_DEVICE_HPP
