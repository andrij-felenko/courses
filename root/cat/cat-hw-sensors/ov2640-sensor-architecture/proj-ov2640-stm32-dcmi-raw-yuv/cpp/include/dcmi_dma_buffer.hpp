#ifndef DCMI_DMA_BUFFER_HPP
#define DCMI_DMA_BUFFER_HPP

#include <cstdint>
#include <cstddef>
#include <vector>
#include <functional>
#include <memory>

namespace ov2640 {

/**
 * @brief Структура метаданих та двійкового вмісту відзнятого кадру зображення.
 */
struct FrameBuffer {
    uint8_t* data{nullptr};          // Вказівник на двійковий масив пікселів/JPEG кадру у RAM/PSRAM
    size_t capacity{0};              // Виділений розмір буфера в байтах
    size_t length{0};                // Фактична довжина кадрів у байтах після захоплення
    uint32_t sequence_number{0};     // Порядковий номер кадру
    uint64_t timestamp_us{0};         // Часова позначка завершення захоплення (мікросекунди)
    bool is_valid{false};             // Прапорець цілісності кадру
};

/// Режими функціонування DMA буферизації
enum class DmaBufferMode {
    DoubleBuffer,       // Двобуферний режим (Ping-Pong)
    CircularRingBuffer  // Кільцевий буфер (3 і більше кадрових секцій)
};

/**
 * @brief Менеджер кадрової відеопам'яті та апаратних інтерфейсів DCMI/DMA.
 * Відповідає за виділення буферів у оперативній пам'яті, обробку переривань DCMI/DMA,
 * перемикання активних буферів та синхронізацію кадрів за сигналами VSYNC/HREF/PCLK.
 */
class DcmiDmaBuffer {
public:
    using FrameReadyCallback = std::function<void(const FrameBuffer&)>;

    DcmiDmaBuffer(size_t buffer_count = 2, size_t buffer_capacity_bytes = 64 * 1024);
    ~DcmiDmaBuffer();

    DcmiDmaBuffer(const DcmiDmaBuffer&) = delete;
    DcmiDmaBuffer& operator=(const DcmiDmaBuffer&) = delete;

    /// Виділення пам'яті під кадрові буфери та конфігурація периферії DMA
    bool init();

    /// Запуск циклічного захоплення DMA
    bool startCapture();

    /// Зупинка захоплення DMA
    void stopCapture();

    /// Реєстрація асинхронного обробника події готовності кадру
    void setFrameCallback(FrameReadyCallback callback);

    /// Отримання стану захоплення
    bool isCapturing() const { return is_capturing_; }

    /// Обробник переривання DMA Half Transfer (заповнено половину поточного буфера)
    void handleDmaHalfTransferInterrupt();

    /// Обробник переривання DMA Transfer Complete (буфер заповнено)
    void handleDmaTransferCompleteInterrupt();

    /// Обробник переривання DCMI VSYNC (початок/кінець кадру)
    void handleDcmiVsyncInterrupt();

    /// Обробник переривання DCMI Frame Complete (апаратне завершення кадру)
    void handleDcmiFrameInterrupt(size_t actual_received_bytes);

    /// Доступ до конкретного кадрового буфера за індексом
    const FrameBuffer& getBuffer(size_t index) const;

private:
    size_t buffer_count_;
    size_t buffer_capacity_;
    std::vector<FrameBuffer> buffers_;
    std::vector<std::unique_ptr<uint8_t[]>> memory_pools_;

    size_t active_write_index_{0};
    size_t active_read_index_{0};
    uint32_t frame_counter_{0};
    bool is_capturing_{false};

    FrameReadyCallback frame_callback_{nullptr};

    void advanceBufferIndex();
};

} // namespace ov2640

#endif // DCMI_DMA_BUFFER_HPP
