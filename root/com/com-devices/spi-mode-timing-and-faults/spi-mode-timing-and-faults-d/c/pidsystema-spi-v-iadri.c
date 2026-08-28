#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>
#include <stdint.h>
#include <stdio.h>

int set_spi_mode(const char *device_path, uint8_t mode) {
    int fd = open(device_path, O_RDWR);
    if (fd < 0) return -1;

    /* mode може набувати значень: SPI_MODE_0, SPI_MODE_1, SPI_MODE_2, SPI_MODE_3 */
    if (ioctl(fd, SPI_IOC_WR_MODE, &mode) < 0) {
        close(fd);
        return -2;
    }

    return fd;
}
