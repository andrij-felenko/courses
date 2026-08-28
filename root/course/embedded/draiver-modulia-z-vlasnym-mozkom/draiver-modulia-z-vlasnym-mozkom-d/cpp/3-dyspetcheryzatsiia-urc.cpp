#include <cstdint>
#include <cstddef>
#include <string_view>
#include <array>
#include <optional>

template <size_t RingSize = 1024>
class UartDmaRingBuffer {
public:
    constexpr UartDmaRingBuffer() : tail_{0} {}

    [[nodiscard]] uint8_t* data() noexcept { return buffer_.data(); }
    [[nodiscard]] static constexpr size_t capacity() noexcept { return RingSize; }

    /* Виділення наступного доступного рядка зі зсувом Tail покажчика */
    [[nodiscard]] std::optional<size_t> extract_line(uint16_t dma_cndtr, 
                                                     char* out_buf, 
                                                     size_t max_len) noexcept {
        const uint16_t head = static_cast<uint16_t>(RingSize - dma_cndtr);
        if (head == tail_) {
            return std::nullopt;
        }

        uint16_t scan_idx = tail_;
        bool found = false;
        size_t raw_len = 0;

        while (scan_idx != head) {
            if (buffer_[scan_idx] == '\n') {
                found = true;
                break;
            }
            scan_idx = (scan_idx + 1U) % RingSize;
            if (++raw_len >= max_len - 1U) {
                tail_ = scan_idx; // Скидання некоректного рядка
                return std::nullopt;
            }
        }

        if (!found) {
            return std::nullopt;
        }

        size_t written = 0;
        while (tail_ != scan_idx) {
            const char c = static_cast<char>(buffer_[tail_]);
            if (c != '\r' && c != '\n' && written < max_len - 1U) {
                out_buf[written++] = c;
            }
            tail_ = (tail_ + 1U) % RingSize;
        }

        tail_ = (tail_ + 1U) % RingSize; // Пропуск '\n'
        out_buf[written] = '\0';

        if (written == 0) {
            return std::nullopt; // Порожній рядок
        }
        return written;
    }

private:
    std::array<uint8_t, RingSize> buffer_{};
    uint16_t tail_{0};
};
