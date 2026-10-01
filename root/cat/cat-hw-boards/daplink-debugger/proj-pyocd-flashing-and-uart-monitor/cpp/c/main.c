#include "uart.h"

#define USART2_BASE_ADDR ((uintptr_t)0x40004400U)

static void delay_ms(volatile uint32_t count) {
    while (count--) {
        for (volatile uint32_t i = 0; i < 4000; ++i) {
            __asm__("nop");
        }
    }
}

int main(void) {
    USART_Registers_t* usart2 = (USART_Registers_t*)USART2_BASE_ADDR;

    // Ініціалізація процедурного UART модуля на швидкість 115200 бод
    uart_init(usart2, 42000000U, 115200U);

    uart_println(usart2, "=========================================");
    uart_println(usart2, "[C-BOOT] WeAct Mini Debugger VCP Logger");
    uart_println(usart2, "[C-BOOT] Initialization complete.");
    uart_println(usart2, "=========================================");

    uint32_t loop_count = 0;

    while (1) {
        uart_write_string(usart2, "[C-LOG] Heartbeat count: ");

        // Преобразування числа в рядок без sprintf для мінімізації розміру бінарного файла
        char num_buf[16];
        uint32_t val = loop_count++;
        size_t idx = 0;

        if (val == 0) {
            num_buf[idx++] = '0';
        } else {
            char temp[16];
            size_t t_idx = 0;
            while (val > 0) {
                temp[t_idx++] = (char)('0' + (val % 10));
                val /= 10;
            }
            while (t_idx > 0) {
                num_buf[idx++] = temp[--t_idx];
            }
        }
        num_buf[idx] = '\0';

        uart_write_string(usart2, num_buf);
        uart_println(usart2, " | Transmitted over VCP");

        uart_flush(usart2);
        delay_ms(1000);
    }

    return 0;
}
