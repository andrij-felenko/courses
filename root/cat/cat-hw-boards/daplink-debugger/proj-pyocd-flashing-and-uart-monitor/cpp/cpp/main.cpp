#include "uart.hpp"

// Базова адреса регістрів USART2 у карті пам'яті ARM Cortex-M (STM32)
constexpr uintptr_t USART2_BASE = 0x40004400U;

// Допоміжна функція затримки для демонстраційного циклу
static void delay_ms(volatile uint32_t count) {
    while (count--) {
        for (volatile uint32_t i = 0; i < 4000; ++i) {
            __asm__("nop");
        }
    }
}

int main() {
    // Отримання вказівника на апаратний модуль USART2
    auto* usart2_regs = reinterpret_cast<mcu::Uart::Registers*>(USART2_BASE);

    // Створення екземпляра C++ класу-обгортки Uart
    mcu::Uart logger(usart2_regs);

    // Ініціалізація UART на швидкість 115200 бод при частоті шини APB1 = 42 МГц
    // Ця швидкість використовується для моніторингу через VCP WeAct Mini Debugger
    constexpr uint32_t APB1_BUS_FREQ = 42000000U; // 42 MHz
    constexpr uint32_t BAUD_RATE     = 115200U;

    logger.init(APB1_BUS_FREQ, BAUD_RATE);

    // Надсилання стартового діагностичного повідомлення
    logger.println("=========================================");
    logger.println("[BOOT] WeAct Mini Debugger UART Logger");
    logger.println("[BOOT] System initialized. Target: ARM Cortex-M");
    logger.println("=========================================");

    uint32_t packet_counter = 0;

    // Головний суперцикл прошивки мікроконтролера
    while (true) {
        logger.write("[STATUS] Running telemetry loop, packet #");

        // Ручне форматування лічильника без виділення динамічної пам'яті
        char buf[16];
        uint32_t val = packet_counter++;
        size_t idx = 0;
        if (val == 0) {
            buf[idx++] = '0';
        } else {
            char temp[16];
            size_t t_idx = 0;
            while (val > 0) {
                temp[t_idx++] = static_cast<char>('0' + (val % 10));
                val /= 10;
            }
            while (t_idx > 0) {
                buf[idx++] = temp[--t_idx];
            }
        }
        buf[idx] = '\0';

        logger.write(std::string_view(buf, idx));
        logger.println(" | Debugger: DAPLink/ST-Link V2.1 VCP OK");

        // Гарантована вичистка буфера перед входом у стан очікування
        logger.flush();

        // Затримка між відправками логів (~1 секунда)
        delay_ms(1000);
    }

    return 0;
}
