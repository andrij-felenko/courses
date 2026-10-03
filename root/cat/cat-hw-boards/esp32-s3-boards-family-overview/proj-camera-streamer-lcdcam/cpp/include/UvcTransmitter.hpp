#ifndef UVC_TRANSMITTER_HPP
#define UVC_TRANSMITTER_HPP

#include <atomic>
#include "esp_err.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "FrameServer.hpp"

namespace camera {

/**
 * @brief Контролер USB Video Class (UVC) для ESP32-S3.
 * 
 * Пакує кадри в пакети стандарту UVC та надсилає їх через ізохронний/bulk
 * USB-ендпоінт апаратного контролера USB OTG.
 */
class UvcTransmitter {
public:
    UvcTransmitter();
    ~UvcTransmitter();

    // Некопійований об'єкт
    UvcTransmitter(const UvcTransmitter&) = delete;
    UvcTransmitter& operator=(const UvcTransmitter&) = delete;

    /**
     * @brief Ініціалізація USB OTG контролера та стака UVC.
     */
    esp_err_t init();

    /**
     * @brief Запуск задачи UVC-передавача.
     */
    esp_err_t start(FrameServer& server, UBaseType_t priority = 5, uint32_t stackSize = 4096);

    /**
     * @brief Зупинка UVC передавача.
     */
    esp_err_t stop();

    /// @brief Прапор підключення хоста USB (PC)
    bool isConnected() const { return connected_.load(); }

    /// @brief Прапор активного передавача
    bool isRunning() const { return running_.load(); }

private:
    static void uvcTask(void* arg);
    void processFrameStream();
    void sendUvcPayload(const FrameBuffer::Ptr& frame);

    FrameServer* server_{nullptr};
    QueueHandle_t frameQueue_{nullptr};
    TaskHandle_t taskHandle_{nullptr};
    std::atomic<bool> running_{false};
    std::atomic<bool> connected_{false};
    uint8_t headerToggle_{0};
};

} // namespace camera

#endif // UVC_TRANSMITTER_HPP
