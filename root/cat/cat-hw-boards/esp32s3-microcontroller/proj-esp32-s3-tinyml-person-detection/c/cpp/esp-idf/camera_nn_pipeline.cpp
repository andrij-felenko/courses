#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <span>
#include <vector>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_system.h"
#include "esp_log.h"
#include "esp_heap_caps.h"
#include "esp_camera.h"
#include "esp_nn.h"

static const char *TAG = "CPP_CAMERA_NN";

// RAII обгортка для автоматичного повернення кадрового буфера камери
class FrameBufferGuard {
public:
    explicit FrameBufferGuard(camera_fb_t *fb) : fb_(fb) {}

    ~FrameBufferGuard() {
        if (fb_) {
            esp_camera_fb_return(fb_);
        }
    }

    // Видаляємо копіювання для запобігання подвійному звільненню
    FrameBufferGuard(const FrameBufferGuard &) = delete;
    FrameBufferGuard &operator=(const FrameBufferGuard &) = delete;

    // Дозволяємо переміщення
    FrameBufferGuard(FrameBufferGuard &&other) noexcept : fb_(other.fb_) {
        other.fb_ = nullptr;
    }

    FrameBufferGuard &operator=(FrameBufferGuard &&other) noexcept {
        if (this != &other) {
            if (fb_) {
                esp_camera_fb_return(fb_);
            }
            fb_ = other.fb_;
            other.fb_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] camera_fb_t *get() const noexcept { return fb_; }
    [[nodiscard]] bool valid() const noexcept { return fb_ != nullptr; }

private:
    camera_fb_t *fb_{nullptr};
};

// RAII алокатор вирівняного буфера в PSRAM
template <typename T>
class PsramBuffer {
public:
    explicit PsramBuffer(size_t count) : count_(count) {
        size_t bytes = count * sizeof(T);
        ptr_ = static_cast<T *>(heap_caps_malloc(bytes, MALLOC_CAP_SPIRAM | MALLOC_CAP_32BIT));
        if (ptr_) {
            std::memset(ptr_, 0, bytes);
        }
    }

    ~PsramBuffer() {
        if (ptr_) {
            heap_caps_free(ptr_);
        }
    }

    PsramBuffer(const PsramBuffer &) = delete;
    PsramBuffer &operator=(const PsramBuffer &) = delete;

    PsramBuffer(PsramBuffer &&other) noexcept : ptr_(other.ptr_), count_(other.count_) {
        other.ptr_ = nullptr;
        other.count_ = 0;
    }

    PsramBuffer &operator=(PsramBuffer &&other) noexcept {
        if (this != &other) {
            if (ptr_) heap_caps_free(ptr_);
            ptr_ = other.ptr_;
            count_ = other.count_;
            other.ptr_ = nullptr;
            other.count_ = 0;
        }
        return *this;
    }

    [[nodiscard]] T *data() noexcept { return ptr_; }
    [[nodiscard]] const T *data() const noexcept { return ptr_; }
    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] bool valid() const noexcept { return ptr_ != nullptr; }
    [[nodiscard]] std::span<T> as_span() noexcept { return std::span<T>(ptr_, count_); }

private:
    T *ptr_{nullptr};
    size_t count_{0};
};

// Клас управління конвеєром захоплення та векторизованої обробки
class CameraPipeline {
public:
    static constexpr size_t kInputDim = 32;
    static constexpr size_t kInChannels = 3;
    static constexpr size_t kOutChannels = 16;
    static constexpr size_t kQueueLen = 2;

    struct Packet {
        camera_fb_t *fb{nullptr};
        int frame_id{0};
    };

    CameraPipeline() = default;

    ~CameraPipeline() {
        if (queue_) {
            vQueueDelete(queue_);
        }
    }

    esp_err_t init() {
        queue_ = xQueueCreate(kQueueLen, sizeof(Packet));
        if (!queue_) {
            ESP_LOGE(TAG, "Помилка створення черги FreeRTOS");
            return ESP_ERR_NO_MEM;
        }

        camera_config_t config = {};
        config.pin_pwdn = -1;
        config.pin_reset = -1;
        config.pin_xclk = 10;
        config.pin_siod = 40;
        config.pin_sioc = 39;
        config.pin_d7 = 48;
        config.pin_d6 = 11;
        config.pin_d5 = 12;
        config.pin_d4 = 14;
        config.pin_d3 = 16;
        config.pin_d2 = 18;
        config.pin_d1 = 17;
        config.pin_d0 = 15;
        config.pin_vsync = 38;
        config.pin_href = 47;
        config.pin_pclk = 13;

        config.xclk_freq_hz = 20000000;
        config.ledc_timer = LEDC_TIMER_0;
        config.ledc_channel = LEDC_CHANNEL_0;
        config.pixel_format = PIXFORMAT_RGB565;
        config.frame_size = FRAMESIZE_QVGA;
        config.jpeg_quality = 12;
        config.fb_count = 2;
        config.fb_location = CAMERA_FB_IN_PSRAM;
        config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;

        esp_err_t err = esp_camera_init(&config);
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "Ініціалізація esp32-camera завершилась з помилкою 0x%x", err);
            return err;
        }
        ESP_LOGI(TAG, "C++ CameraPipeline успішно ініціалізовано");
        return ESP_OK;
    }

    void start_tasks() {
        xTaskCreatePinnedToCore(&CameraPipeline::capture_task_entry, "cpp_cam_task", 4096, this, 5, nullptr, 0);
        xTaskCreatePinnedToCore(&CameraPipeline::infer_task_entry, "cpp_nn_task", 8192, this, 5, nullptr, 1);
    }

private:
    static void capture_task_entry(void *arg) {
        static_cast<CameraPipeline *>(arg)->run_capture();
    }

    static void infer_task_entry(void *arg) {
        static_cast<CameraPipeline *>(arg)->run_inference();
    }

    void run_capture() {
        int frame_counter = 0;
        ESP_LOGI(TAG, "Запущено C++ задачу захоплення на ядрі %d", xPortGetCoreID());

        while (true) {
            camera_fb_t *raw_fb = esp_camera_fb_get();
            if (!raw_fb) {
                vTaskDelay(pdMS_TO_TICKS(10));
                continue;
            }

            Packet pkt{.fb = raw_fb, .frame_id = ++frame_counter};
            if (xQueueSend(queue_, &pkt, pdMS_TO_TICKS(50)) != pdTRUE) {
                ESP_LOGW(TAG, "C++ черга переповнена, вертаємо кадр #%d", pkt.frame_id);
                esp_camera_fb_return(raw_fb);
            }
            vTaskDelay(pdMS_TO_TICKS(30));
        }
    }

    void run_inference() {
        ESP_LOGI(TAG, "Запущено C++ задачу ESP-NN векторизації на ядрі %d", xPortGetCoreID());

        size_t in_size = kInputDim * kInputDim * kInChannels;
        size_t out_size = kInputDim * kInputDim * kOutChannels;
        size_t filter_size = kInChannels * kOutChannels * 3 * 3;

        PsramBuffer<int8_t> in_buf(in_size);
        PsramBuffer<int8_t> out_buf(out_size);
        PsramBuffer<int8_t> weights(filter_size);
        PsramBuffer<int32_t> bias(kOutChannels);

        if (!in_buf.valid() || !out_buf.valid() || !weights.valid() || !bias.valid()) {
            ESP_LOGE(TAG, "Критична помилка: не вдалося виділити C++ RAII буфери в PSRAM");
            vTaskDelete(nullptr);
            return;
        }

        std::fill(weights.as_span().begin(), weights.as_span().end(), static_cast<int8_t>(1));

        esp_nn_conv_s8_data_t conv_params = {
            .in_x = static_cast<uint16_t>(kInputDim),
            .in_y = static_cast<uint16_t>(kInputDim),
            .in_ch = static_cast<uint16_t>(kInChannels),
            .out_ch = static_cast<uint16_t>(kOutChannels),
            .filter_x = 3,
            .filter_y = 3,
            .stride_x = 1,
            .stride_y = 1,
            .pad_x = 1,
            .pad_y = 1,
            .activation_min = -128,
            .activation_max = 127,
        };

        Packet pkt;
        while (true) {
            if (xQueueReceive(queue_, &pkt, portMAX_DELAY) == pdTRUE) {
                FrameBufferGuard guard(pkt.fb);

                if (guard.valid()) {
                    auto in_span = in_buf.as_span();
                    size_t copy_len = (guard.get()->len < in_span.size()) ? guard.get()->len : in_span.size();

                    for (size_t i = 0; i < copy_len; ++i) {
                        in_span[i] = static_cast<int8_t>(static_cast<int>(guard.get()->buf[i]) - 128);
                    }

                    esp_nn_conv_s8(&conv_params, in_buf.data(), out_buf.data(), weights.data(), bias.data());

                    ESP_LOGI(TAG, "C++ ESP-NN PIE обробив кадр #%d (байтів: %zu)",
                             pkt.frame_id, guard.get()->len);
                }
                // FrameBufferGuard автоматично викликає esp_camera_fb_return(pkt.fb) при виході з блоку
            }
        }
    }

    QueueHandle_t queue_{nullptr};
};

extern "C" void app_main(void)
{
    ESP_LOGI(TAG, "Запуск C++ ESP32-S3 Camera & ESP-NN Pipeline");

    static CameraPipeline pipeline;
    if (pipeline.init() == ESP_OK) {
        pipeline.start_tasks();
    }
}
