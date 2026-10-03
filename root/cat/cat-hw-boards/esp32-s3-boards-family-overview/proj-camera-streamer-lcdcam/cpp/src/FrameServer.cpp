#include "FrameServer.hpp"
#include "esp_log.h"
#include <algorithm>

static const char* TAG = "FrameServer";

namespace camera {

FrameServer::FrameServer(size_t maxSubscribers)
    : maxSubscribers_(maxSubscribers) {
    mutex_ = xSemaphoreCreateMutex();
}

FrameServer::~FrameServer() {
    stop();
    if (mutex_) {
        vSemaphoreDelete(mutex_);
        mutex_ = nullptr;
    }
}

esp_err_t FrameServer::start(CameraDmaDriver& driver, UBaseType_t taskPriority, uint32_t stackSize) {
    if (running_) {
        ESP_LOGW(TAG, "Кадровий сервер вже запущено");
        return ESP_OK;
    }

    driver_ = &driver;
    running_ = true;

    BaseType_t ret = xTaskCreatePinnedToCore(
        taskEntry,
        "FrameServerTask",
        stackSize,
        this,
        taskPriority,
        &taskHandle_,
        1 // Прив'язуємо задачу до ядра 1 ESP32-S3
    );

    if (ret != pdPASS) {
        running_ = false;
        ESP_LOGE(TAG, "Не вдалося створити задачу FrameServer");
        return ESP_FAIL;
    }

    ESP_LOGI(TAG, "Кадровий сервер успішно запущено на ядрі 1 з пріоритетом %u", taskPriority);
    return ESP_OK;
}

esp_err_t FrameServer::stop() {
    if (!running_) {
        return ESP_OK;
    }

    running_ = false;
    if (taskHandle_) {
        // Очікуємо завершення задачи
        vTaskDelay(pdMS_TO_TICKS(100));
        taskHandle_ = nullptr;
    }

    xSemaphoreTake(mutex_, portMAX_DELAY);
    for (auto subQueue : subscribers_) {
        vQueueDelete(subQueue);
    }
    subscribers_.clear();
    xSemaphoreGive(mutex_);

    ESP_LOGI(TAG, "Кадровий сервер зупинено");
    return ESP_OK;
}

QueueHandle_t FrameServer::registerSubscriber(size_t queueDepth) {
    xSemaphoreTake(mutex_, portMAX_DELAY);

    if (subscribers_.size() >= maxSubscribers_) {
        xSemaphoreGive(mutex_);
        ESP_LOGE(TAG, "Досягнуто ліміт підписників (%zu)", maxSubscribers_);
        return nullptr;
    }

    QueueHandle_t subQueue = xQueueCreate(queueDepth, sizeof(FrameBuffer::Ptr*));
    if (subQueue) {
        subscribers_.push_back(subQueue);
        ESP_LOGI(TAG, "Зареєстровано нового підписника. Всього підписників: %zu", subscribers_.size());
    } else {
        ESP_LOGE(TAG, "Не вдалося створити чергу підписника");
    }

    xSemaphoreGive(mutex_);
    return subQueue;
}

esp_err_t FrameServer::unregisterSubscriber(QueueHandle_t queue) {
    if (!queue) return ESP_ERR_INVALID_ARG;

    xSemaphoreTake(mutex_, portMAX_DELAY);
    auto it = std::find(subscribers_.begin(), subscribers_.end(), queue);
    if (it != subscribers_.end()) {
        subscribers_.erase(it);
        vQueueDelete(queue);
        ESP_LOGI(TAG, "Підписника видалено. Залишилось: %zu", subscribers_.size());
        xSemaphoreGive(mutex_);
        return ESP_OK;
    }

    xSemaphoreGive(mutex_);
    return ESP_ERR_NOT_FOUND;
}

size_t FrameServer::subscriberCount() {
    xSemaphoreTake(mutex_, portMAX_DELAY);
    size_t count = subscribers_.size();
    xSemaphoreGive(mutex_);
    return count;
}

void FrameServer::taskEntry(void* arg) {
    auto* self = static_cast<FrameServer*>(arg);
    self->taskLoop();
    vTaskDelete(nullptr);
}

void FrameServer::taskLoop() {
    FrameBuffer::Ptr* framePtrContainer = nullptr;

    while (running_) {
        if (!driver_ || !driver_->frameQueue()) {
            vTaskDelay(pdMS_TO_TICKS(10));
            continue;
        }

        // Очікуємо новий кадр з DMA-драйвера
        if (xQueueReceive(driver_->frameQueue(), &framePtrContainer, pdMS_TO_TICKS(100)) == pdTRUE) {
            if (framePtrContainer && *framePtrContainer) {
                FrameBuffer::Ptr frame = *framePtrContainer;
                delete framePtrContainer; // Звільняємо контейнер покажчика

                // Розсилаємо отриманий кадр усім активним споживачам
                dispatchFrame(frame);
            }
        }
    }
}

void FrameServer::dispatchFrame(const FrameBuffer::Ptr& frame) {
    xSemaphoreTake(mutex_, portMAX_DELAY);

    for (auto subQueue : subscribers_) {
        // Створюємо копію shared_ptr (збільшується лічильник посилань без копіювання самого PSRAM буфера)
        auto* rawContainer = new FrameBuffer::Ptr(frame);

        // Передаємо без блокування (timeout = 0): якщо черга підписника переповнена, кадр скидається
        if (xQueueSend(subQueue, &rawContainer, 0) != pdTRUE) {
            delete rawContainer;
        }
    }

    xSemaphoreGive(mutex_);
}

} // namespace camera
