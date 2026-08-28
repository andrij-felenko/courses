// sw6106_probe.c — прочитати керувальний регістр SW6106 по I²C.
// Збірка:  gcc -O2 -o sw6106_probe sw6106_probe.c
// Запуск:  ./sw6106_probe            (потрібні права на /dev/i2c-1)
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

#define SW6106_ADDR  0x3C   // 7-бітна адреса (саме 7-бітна — див. блок нижче)
#define SW6106_REG   0xB0   // єдиний керувальний регістр із datasheet

int main(void) {
    int fd = open("/dev/i2c-1", O_RDWR);
    if (fd < 0) { perror("open /dev/i2c-1"); return 1; }

    // ioctl бере САМЕ 7-бітну адресу; ядро само зсуне її й додасть біт R/W
    if (ioctl(fd, I2C_SLAVE, SW6106_ADDR) < 0) {
        perror("ioctl I2C_SLAVE"); close(fd); return 1;
    }

    // записати номер регістра, потім прочитати його байт (SMBus read-byte-data)
    unsigned char reg = SW6106_REG, val = 0;
    if (write(fd, &reg, 1) != 1) {          // виставити «покажчик» на 0xB0
        fprintf(stderr, "write reg: %s\n", strerror(errno));
        fprintf(stderr, "  порожньо у i2cdetect? LED4/I2C не на землі.\n");
        close(fd); return 1;
    }
    if (read(fd, &val, 1) != 1) {           // прочитати вміст 0xB0
        fprintf(stderr, "read val: %s\n", strerror(errno));
        close(fd); return 1;
    }

    printf("SW6106 reg 0xB0 = 0x%02X\n", val);
    printf("Це керувальне значення, НЕ відсоток заряду.\n");
    close(fd);
    return 0;
}
