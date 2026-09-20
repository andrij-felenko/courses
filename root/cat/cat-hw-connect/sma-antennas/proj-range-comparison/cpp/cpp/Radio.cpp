#include "Radio.hpp"
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>
#include <system_error>

Radio::Radio(const std::string& spi_device) {
    spi_fd = open(spi_device.c_str(), O_RDWR);
    if (spi_fd < 0) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити SPI пристрій");
    }
    // Налаштування SPI (швидкість, фаза тощо)
}

Radio::~Radio() {
    if (spi_fd >= 0) {
        close(spi_fd);
    }
}

int8_t Radio::getRssi() const {
    uint8_t tx_buf[2] = {0x00, 0x00}; // Команда читання RSSI
    uint8_t rx_buf[2] = {0x00, 0x00};
    
    struct spi_ioc_transfer tr = {};
    tr.tx_buf = reinterpret_cast<unsigned long>(tx_buf);
    tr.rx_buf = reinterpret_cast<unsigned long>(rx_buf);
    tr.len = 2;
    tr.speed_hz = 500000;
    tr.bits_per_word = 8;
    
    if (ioctl(spi_fd, SPI_IOC_MESSAGE(1), &tr) < 1) {
        throw std::system_error(errno, std::generic_category(), "Помилка SPI транзакції");
    }
    
    // Симуляція значення RSSI з регістра
    return -75; // -75 дБм
}
