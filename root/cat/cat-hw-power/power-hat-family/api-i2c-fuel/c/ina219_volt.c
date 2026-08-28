// ina219_volt.c — прочитати напругу елемента з INA219 (адреса 0x40).
// Збірка:  gcc -O2 -o ina219_volt ina219_volt.c
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

#define INA219_ADDR   0x40   // 7-бітна; div by 2, якщо десь бачиш 0x80
#define REG_BUSVOLT   0x02

int main(void) {
    int fd = open("/dev/i2c-1", O_RDWR);
    if (fd < 0) { perror("open"); return 1; }
    if (ioctl(fd, I2C_SLAVE, INA219_ADDR) < 0) { perror("addr"); return 1; }

    unsigned char reg = REG_BUSVOLT, buf[2];
    write(fd, &reg, 1);          // навести покажчик на регістр напруги
    if (read(fd, buf, 2) != 2) { perror("read"); return 1; }

    // 16 біт big-endian; значущі — старші 13 → зсув на 3; крок 4 мВ
    int raw = (buf[0] << 8) | buf[1];
    double volts = (raw >> 3) * 0.004;   // 4 мВ на одиницю
    printf("Напруга елемента: %.3f В\n", volts);
    close(fd);
    return 0;
}
