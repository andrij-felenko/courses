#include <cstdint>
#include <atomic>

class DisplaySyncEngine {
public:
    DisplaySyncEngine() : frame_ready_(false), dma_busy_(false), buffer_(nullptr), size_(0) {}

    // Реєстрація буфера кадру для безпечного виводу
    void postFrame(const uint8_t* buffer, uint32_t size) {
        buffer_ = buffer;
        size_ = size;
        frame_ready_.store(true, std::memory_order_release);
    }

    // Викликається з підпрограми обробки переривання піна TE
    void onTearingEffectInterrupt() {
        if (frame_ready_.load(std::memory_order_acquire) && !dma_busy_.load(std::memory_order_relaxed)) {
            frame_ready_.store(false, std::memory_order_relaxed);
            dma_busy_.store(true, std::memory_order_release);

            // Переведення ліній керування в режим передачі даних
            setChipSelect(false);
            setDataCommand(true);

            // Апаратний пуск передавача без блокування ядра
            startDmaTransfer(buffer_, size_);
        }
    }

    // Викликається після завершення спустошення буфера DMA
    void onDmaTransferComplete() {
        setChipSelect(true);
        dma_busy_.store(false, std::memory_order_release);
    }

private:
    std::atomic<bool> frame_ready_;
    std::atomic<bool> dma_busy_;
    const uint8_t* buffer_;
    uint32_t size_;

    void setChipSelect(bool level);
    void setDataCommand(bool is_data);
    void startDmaTransfer(const uint8_t* data, uint32_t len);
};
