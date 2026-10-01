#pragma once

#include <cstdint>
#include <cstddef>
#include <utility>
#include "esp_err.h"
#include "esp_log.h"
#include "esp_heap_caps.h"
#include "driver/spi_master.h"

namespace graphics {

/**
 * @brief RAII-обгортка подвійного кадрового буфера у зовнішній пам'яті PSRAM
 * з підтримкою асинхронної передачі через SPI DMA для ESP32-S3.
 */
class PsramFrameBuffer {
public:
    /**
     * @brief Конструктор: виділяє пам'ять під два кадрові буфери в PSRAM.
     * @param width Ширина кадру в пікселях.
     * @param height Висота кадру в пікселях.
     * @param bytes_per_pixel Кількість байтів на піксель (за замовчуванням 2 для RGB565).
     */
    PsramFrameBuffer(uint16_t width, uint16_t height, uint8_t bytes_per_pixel = 2);

    /// Деструктор: автоматично звільняє виділену в PSRAM пам'ять
    ~PsramFrameBuffer();

    // Забороняємо копіювання для збереження концепції RAII
    PsramFrameBuffer(const PsramFrameBuffer&) = delete;
    PsramFrameBuffer& operator=(const PsramFrameBuffer&) = delete;

    // Дозволяємо переміщення (move-семантика)
    PsramFrameBuffer(PsramFrameBuffer&& other) noexcept;
    PsramFrameBuffer& operator=(PsramFrameBuffer&& other) noexcept;

    /**
     * @brief Перемикає активні буфери (Ping-Pong buffering).
     * Буфер малювання стає готовим до відправки, а попередній відправлений — для нового кадру.
     */
    void swap_buffers() noexcept;

    /// Повертає вказівник на активний буфер малювання (back buffer)
    [[nodiscard]] uint16_t* get_draw_buffer() noexcept { return draw_buffer_; }

    /// Повертає константний вказівник на готовий буфер виведення (front buffer)
    [[nodiscard]] const uint16_t* get_front_buffer() const noexcept { return display_buffer_; }

    /// Повертає загальний розмір одного кадрового буфера у байтах
    [[nodiscard]] size_t get_buffer_size() const noexcept { return buffer_size_; }

    /**
     * @brief Запускає асинхронну передачу готового кадру по шині SPI DMA.
     * @param spi Хендл ініціалізованого пристрою SPI.
     * @return ESP_OK у разі успішного запуску транзакції.
     */
    esp_err_t flush_async(spi_device_handle_t spi);

    /**
     * @brief Очікує завершення попередньої асинхронної передачі по DMA.
     * @param spi Хендл пристрою SPI.
     */
    esp_err_t wait_until_idle(spi_device_handle_t spi);

private:
    uint16_t width_{0};
    uint16_t height_{0};
    uint8_t bytes_per_pixel_{2};
    size_t buffer_size_{0};

    uint16_t* buffer_a_{nullptr};
    uint16_t* buffer_b_{nullptr};

    uint16_t* draw_buffer_{nullptr};     ///< Активний буфер малювання
    uint16_t* display_buffer_{nullptr};  ///< Активний буфер виведення на DMA

    spi_transaction_t trans_{};
    bool trans_in_flight_{false};
};

} // namespace graphics
