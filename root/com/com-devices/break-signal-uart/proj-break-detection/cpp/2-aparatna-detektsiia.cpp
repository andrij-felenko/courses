// uart_break_receiver.hpp - Безпечний C++ автомат детекції Break
#include <cstdint>
#include <array>
#include <atomic>

class DmxReceiver {
public:
    static constexpr size_t BufferSize = 512;

    enum class State : uint8_t {
        WaitBreak,
        WaitStartCode,
        ReceiveData
    };

    void handle_uart_irq(uint32_t status_reg, uint8_t data_reg) noexcept {
        const bool framing_error = (status_reg & (1u << 1)) != 0;

        if (framing_error) {
            if (data_reg == 0x00) {
                // Виявлено Break: синхронізація початку пакета
                state_ = State::WaitStartCode;
                channel_idx_ = 0;
            }
            return;
        }

        switch (state_) {
            case State::WaitStartCode:
                if (data_reg == 0x00) {
                    state_ = State::ReceiveData;
                    channel_idx_ = 0;
                } else {
                    state_ = State::WaitBreak;
                }
                break;

            case State::ReceiveData:
                if (channel_idx_ < BufferSize) {
                    buffer_[channel_idx_++] = data_reg;
                    if (channel_idx_ == BufferSize) {
                        frame_ready_.store(true, std::memory_order_release);
                        state_ = State::WaitBreak;
                    }
                }
                break;

            case State::WaitBreak:
            default:
                break;
        }
    }

    [[nodiscard]] bool is_frame_ready() const noexcept {
        return frame_ready_.load(std::memory_order_acquire);
    }

    void clear_frame_ready() noexcept {
        frame_ready_.store(false, std::memory_order_release);
    }

    [[nodiscard]] const std::array<uint8_t, BufferSize>& data() const noexcept {
        return buffer_;
    }

private:
    State state_{State::WaitBreak};
    size_t channel_idx_{0};
    std::atomic<bool> frame_ready_{false};
    std::array<uint8_t, BufferSize> buffer_{};
};
