#include <cstdint>
#include <cstddef>
#include <utility>

class St7789DmaPipeline {
public:
    static constexpr uint16_t Width = 240;
    static constexpr uint16_t Height = 240;
    static constexpr uint16_t BlockLines = 16;
    static constexpr size_t BlockPixels = Width * BlockLines;
    static constexpr size_t BlockBytes = BlockPixels * sizeof(uint16_t);

    St7789DmaPipeline() : dmaActive_(false) {}

    // Викликається з обробника переривання завершення транзакції DMA
    void onDmaCompleteInterrupt() {
        dmaActive_ = false;
    }

    // Шаблонний метод виведення кадру з довільним рендерером
    template <typename RenderCallback>
    void renderFrame(RenderCallback&& renderSlice) {
        uint8_t* renderBuffer = bufferA_;
        uint8_t* dmaBuffer = bufferB_;

        for (uint16_t y = 0; y < Height; y += BlockLines) {
            // Процесор формує пікселі для поточної смуги
            renderSlice(y, BlockLines, reinterpret_cast<uint16_t*>(renderBuffer));

            // Очікування вивільнення контролера DMA попередньою передачею
            while (dmaActive_) {
                // Очікування завершення апаратного перенесення даних
            }

            // Налаштування прямокутної області оновлення дисплея
            setWindow(0, y, Width - 1, y + BlockLines - 1);

            // Асинхронний старт передачі підготовленого блоку
            dmaActive_ = true;
            startDmaTransfer(renderBuffer, BlockBytes);

            // Обмін покажчиків: переданий буфер переходить під малювання
            std::swap(renderBuffer, dmaBuffer);
        }

        // Очікування фіналізації останньої транзакції кадру
        while (dmaActive_) {
        }
    }

private:
    uint8_t bufferA_[BlockBytes];
    uint8_t bufferB_[BlockBytes];
    volatile bool dmaActive_;

    void setWindow(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);
    void startDmaTransfer(const uint8_t* data, size_t length);
};
