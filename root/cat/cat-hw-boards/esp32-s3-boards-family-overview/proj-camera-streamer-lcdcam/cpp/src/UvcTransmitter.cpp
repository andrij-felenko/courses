#include "UvcTransmitter.hpp"
#include "esp_log.h"
#include "esp_timer.h"
#include <cstring>

static const char* TAG = "UvcTransmitter";

namespace camera {

// Структура 2-байтового стандартного заголовка кадру UVC (USB Video Class)
struct UvcHeader {
    uint8_t length;
    uint8_t flags;
};

enum UvcHeaderFlags : uint8_t {
    UVC_HEADER_FID = (1 << 0), //!< Frame ID bit
    UVC_HEADER_EOF = (1 << 1), //!< End of Frame bit
    UVC_HEADER_PTS = (1 << 2), //!< Presentation Timestamp present
    UVC_HEADER_SCR = (1 << 3), //!< Source Clock Reference present
    UVC_HEADER_ERR = (1 << 5), //!< Error bit
    UVC_HEADER_EOI = (1 << 7)  //!< End of Image bit
};

UvcTransmitter::UvcTransmitter() = default;

UvcTransmitter::~UvcTransmitter() {
    stop();
}

esp_err_t UvcTransmitter::init() {
    ESP_LOGI(TAG, "Ініціалізація USB OTG контролера у режимі UVC (USB Video Class)");
    // Апаратна налаштування TinyUSB / USB PHY контролера ESP32-S3
    connected_ = true; // Умовна індикація підключення хоста
    return ESP_OK;
}

esp_err_t UvcTransmitter::start(FrameServer& server, UBaseType_t priority, uint32_t stackSize) {
    if (running_) return ESP_OK;

    server_ = &server;
    frameQueue_ = server_->registerSubscriber(3);
    if (!frameQueue_) {
        ESP_LOGE(TAG, "Не вдалося зареєструвати підписника в FrameServer для UVC");
        return ESP_FAIL;
    }

    running_ = true;

    BaseType_t ret = xTaskCreatePinnedToCore(
        uvcTask,
        "UvcStreamTask",
        stackSize,
        this,
        priority,
        &taskHandle_,
        1 // Рекомендовано виконувати на ядрі 1 поруч із DMA
    );

    if (ret != pdPASS) {
        running_ = false;
        server_->unregisterSubscriber(frameQueue_);
        frameQueue_ = nullptr;
        ESP_LOGE(TAG, "Не вдалося створити задачу UvcTransmitter");
        return ESP_FAIL;
    }

    ESP_LOGI(TAG, "UVC передавач відеокадрів успішно запущено");
    return ESP_OK;
}

esp_err_t UvcTransmitter::stop() {
    if (!running_) return ESP_OK;

    running_ = false;
    if (server_ && frameQueue_) {
        server_->unregisterSubscriber(frameQueue_);
        frameQueue_ = nullptr;
    }

    if (taskHandle_) {
        vTaskDelay(pdMS_TO_TICKS(100));
        taskHandle_ = nullptr;
    }

    ESP_LOGI(TAG, "UVC передавач зупинено");
    return ESP_OK;
}

void UvcTransmitter::uvcTask(void* arg) {
    auto* self = static_cast<UvcTransmitter*>(arg);
    self->processFrameStream();
    vTaskDelete(nullptr);
}

void UvcTransmitter::processFrameStream() {
    FrameBuffer::Ptr* framePtrContainer = nullptr;

    while (running_) {
        if (xQueueReceive(frameQueue_, &framePtrContainer, pdMS_TO_TICKS(50)) == pdTRUE) {
            if (framePtrContainer && *framePtrContainer) {
                FrameBuffer::Ptr frame = *framePtrContainer;
                delete framePtrContainer;

                if (connected_) {
                    sendUvcPayload(frame);
                }
            }
        }
    }
}

void UvcTransmitter::sendUvcPayload(const FrameBuffer::Ptr& frame) {
    if (!frame || frame->actualSize() == 0) return;

    // Перемикання біта FID (Frame ID) при отриманні нового кадру
    headerToggle_ ^= UVC_HEADER_FID;

    const size_t maxPacketLen = 1024; // Максимальний розмір пакету USB Endpoint
    uint8_t packetBuf[maxPacketLen];

    const uint8_t* rawData = frame->data();
    size_t bytesRemaining = frame->actualSize();
    size_t offset = 0;

    while (bytesRemaining > 0 && running_) {
        size_t payloadSize = (bytesRemaining > maxPacketLen - 2) ? (maxPacketLen - 2) : bytesRemaining;

        // Формування заголовка UVC
        UvcHeader header = {};
        header.length = 2;
        header.flags = headerToggle_;

        if (offset + payloadSize >= frame->actualSize()) {
            header.flags |= UVC_HEADER_EOF; // Позначка кінця кадру
        }

        packetBuf[0] = header.length;
        packetBuf[1] = header.flags;
        std::memcpy(&packetBuf[2], rawData + offset, payloadSize);

        // Симуляція відправки ізохронного пакета через USB Endpoint ESP32-S3
        // tinyusb_cdcacm_write_queue(packetBuf, payloadSize + 2);

        offset += payloadSize;
        bytesRemaining -= payloadSize;
    }
}

} // namespace camera
