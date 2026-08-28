#include <stdint.h>
// Регістр FIFO передавача UART0 — фіксована адреса в карті пам'яті.
// У залізі тут периферія; в емуляторі цю саму адресу перехоплює модель.
#define UART0_FIFO  (*(volatile uint32_t *)0x3FF40000)

static void uart_putc(char c) {
    UART0_FIFO = (uint32_t)c;   // той самий запис, що й на чипі
}

int app_main(void) {
    const char *msg = "boot ok\n";
    for (const char *p = msg; *p; ++p)
        uart_putc(*p);          // емулятор «надрукує» це у свій stdout
    return 0;
}
