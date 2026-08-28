// spi_xfer.c — повнодуплексний обмін по SPI0, chip-enable CE0 (/dev/spidev0.0)
// збірка:  gcc spi_xfer.c -o spi_xfer
#include <stdio.h>
#include <fcntl.h>            // open
#include <unistd.h>          // close
#include <string.h>          // memset
#include <errno.h>
#include <stdint.h>
#include <linux/spi/spidev.h>
#include <sys/ioctl.h>

#define SPI_DEV   "/dev/spidev0.0"   // SPI0, CE0 = GPIO8 (штир 24)

int main(void)
{
    int fd = open(SPI_DEV, O_RDWR);
    if (fd < 0) { fprintf(stderr, "відкрити %s: %s\n", SPI_DEV, strerror(errno)); return 1; }

    // параметри шини: режим 0, 8 біт на слово, 1 МГц (звіряйте з даташитом пристрою)
    uint8_t  mode = SPI_MODE_0;
    uint8_t  bits = 8;
    uint32_t hz   = 1000000;
    if (ioctl(fd, SPI_IOC_WR_MODE, &mode)          < 0 ||
        ioctl(fd, SPI_IOC_WR_BITS_PER_WORD, &bits) < 0 ||
        ioctl(fd, SPI_IOC_WR_MAX_SPEED_HZ, &hz)    < 0) {
        fprintf(stderr, "налаштування шини: %s\n", strerror(errno)); close(fd); return 1;
    }

    // надсилаємо 2 байти й водночас забираємо 2 байти відповіді
    uint8_t tx[2] = { 0x9F, 0x00 };   // напр. команда «read ID» + порожній такт
    uint8_t rx[2] = { 0, 0 };

    struct spi_ioc_transfer tr;
    memset(&tr, 0, sizeof tr);         // ОБОВ'ЯЗКОВО: обнулити невживані поля
    tr.tx_buf        = (unsigned long) tx;
    tr.rx_buf        = (unsigned long) rx;
    tr.len           = 2;
    tr.speed_hz      = hz;
    tr.bits_per_word = bits;

    // SPI_IOC_MESSAGE(1) — один transfer; поки жене такт, tx їде, rx приходить
    if (ioctl(fd, SPI_IOC_MESSAGE(1), &tr) < 0) {
        fprintf(stderr, "обмін не вдався: %s\n", strerror(errno)); close(fd); return 1;
    }

    printf("прийнято: 0x%02X 0x%02X\n", rx[0], rx[1]);
    close(fd);
    return 0;
}
