#include <iostream>

#define REGISTER_HANDLE(name) int handle_##name = 0

REGISTER_HANDLE(uart); // int handle_uart = 0;
REGISTER_HANDLE(spi);  // int handle_spi = 0;

int main() {
    std::cout << "UART handle: " << handle_uart
              << ", SPI handle: " << handle_spi << "\n";
    return 0;
}
