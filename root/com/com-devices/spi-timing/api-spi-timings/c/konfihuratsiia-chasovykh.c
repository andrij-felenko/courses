#include <linux/spi/spidev.h>
#include <sys/ioctl.h>
#include <stdint.h>
#include <stdbool.h>

bool perform_spi_transfer(int fd, const uint8_t *tx, uint8_t *rx, uint32_t len) {
    struct spi_ioc_transfer tr = {
        .tx_buf = (unsigned long)tx,
        .rx_buf = (unsigned long)rx,
        .len = len,
        .speed_hz = 25000000,               // 25 МГц
        .delay_usecs = 0,                   // Пауза після передачі пакета в мікросекундах
        .bits_per_word = 8,
        .cs_change = 0,                     // 0 = утримувати CS активним, 1 = відпустити після трансферу
        .word_delay_usecs = 0,              // Затримка між окремими словами
    };

    return ioctl(fd, SPI_IOC_MESSAGE(1), &tr) >= 0;
}
