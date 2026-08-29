// Ретрансляція UART → I2C: як виглядає та сама дія, якщо не чекати в ISR.
#pragma once

#include <cstdint>
#include <expected>

namespace isr {

enum class I2cError : std::uint8_t {
    Timeout,  // пристрій не відпустив шину за відведений час
    BusError, // залізо підняло BERR: колізія на лінії
    Nack      // адресу ніхто не підтвердив
};

class I2cRelay {
public:
    static void start();

    // Верхня половина USART2: забрати байт і піти.
    static void handle_irq() noexcept;

    [[nodiscard]] static std::uint32_t dropped() noexcept;
    [[nodiscard]] static std::uint32_t failures() noexcept;

private:
    // Помилка тут — очікуваний результат, а не аварія, тож вона й повертається
    // значенням. Ні -1, ні errno, ні винятку: у прошивці без розкрутки стека
    // std::expected каже те саме дешевше й чесніше.
    static std::expected<void, I2cError> write(std::uint8_t addr7, std::uint8_t data) noexcept;

    static void relay_entry(void *arg) noexcept;
};

} // namespace isr
