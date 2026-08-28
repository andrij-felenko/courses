// C++ implementation: RAII-managed OSD Line Injector using std::span & Type Safety
#include <cstdint>
#include <array>
#include <span>
#include <algorithm>

class OsdLineInjector {
public:
    static constexpr std::size_t kActivePixels = 320;
    static constexpr std::size_t kBufferBytes  = kActivePixels / 8;
    static constexpr uint16_t kStartLine       = 40;
    static constexpr uint16_t kEndLine         = 280;

    OsdLineInjector() noexcept {
        clearBuffer();
    }

    // Очищення буфера рядка
    void clearBuffer() noexcept {
        line_buffer_.fill(0x00);
    }

    // Обробка рядкового синхроімпульсу HSYNC
    void handleHsync() noexcept {
        ++current_line_;
        if (current_line_ >= kStartLine && current_line_ <= kEndLine) {
            dma_busy_ = true;
            triggerDmaTransfer(std::span<const uint8_t>{line_buffer_});
        }
    }

    // Обробка кадрового синхроімпульсу VSYNC
    void handleVsync() noexcept {
        current_line_ = 0;
        is_active_frame_ = true;
    }

    // Встановлення точкового пікселя в маску
    void drawPixel(std::size_t x) noexcept {
        if (x < kActivePixels) {
            const std::size_t byte_idx = x / 8;
            const uint8_t bit_idx = static_cast<uint8_t>(7u - (x % 8));
            line_buffer_[byte_idx] |= static_cast<uint8_t>(1u << bit_idx);
        }
    }

    // Обробник завершення DMA
    void handleDmaComplete() noexcept {
        dma_busy_ = false;
    }

    [[nodiscard]] uint16_t currentLine() const noexcept {
        return current_line_;
    }

    [[nodiscard]] bool isBusy() const noexcept {
        return dma_busy_;
    }

private:
    void triggerDmaTransfer(std::span<const uint8_t> data) noexcept {
        // Апаратний запуск SPI DMA передачі у відеоключ після затримки 10.5 мкс
        (void)data;
    }

    std::array<uint8_t, kBufferBytes> line_buffer_{};
    volatile uint16_t current_line_{0};
    volatile bool is_active_frame_{false};
    volatile bool dma_busy_{false};
};
