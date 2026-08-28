#include <array>
#include <span>
#include <optional>
#include <concepts>
#include <cstdint>
#include <cstddef>

template <std::size_t Capacity = 256>
class FlowControlRingBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of two");
    static constexpr std::size_t HighWatermark = Capacity * 3 / 4;
    static constexpr std::size_t LowWatermark  = Capacity * 1 / 4;

public:
    using RtsCallback = void (*)(bool is_ready);

    explicit FlowControlRingBuffer(RtsCallback rts_cb) noexcept
        : set_rts_{rts_cb}, rts_asserted_{true} {
        if (set_rts_) {
            set_rts_(true);
        }
    }

    // Виклик із контексту переривання UART
    [[nodiscard]] bool push_from_isr(uint8_t byte) noexcept {
        if (count_ >= Capacity) {
            return false;
        }

        storage_[head_] = byte;
        head_ = (head_ + 1) & (Capacity - 1);
        ++count_;

        if (rts_asserted_ && count_ >= HighWatermark) {
            rts_asserted_ = false;
            if (set_rts_) {
                set_rts_(false);
            }
        }
        return true;
    }

    // Виклик із контексту споживача
    [[nodiscard]] std::optional<uint8_t> pop() noexcept {
        if (count_ == 0) {
            return std::nullopt;
        }

        const uint8_t byte = storage_[tail_];
        tail_ = (tail_ + 1) & (Capacity - 1);
        --count_;

        if (!rts_asserted_ && count_ <= LowWatermark) {
            rts_asserted_ = true;
            if (set_rts_) {
                set_rts_(true);
            }
        }
        return byte;
    }

    [[nodiscard]] std::size_t size() const noexcept { return count_; }
    [[nodiscard]] bool is_ready() const noexcept { return rts_asserted_; }

private:
    std::array<uint8_t, Capacity> storage_{};
    volatile std::size_t head_{0};
    volatile std::size_t tail_{0};
    volatile std::size_t count_{0};
    RtsCallback set_rts_{nullptr};
    bool rts_asserted_{false};
};
