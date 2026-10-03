#ifndef FRAME_BUFFER_HPP
#define FRAME_BUFFER_HPP

#include <cstdint>
#include <cstddef>
#include <atomic>
#include <memory>
#include "esp_heap_caps.h"
#include "esp_err.h"

namespace camera {

/**
 * @brief Перелік підтримуваних форматів пікселів відеокадру.
 */
enum class PixelFormat {
    RGB565,
    YUV422,
    GRAYSCALE,
    JPEG
};

/**
 * @brief Структура метаданих кадру.
 */
struct FrameMetadata {
    uint32_t sequenceNumber{0}; //!< Послідовний номер кадру з моменту запуску
    int64_t timestampUs{0};     //!< Часова мітка захоплення кадру (мікросекунди)
    uint32_t width{0};          //!< Ширина кадру у пікселях
    uint32_t height{0};         //!< Висота кадру у пікселях
    size_t dataSize{0};         //!< Актуальний розмір корисних даних кадру (байти)
    PixelFormat format{PixelFormat::JPEG}; //!< Формат даних пікселів
};

/**
 * @brief Клас абстракції кадрового буфера у зовнішній пам'яті PSRAM.
 * 
 * Забезпечує безпечну алокацію пам'яті в PSRAM (SPIRAM), підрахунок посилань
 * та інкапсуляцію метаданих без блокування процесорного ядра ESP32-S3.
 */
class FrameBuffer : public std::enable_shared_from_this<FrameBuffer> {
public:
    using Ptr = std::shared_ptr<FrameBuffer>;

    /**
     * @brief Фабричний метод для створення екземпляра FrameBuffer у PSRAM.
     * @param capacity Максимальна ємність буфера в байтах
     * @param width Ширина кадру
     * @param height Висота кадру
     * @param format Формат пікселів
     * @return Умний вказівник std::shared_ptr на створений кадровий буфер або nullptr при помилці
     */
    static Ptr create(size_t capacity, uint32_t width, uint32_t height, PixelFormat format);

    ~FrameBuffer();

    // Заборона копіювання задля виключення подвійного звільнення пам'яті PSRAM
    FrameBuffer(const FrameBuffer&) = delete;
    FrameBuffer& operator=(const FrameBuffer&) = delete;

    // Семантика переміщення
    FrameBuffer(FrameBuffer&& other) noexcept;
    FrameBuffer& operator=(FrameBuffer&& other) noexcept;

    /// @brief Вказівник на сирий масив даних у PSRAM
    uint8_t* data() { return data_; }
    const uint8_t* data() const { return data_; }

    /// @brief Виділена ємність буфера у байтах
    size_t capacity() const { return capacity_; }

    /// @brief Метадані кадру
    FrameMetadata& metadata() { return metadata_; }
    const FrameMetadata& metadata() const { return metadata_; }

    /// @brief Встановлення фактичного розміру записаного кадру
    void setActualSize(size_t size);
    
    /// @brief Фактичний розмір корисного навантаження кадру
    size_t actualSize() const { return metadata_.dataSize; }

    /// @brief Інкремент атомарного лічильника посилань
    void retain();

    /// @brief Декремент атомарного лічильника посилань. Повертає true, якщо лічильник досяг 0.
    bool release();

    /// @brief Поточне значення лічильника посилань
    uint32_t refCount() const { return refCount_.load(std::memory_order_relaxed); }

private:
    FrameBuffer(size_t capacity, uint32_t width, uint32_t height, PixelFormat format);

    uint8_t* data_{nullptr};
    size_t capacity_{0};
    FrameMetadata metadata_{};
    std::atomic<uint32_t> refCount_{1};
};

} // namespace camera

#endif // FRAME_BUFFER_HPP
