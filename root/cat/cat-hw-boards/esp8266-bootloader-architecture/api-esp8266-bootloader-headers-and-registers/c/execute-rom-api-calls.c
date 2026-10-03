#include <stdint.h>

/* Сигнатура системного виводу ets_printf у ROM */
typedef int (*ets_printf_t)(const char *fmt, ...);

/* Сигнатура процедури зчитування з SPI Flash у ROM */
typedef int (*spi_read_t)(uint32_t src_addr, uint32_t *dst_buf, uint32_t size);

/* Фіксовані адреси запечених процедур у масочному ROM */
#define ETS_PRINTF_ADDR 0x40002478U
#define SPI_READ_ADDR   0x40004b20U

void execute_rom_api_calls(void) {
    /* Прив'язка вказівників до адрес у ROM */
    ets_printf_t rom_printf = (ets_printf_t)ETS_PRINTF_ADDR;
    spi_read_t rom_spi_read = (spi_read_t)SPI_READ_ADDR;

    uint32_t flash_header[2];

    /* Звернення до системного виводу без підключення вагомих бібліотек */
    rom_printf("Ініціалізація: зчитування заголовка флеш-пам'яті...\n");

    /* Пряме зчитування 8 байтів з початкового зсуву SPI Flash */
    if (rom_spi_read(0x00000000, flash_header, sizeof(flash_header)) == 0) {
        rom_printf("Успіх! Сигнатура: 0x%08X\n", flash_header[0]);
    }
}
