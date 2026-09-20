#include "radio.h"
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>

int radio_init(RadioModule *radio, const char *spi_device) {
    radio->spi_fd = open(spi_device, O_RDWR);
    if (radio->spi_fd < 0) {
        return -1;
    }
    // Налаштування SPI (режим, швидкість тощо) зазвичай тут
    return 0;
}

int radio_get_rssi(RadioModule *radio, int8_t *rssi_out) {
    if (radio->spi_fd < 0) return -1;
    
    // Імітація зчитування регістру RSSI
    // Зазвичай адреса регістра специфічна для чипу, напр. CC1101 або NRF24L01
    uint8_t tx_buf[2] = {0x00, 0x00}; // Команда читання RSSI
    uint8_t rx_buf[2] = {0x00, 0x00};
    
    struct spi_ioc_transfer tr = {
        .tx_buf = (unsigned long)tx_buf,
        .rx_buf = (unsigned long)rx_buf,
        .len = 2,
        .delay_usecs = 0,
        .speed_hz = 500000,
        .bits_per_word = 8,
    };
    
    if (ioctl(radio->spi_fd, SPI_IOC_MESSAGE(1), &tr) < 1) {
        return -1;
    }
    
    // Симуляція значення RSSI з регістра
    *rssi_out = -75; // Наприклад, -75 дБм
    return 0;
}

void radio_close(RadioModule *radio) {
    if (radio->spi_fd >= 0) {
        close(radio->spi_fd);
        radio->spi_fd = -1;
    }
}
