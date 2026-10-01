#ifndef CAMERA_DRIVER_HPP
#define CAMERA_DRIVER_HPP

#include <cstdint>
#include <memory>
#include <esp_log.h>
#include <esp_camera.h>
#include <esp_heap_caps.h>

namespace esp32s3 {

// RAII-обгортка для автоматичного повернення буфера камери в пулик
class CameraFrame {
public:
    explicit CameraFrame(camera_fb_t* fb) : fb_(fb) {}

    ~CameraFrame() {
        if (fb_) {
            esp_camera_fb_return(fb_);
        }
    }

    // Забороняємо копіювання для запобігання подвійному звільненню
    CameraFrame(const CameraFrame&) = delete;
    CameraFrame& operator=(const CameraFrame&) = delete;

    // Дозволяємо переміщення
    CameraFrame(CameraFrame&& other) noexcept : fb_(other.fb_) {
        other.fb_ = nullptr;
    }

    CameraFrame& operator=(CameraFrame&& other) noexcept {
        if (this != &other) {
            if (fb_) {
                esp_camera_fb_return(fb_);
            }
            fb_ = other.fb_;
            other.fb_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] const uint8_t* data() const { return fb_ ? fb_->buf : nullptr; }
    [[nodiscard]] size_t size() const { return fb_ ? fb_->len : 0; }
    [[nodiscard]] pixformat_t format() const { return fb_ ? fb_->format : PIXFORMAT_JPEG; }
    [[nodiscard]] camera_fb_t* get() const { return fb_; }

private:
    camera_fb_t* fb_{nullptr};
};

class CameraDriver {
public:
    CameraDriver() = default;
    ~CameraDriver() {
        if (initialized_) {
            esp_camera_deinit();
            ESP_LOGI(TAG, "Драйвер камери деініціалізовано");
        }
    }

    bool init() {
        if (initialized_) {
            return true;
        }

        // Перевіряємо наявність Octal PSRAM для розташування буферів
        if (!heap_caps_get_total_size(MALLOC_CAP_SPIRAM)) {
            ESP_LOGE(TAG, "Octal PSRAM не виявлено! Для подвійної буферизації потрібна PSRAM");
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
        config.pixel_format = PIXFORMAT_JPEG;
        config.frame_size = FRAMESIZE_VGA;
        config.jpeg_quality = 12;
        config.fb_count = 2; // Подвійна буферизація в Octal PSRAM
        config.fb_location = CAMERA_FB_IN_PSRAM;
        config.grab_mode = CAMERA_GRAB_LATEST;

        esp_err_t err = esp_camera_init(&config);
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x", err);
            return false;
        }

        sensor_t* s = esp_camera_sensor_get();
        if (s) {
            s->set_vflip(s, 1);
            s->set_hmirror(s, 1);
        }

        initialized_ = true;
        ESP_LOGI(TAG, "Камеру успішно ініціалізовано (роздільна здатність VGA, буфери в PSRAM)");
        return true;
    }

    std::unique_ptr<CameraFrame> capture() {
        if (!initialized_) {
            ESP_LOGE(TAG, "Спроба захоплення кадру з неініціалізованої камери");
            return nullptr;
        }

        camera_fb_t* fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGW(TAG, "Не вдалося отримати кадр із камери");
            return nullptr;
        }

        return std::make_unique<CameraFrame>(fb);
    }

private:
    static constexpr const char* TAG = "CameraDriver";
    bool initialized_{false};
};

} // namespace esp32s3

#endif // CAMERA_DRIVER_HPP
