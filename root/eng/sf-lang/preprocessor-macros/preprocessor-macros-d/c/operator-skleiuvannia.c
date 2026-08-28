#include <stdio.h>

#define REGISTER_HANDLE(name) int handle_##name = 0

REGISTER_HANDLE(uart); // Розгортається у: int handle_uart = 0;
REGISTER_HANDLE(spi);  // Розгортається у: int handle_spi = 0;

int main(void) {
    printf("UART handle: %d, SPI handle: %d\n", handle_uart, handle_spi);
    return 0;
}
