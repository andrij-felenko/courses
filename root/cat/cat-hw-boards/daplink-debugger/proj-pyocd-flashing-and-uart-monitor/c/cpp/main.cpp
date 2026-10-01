#include "uart.hpp"
#include <array>
#include <string_view>
#include <cstdio>

namespace {

// Функція часової затримки
void delay_ms(uint32_t ms) {
    for (uint32_t i = 0; i < ms; ++i) {
        for (volatile uint32_t count = 0; count < 8000U; ++count) {
            asm volatile("nop");
        }
    }
}

} // namespace

int main() {
    // Ініціалізація екземпляра класу Uart зі швидкістю 115200 бод
    mcu::Uart debugger_uart(mcu::Uart::BaudRate::Baud115200);
    debugger_uart.init();

    // Передача банера прошивки в VCP WeAct Mini Debugger
    debugger_uart.send_string("\r\n============================================\r\n");
    debugger_uart.send_string("   WeAct Mini Debugger (DAPLink / ST-Link)  \r\n");
    debugger_uart.send_string("  ARM Cortex-M UART VCP Test Firmware (C++) \r\n");
    debugger_uart.send_string("============================================\r\n\r\n");

    uint32_t cycle_counter = 0;
    std::array<char, 128> tx_buffer{};

    while (true) {
        ++cycle_counter;

        // Форматування відправної стрічки телеметрії
        const int len = std::snprintf(
            tx_buffer.data(), tx_buffer.size(),
            "[C++ VCP Debug] Цикл #%lu | DAPLink VCP Активний | Status OK\r\n",
            static_cast<unsigned long>(cycle_counter)
        );

        if (len > 0) {
            debugger_uart.send_string(std::string_view(tx_buffer.data(), static_cast<size_t>(len)));
        }

        // Обробка зворотного зв'язку від користувача через термінал VCP
        char rx_char{};
        if (debugger_uart.receive_char(rx_char)) {
            debugger_uart.send_string(" -> C++ VCP Отримано дебаг-символ: '");
            debugger_uart.send_char(rx_char);
            debugger_uart.send_string("'\r\n");
        }

        delay_ms(1000);
    }

    return 0;
}
