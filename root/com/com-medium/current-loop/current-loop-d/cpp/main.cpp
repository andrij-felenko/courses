// cpp
#include <cstdint>
#include <array>
#include <expected>

namespace current_loop {

constexpr std::size_t BufferSize = 128;

enum class DriverError {
    BufferEmpty,
    LineBreakFault // Фізичний обрив петлі
};

class LoopReceiver {
public:
    void on_rx_interrupt(uint8_t byte, bool break_detected) noexcept {
        if (break_detected) {
            line_fault_ = true;
            return;
        }
        const auto next = (head_ + 1) % BufferSize;
        if (next != tail_) {
            buffer_[head_] = byte;
            head_ = next;
        }
    }

    [[nodiscard]] std::expected<uint8_t, DriverError> read_byte() noexcept {
        if (line_fault_) {
            return std::unexpected(DriverError::LineBreakFault);
        }
        if (head_ == tail_) {
            return std::unexpected(DriverError::BufferEmpty);
        }
        uint8_t byte = buffer_[tail_];
        tail_ = (tail_ + 1) % BufferSize;
        return byte;
    }

    void clear_fault() noexcept { line_fault_ = false; }

private:
    std::array<uint8_t, BufferSize> buffer_{};
    volatile std::size_t head_{0};
    volatile std::size_t tail_{0};
    volatile bool line_fault_{false};
};

} // namespace current_loop
:::

> ⚙️ Повний приклад проєкту з кільцевим буфером, обробкою помилок кадрування та таймером міжбайтового інтервалу дивіться у [реалізації трансивера струмової петлі](root:com-medium/current-loop/proj-current-loop-uart.md).

---

### Порівняльний підсумок інтерфейсів струмової петлі
