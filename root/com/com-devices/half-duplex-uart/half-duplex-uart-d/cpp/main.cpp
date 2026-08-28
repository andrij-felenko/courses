#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

enum class SerialError {
    EmptyBuffer,
    HardwareFault
};

// RAII-обгортка керування лінією Driver Enable
class [[nodiscard]] DirectionGuard {
public:
    explicit DirectionGuard() noexcept {
        set_pin_high();
    }

    ~DirectionGuard() noexcept {
        set_pin_low();
    }

    DirectionGuard(const DirectionGuard&) = delete;
    DirectionGuard& operator=(const DirectionGuard&) = delete;

private:
    static void set_pin_high() noexcept {
        GPIOA->BSRR = (1 << 4);
    }
    static void set_pin_low() noexcept {
        GPIOA->BSRR = (1 << (4 + 16));
    }
};

class HalfDuplexPort {
public:
    explicit constexpr HalfDuplexPort() noexcept = default;

    [[nodiscard]] std::expected<void, SerialError> send_frame(std::span<const uint8_t> packet) noexcept {
        if (packet.empty()) {
            return std::unexpected(SerialError::EmptyBuffer);
        }

        // Активація режиму передачі через об'єкт з автоматичним контролем часу життя
        DirectionGuard direction_guard;

        for (const uint8_t byte : packet) {
            wait_for_txe();
            write_tdr(byte);
        }

        // Чекаємо завершення зсуву останнього стоп-біта
        wait_for_tc();
        clear_tc_flag();

        // Деструктор direction_guard гарантовано опустить DE при виході з функції
        return {};
    }

private:
    static void wait_for_txe() noexcept {
        while (!(USART1->ISR & USART_ISR_TXE_TXFNF)) {}
    }
    static void write_tdr(uint8_t byte) noexcept {
        USART1->TDR = byte;
    }
    static void wait_for_tc() noexcept {
        while (!(USART1->ISR & USART_ISR_TC)) {}
    }
    static void clear_tc_flag() noexcept {
        USART1->ICR = USART_ICR_TCCF;
    }
};
