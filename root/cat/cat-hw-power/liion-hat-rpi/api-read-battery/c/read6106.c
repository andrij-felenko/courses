// Той самий доступ через ядерний i2c-dev (без зовнішніх бібліотек).
// Компілювати: gcc read6106.c -o read6106
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

#define SW6106   0x3C   // адреса пристрою
#define REG_CTRL 0xB0   // єдиний задокументований регістр

int main(void) {
    int fd = open("/dev/i2c-1", O_RDWR);      // шина i2c-1
    if (fd < 0) { perror("open"); return 1; }

    if (ioctl(fd, I2C_SLAVE, SW6106) < 0) {   // обрати раба 0x3C
        perror("ioctl I2C_SLAVE"); close(fd); return 1;
    }

    unsigned char reg = REG_CTRL;
    if (write(fd, &reg, 1) != 1) {            // вказати регістр
        perror("write reg (пристрій мовчить?)"); close(fd); return 1;
    }

    unsigned char val = 0;
    if (read(fd, &val, 1) != 1) {             // прочитати байт
        perror("read"); close(fd); return 1;
    }

    printf("0xB0 = 0x%02X\n", val);
    close(fd);
    return 0;
}
