#ifndef FRAME_SERVER_HPP
#define FRAME_SERVER_HPP

#include <vector>
#include <atomic>
#include "esp_err.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "CameraDmaDriver.hpp"
#include "FrameBuffer.hpp"

namespace camera {

/**
 * @brief Центральний координатор кадрового сервера.
 * 
 * Вичитує кадри з черги DMA драйвера, керує їх життєвим циклом та безпечно
 * розподіляє покажчики між активними споживачами (MJPEG, UVC) у FreeRTOS.
 */
class FrameServer {
public:
    explicit FrameServer(size_t maxSubscribers = 8);
    ~FrameServer();

    // Некопійований об'єкт
    FrameServer(const FrameServer&) = delete;
    FrameServer& operator=(const FrameServer&) = delete;

    /**
     * @brief Запуск фонової задачи диспетчеризації кадрів FreeRTOS.
     */
    esp_err_t start(CameraDmaDriver& driver, UBaseType_t taskPriority = 5, uint32_t stackSize = 4096);

    /**
     * @brief Зупинка сервера та звільнення ресурсів.
     */
    esp_err_t stop();

    /**
     * @brief Реєстрація нового споживача відеопотоку.
     * @param queueDepth Глибина черги для даного споживача
     * @return QueueHandle_t Хендл створити черги або nullptr
     */
    QueueHandle_t registerSubscriber(size_t queueDepth = 3);

    /**
     * @brief Скасування реєстрації споживача та видалення його черги.
     */
    esp_err_t unregisterSubscriber(QueueHandle_t queue);

    /// @brief Перевірка статусу виконання
    bool isRunning() const { return running_; }

    /// @brief Кількість активних підписників
    size_t subscriberCount();

private:
    static void taskEntry(void* arg);
    void taskLoop();
    void dispatchFrame(const FrameBuffer::Ptr& frame);

    CameraDmaDriver* driver_{nullptr};
    TaskHandle_t taskHandle_{nullptr};
    SemaphoreHandle_t mutex_{nullptr};
    std::vector<QueueHandle_t> subscribers_;
    size_t maxSubscribers_;
    std::atomic<bool> running_{false};
};

} // namespace camera

#endif // FRAME_SERVER_HPP
