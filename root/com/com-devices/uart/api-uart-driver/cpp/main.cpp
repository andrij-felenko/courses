#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>

class UartPeripheral {
public:
    static constexpr size_t BufferSize = 128;

    enum class Error : uint8_t {
        BufferOverflow,
        HardwareOverrun,
        FramingError,
        ParityError,
        TxBufferFull
    };

    explicit UartPeripheral(uintptr_t base_address) noexcept
        : hw_base_(reinterpret_cast<volatile uint32_t*>(base_address)) {}

    ~UartPeripheral() noexcept = default;

    // Заборона копіювання (RAII керування апаратним ресурсом)
    UartPeripheral(const UartPeripheral&) = delete;
    UartPeripheral& operator=(const UartPeripheral&) = delete;
    UartPeripheral(UartPeripheral&&) noexcept = default;
    UartPeripheral& operator=(UartPeripheral&&) noexcept = default;

    void init(uint32_t baud_rate, bool enable_rts_cts) noexcept {
        // Конфігурація апаратного модуля
        hw_base_[3] = 0; // CR1 reset
        // Налаштування baud і прапорців...
        hw_base_[3] |= (1U << 13) | (1U << 2) | (1U << 3) | (1U << 5); // UE, RE, TE, RXNEIE
    }

    [[nodiscard]] std::expected<void, Error> send(uint8_t byte) noexcept {
        const size_t next_head = (tx_head_ + 1) % BufferSize;
        if (next_head == tx_tail_) {
            return std::unexpected(Error::TxBufferFull);
        }
        tx_buffer_[tx_head_] = byte;
        tx_head_ = next_head;

        // Увімкнути переривання TXEIE
        hw_base_[3] |= (1U << 7);
        return {};
    }

    [[nodiscard]] size_t send(std::span<const uint8_t> data) noexcept {
        size_t written = 0;
        for (uint8_t b : data) {
            if (!send(b).has_value()) {
                break;
            }
            ++written;
        }
        return written;
    }

    [[nodiscard]] std::expected<uint8_t, Error> receive() noexcept {
        if (rx_head_ == rx_tail_) {
            return std::unexpected(Error::BufferOverflow); // Або NoData
        }
        uint8_t byte = rx_buffer_[rx_tail_];
        rx_tail_ = (rx_tail_ + 1) % BufferSize;
        return byte;
    }

    [[nodiscard]] size_t available() const noexcept {
        if (rx_head_ >= rx_tail_) {
            return rx_head_ - rx_tail_;
        }
        return BufferSize - (rx_tail_ - rx_head_);
    }

    // Обробник переривання (викликується з векторного столу IRQ)
    void handle_interrupt() noexcept {
        const uint32_t sr = hw_base_[0]; // SR
        const uint32_t cr1 = hw_base_[3]; // CR1

        // Читання RXNE
        if (sr & (1U << 5)) {
            const uint8_t byte = static_cast<uint8_t>(hw_base_[1]); // DR
            const size_t next_head = (rx_head_ + 1) % BufferSize;
            if (next_head != rx_tail_) {
                rx_buffer_[rx_head_] = byte;
                rx_head_ = next_head;
            } else {
                last_error_ = Error::BufferOverflow;
            }
        }

        // Запис TXE
        if ((sr & (1U << 7)) && (cr1 & (1U << 7))) {
            if (tx_head_ != tx_tail_) {
                hw_base_[1] = tx_buffer_[tx_tail_];
                tx_tail_ = (tx_tail_ + 1) % BufferSize;
            } else {
                hw_base_[3] &= ~(1U << 7); // Вимкнути TXEIE
            }
        }
    }

private:
    volatile uint32_t* hw_base_;
    std::array<uint8_t, BufferSize> rx_buffer_{};
    std::array<uint8_t, BufferSize> tx_buffer_{};
    volatile size_t rx_head_{0};
    volatile size_t rx_tail_{0};
    volatile size_t tx_head_{0};
    volatile size_t tx_tail_{0};
    Error last_error_{Error::BufferOverflow};
};
