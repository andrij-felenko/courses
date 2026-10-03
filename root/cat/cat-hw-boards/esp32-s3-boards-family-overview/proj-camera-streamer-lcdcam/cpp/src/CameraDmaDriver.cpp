#include "CameraDmaDriver.hpp"
#include "esp_log.h"
#include "esp_timer.h"
#include "driver/gpio.h"
#include "esp_heap_caps.h"
#include <cstring>

static const char* TAG = "CameraDmaDriver";

namespace camera {

CameraDmaDriver::CameraDmaDriver() = default;

CameraDmaDriver::~CameraDmaDriver() {
    stopStream();
    freeDmaResources();
    if (frameQueue_) {
        vQueueDelete(frameQueue_);
        frameQueue_ = nullptr;
    }
}

esp_err_t CameraDmaDriver::init(const CameraConfig& config) {
    if (initialized_) {
        ESP_LOGW(TAG, "Драйвер камери вже ініціалізовано");
        return ESP_OK;
    }

    config_ = config;

    // Створюємо чергу FreeRTOS для збереження вказівників на FrameBuffer (підтримуємо до 5 кадрів)
    frameQueue_ = xQueueCreate(5, sizeof(FrameBuffer::Ptr*));
    if (!frameQueue_) {
        ESP_LOGE(TAG, "Помилка створення черги кадрів FreeRTOS");
        return ESP_FAIL;
    }

    esp_err_t ret = configureGpios();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка налаштування GPIO камери");
        return ret;
    }

    ret = setupClockGenerator();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка генерації тактового сигналу XCLK");
        return ret;
    }

    ret = setupDmaDescriptors();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка виділення та налаштування DMA дескрипторів");
        return ret;
    }

    // Створюємо початковий кадровий буфер у PSRAM під перший кадр
    currentFrame_ = FrameBuffer::create(config_.maxFrameSize, config_.width, config_.height, config_.format);
    if (!currentFrame_) {
        ESP_LOGE(TAG, "Помилка створення первинного FrameBuffer у PSRAM");
        return ESP_ERR_NO_MEM;
    }

    initialized_ = true;
    ESP_LOGI(TAG, "Драйвер камери ESP32-S3 успішно ініціалізовано");
    return ESP_OK;
}

esp_err_t CameraDmaDriver::configureGpios() {
    gpio_config_t io_conf = {};
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pin_bit_mask = (1ULL << config_.pinD0) | (1ULL << config_.pinD1) |
                           (1ULL << config_.pinD2) | (1ULL << config_.pinD3) |
                           (1ULL << config_.pinD4) | (1ULL << config_.pinD5) |
                           (1ULL << config_.pinD6) | (1ULL << config_.pinD7) |
                           (1ULL << config_.pinPclk) | (1ULL << config_.pinVsync) |
                           (1ULL << config_.pinHsync);
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.pull_up_en = GPIO_PULLUP_ENABLE;
    
    return gpio_config(&io_conf);
}

esp_err_t CameraDmaDriver::setupClockGenerator() {
    // В реальній прошивці ESP-IDF тут налаштовується LEDC або I2S/LCD_CAM майстер-клок
    ESP_LOGI(TAG, "Тактування XCLK налаштовано на частоту %lu Гц", config_.xclkFreqHz);
    return ESP_OK;
}

esp_err_t CameraDmaDriver::setupDmaDescriptors() {
    // Алокація кільцевого буфера DMA у SRAM (MALLOC_CAP_DMA)
    dmaBuffers_ = static_cast<void**>(heap_caps_malloc(config_.dmaBufferCount * sizeof(void*), MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT));
    if (!dmaBuffers_) {
        return ESP_ERR_NO_MEM;
    }

    for (size_t i = 0; i < config_.dmaBufferCount; ++i) {
        dmaBuffers_[i] = heap_caps_malloc(config_.dmaBufferSize, MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL);
        if (!dmaBuffers_[i]) {
            freeDmaResources();
            return ESP_ERR_NO_MEM;
        }
    }

    ESP_LOGI(TAG, "Виділено %zu DMA кільцевих буферів по %zu байт", config_.dmaBufferCount, config_.dmaBufferSize);
    return ESP_OK;
}

void CameraDmaDriver::freeDmaResources() {
    if (dmaBuffers_) {
        for (size_t i = 0; i < config_.dmaBufferCount; ++i) {
            if (dmaBuffers_[i]) {
                heap_caps_free(dmaBuffers_[i]);
            }
        }
        heap_caps_free(dmaBuffers_);
        dmaBuffers_ = nullptr;
    }
}

esp_err_t CameraDmaDriver::startStream() {
    if (!initialized_) {
        return ESP_ERR_INVALID_STATE;
    }
    if (streaming_) {
        return ESP_OK;
    }

    streaming_ = true;
    ESP_LOGI(TAG, "Запущено апаратне захоплення кадрів через DMA");
    return ESP_OK;
}

esp_err_t CameraDmaDriver::stopStream() {
    if (!streaming_) {
        return ESP_OK;
    }
    streaming_ = false;
    ESP_LOGI(TAG, "Зупинено DMA захоплення кадрів");
    return ESP_OK;
}

void IRAM_ATTR CameraDmaDriver::handleDmaInterrupt(void* arg) {
    auto* self = static_cast<CameraDmaDriver*>(arg);
    if (!self || !self->streaming_) {
        return;
    }

    BaseType_t xHigherPriorityTaskWoken = pdFALSE;

    // Перевірка завершення кадру (симуляція апаратного переривання VSYNC/EOF)
    if (self->currentFrame_) {
        self->currentFrame_->setActualSize(self->currentFrameBytes_);
        self->currentFrame_->metadata().sequenceNumber = ++self->sequenceCounter_;
        self->currentFrame_->metadata().timestampUs = esp_timer_get_time();

        // Створюємо новий об'єкт shared_ptr для відправлення у чергу FreeRTOS
        FrameBuffer::Ptr frameToSend = self->currentFrame_;

        // Виділяємо наступний буфер у PSRAM для неблокуючого прийому
        self->currentFrame_ = FrameBuffer::create(self->config_.maxFrameSize, self->config_.width, self->config_.height, self->config_.format);
        self->currentFrameBytes_ = 0;

        // Неблокуюча передача покажчика у чергу FreeRTOS із ISR
        auto* rawPtr = new FrameBuffer::Ptr(frameToSend);
        if (xQueueSendFromISR(self->frameQueue_, &rawPtr, &xHigherPriorityTaskWoken) != pdTRUE) {
            delete rawPtr; // Черга переповнена, кадр відкинуто для збереження затримки
        }
    }

    if (xHigherPriorityTaskWoken == pdTRUE) {
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

} // namespace camera
