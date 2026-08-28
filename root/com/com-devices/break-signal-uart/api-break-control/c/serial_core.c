/* Фрагмент інтерфейсу ядра serial_core (drivers/tty/serial/serial_core.c) */
#include <linux/serial_core.h>
#include <linux/tty.h>
#include <linux/sysrq.h>

/* Обробник Break у контексті переривання драйвера порту */
void kernel_uart_handle_break(struct uart_port *port) {
    if (uart_handle_break(port))
        return;

    /* Вставка TTY_BREAK у буфер термінала */
    tty_insert_flip_char(&port->state->port, 0, TTY_BREAK);
}
