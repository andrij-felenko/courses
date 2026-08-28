#include <stdint.h>

// Після налаштування OCTOSPI на memory-mapped режим уся HyperRAM
// доступна як звичайна пам'ять за цією базовою адресою.
#define HYPERRAM_BASE  0x90000000u

void hyperram_demo(void) {
    volatile uint16_t *ram = (uint16_t *)HYPERRAM_BASE;

    ram[0]   = 0xBEEF;          // контролер сам зробить DDR-запис по 8 лініях
    ram[1000] = 0x1234;         // адреса всередині масиву — просто зміщення
    uint16_t back = ram[0];     // а це — DDR-читання; back == 0xBEEF
    (void)back;
}
