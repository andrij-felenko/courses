#ifndef CAMERA_DMA_DRIVER_HPP
#define CAMERA_DMA_DRIVER_HPP

#include <cstdint>
#include <cstddef>
#include "esp_err.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "FrameBuffer.hpp"

namespace camera {

/**
 * @brief Конфігурація GPIO та параметрів відеопериферії ESP32-S3 (LCD_CAM/DVP).
 */
struct CameraConfig {
    int pinD0{4};
    int pinD1{5};
    int pinD2{6};
    int pinD3{7};
    int pinD4{15};
    int pinD5{16};
    int pinD6{17};
    int pinD7{18};
    int pinXclk{10};
    int pinPclk{12};
    int pinVsync{11};
    int pinHsync{13};
    int pinSda{1};
    int pinScl{2};
    int pinReset{-1};

    uint32_t xclkFreqHz{20000000}; //!< Частота тактування XCLK (20 МГц)
    uint32_t width{640};
    uint32_t height{480};
    PixelFormat format{PixelFormat::JPEG};
    size_t dmaBufferCount{4};      //!< Кількість кільцевих буферів DMA
    size_t dmaBufferSize{32768};   //!< Розмір одного DMA буфера в байтах
    size_t maxFrameSize{128000};   //!< Максимальний очікуваний розмір кадру
};

/**
 * @brief Драйвер апаратної відеопериферії ESP32-S3 з DMA.
 * 
 * Конфігурує шину DVP/LCD_CAM, дескриптори DMA та здійснює неблокуючу
 * обробку переривань прийому кадрів з передачею готових об'єктів у чергу FreeRTOS.
 */
class CameraDmaDriver {
public:
    CameraDmaDriver();
    ~CameraDmaDriver();

    // Некопійований об'єкт
    CameraDmaDriver(const CameraDmaDriver&) = delete;
    CameraDmaDriver& operator=(const CameraDmaDriver&) = delete;

    /**
     * @brief Ініціалізація периферії та апаратного DMA-контролера.
     */
    esp_err_t init(const CameraConfig& config);

    /**
     * @brief Запуск відеопотоку та активізація DMA-переривань.
     */
    esp_err_t startStream();

    /**
     * @brief Зупинка відеопотоку.
     */
    esp_err_t stopStream();

    /// @brief Черга FreeRTOS для передачі захоплених кадрів
    QueueHandle_t frameQueue() const { return frameQueue_; }

    /// @brief Прапор стану активного стримінгу
    bool isStreaming() const { return streaming_; }

    /// @brief Отримання поточної конфігурації
    const CameraConfig& config() const { return config_; }

private:
    esp_err_t configureGpios();
    esp_err_t setupClockGenerator();
    esp_err_t setupDmaDescriptors();
    void freeDmaResources();

    /// @brief Апаратний ISR обробник переривань DMA LCD_CAM
    static void IRAM_ATTR handleDmaInterrupt(void* arg);

    CameraConfig config_{};
    QueueHandle_t frameQueue_{nullptr};
    bool initialized_{false};
    bool streaming_{false};
    uint32_t sequenceCounter_{0};

    // Буфери DMA та дескриптори
    void** dmaBuffers_{nullptr};
    void* dmaDescriptors_{nullptr};
    FrameBuffer::Ptr currentFrame_{nullptr};
    size_t currentFrameBytes_{0};
};

} // namespace camera

#endif // CAMERA_DMA_DRIVER_HPP
