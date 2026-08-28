#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>

enum class DriverError {
    BusBusy,
    BufferOverflow,
    HardwareFault,
    Timeout
};

enum class BusState {
    Idle,
    Transmitting,
    Receiving,
    Error
};

template <size_t BufferSize = 256>
class HalfDuplexUart {
public:
    constexpr explicit HalfDuplexUart(bool suppress_echo = true) noexcept
        : suppress_local_echo_(suppress_echo) {}

    void init() noexcept {
        tx_head_ = 0;
        tx_len_ = 0;
        rx_len_ = 0;
        state_ = BusState::Idle;
        echo_to_skip_ = 0;
        set_driver_enable(false);
    }

    [[nodiscard]] std::expected<void, DriverError> send(std::span<const uint8_t> data) noexcept {
        if (data.empty() || data.size() > BufferSize) {
            return std::unexpected(DriverError::BufferOverflow);
        }
        if (state_ == BusState::Transmitting) {
            return std::unexpected(DriverError::BusBusy);
        }

        for (size_t i = 0; i < data.size(); ++i) {
            tx_buffer_[i] = data[i];
        }
        tx_len_ = data.size();
        tx_head_ = 0;
        echo_to_skip_ = suppress_local_echo_ ? tx_len_ : 0;
        state_ = BusState::Transmitting;

        // Активація режиму передачі
        set_driver_enable(true);
        start_hardware_tx();
        return {};
    }

    [[nodiscard]] std::span<const uint8_t> received_data() const noexcept {
        return std::span<const uint8_t>(rx_buffer_.data(), rx_len_);
    }

    void clear_rx_buffer() noexcept {
        rx_len_ = 0;
    }

    [[nodiscard]] BusState state() const noexcept {
        return state_;
    }

    // Обробники внутрішніх переривань апаратного контролера
    void on_txe_interrupt() noexcept {
        if (state_ != BusState::Transmitting) return;

        if (tx_head_ < tx_len_) {
            write_hw_tdr(tx_buffer_[tx_head_++]);
        } else {
            disable_hw_txe_interrupt();
            enable_hw_tc_interrupt();
        }
    }

    void on_tc_interrupt() noexcept {
        clear_hw_tc_flag();
        disable_hw_tc_interrupt();
        set_driver_enable(false); // Повернення лінії в прийом
        state_ = BusState::Idle;
    }

    void on_rxne_interrupt(uint8_t received_byte) noexcept {
        if (echo_to_skip_ > 0) {
            --echo_to_skip_;
            return;
        }
        if (rx_len_ < BufferSize) {
            rx_buffer_[rx_len_++] = received_byte;
        }
    }

private:
    std::array<uint8_t, BufferSize> tx_buffer_{};
    std::array<uint8_t, BufferSize> rx_buffer_{};
    volatile size_t tx_head_{0};
    volatile size_t tx_len_{0};
    volatile size_t rx_len_{0};
    volatile size_t echo_to_skip_{0};
    volatile BusState state_{BusState::Idle};
    bool suppress_local_echo_{true};

    // Апаратно-залежні методи доступу до регістрів
    static void set_driver_enable(bool enable) noexcept {
        if (enable) {
            GPIOA->BSRR = (1 << 4);
        } else {
            GPIOA->BSRR = (1 << (4 + 16));
        }
    }

    void start_hardware_tx() noexcept {
        USART1->TDR = tx_buffer_[tx_head_++];
        USART1->CR1 |= USART_CR1_TXEIE;
    }

    static void write_hw_tdr(uint8_t byte) noexcept {
        USART1->TDR = byte;
    }

    static void disable_hw_txe_interrupt() noexcept {
        USART1->CR1 &= ~USART_CR1_TXEIE;
    }

    static void enable_hw_tc_interrupt() noexcept {
        USART1->CR1 |= USART_CR1_TCIE;
    }

    static void clear_hw_tc_flag() noexcept {
        USART1->ICR = USART_ICR_TCCF;
    }

    static void disable_hw_tc_interrupt() noexcept {
        USART1->CR1 &= ~USART_CR1_TCIE;
    }
};
