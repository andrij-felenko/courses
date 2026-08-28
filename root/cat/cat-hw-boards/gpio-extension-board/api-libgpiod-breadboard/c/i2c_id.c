// i2c_id.c — читаємо регістр 0xD0 (id) BMP280 за адресою 0x76 на шині i2c-1
// збірка:  gcc i2c_id.c -o i2c_id
#include <stdio.h>
#include <fcntl.h>            // open
#include <unistd.h>          // read, write, close
#include <string.h>
#include <errno.h>
#include <linux/i2c-dev.h>   // I2C_SLAVE
#include <sys/ioctl.h>

#define I2C_BUS   "/dev/i2c-1"   // лінії SDA (GPIO2) і SCL (GPIO3), виведені платою
#define ADDR      0x76           // адреса BMP280 на шині
#define REG_ID    0xD0           // регістр «id»; має віддати 0x58

int main(void)
{
    int fd = open(I2C_BUS, O_RDWR);
    if (fd < 0) { fprintf(stderr, "відкрити %s: %s\n", I2C_BUS, strerror(errno)); return 1; }

    // кажемо драйверу, з яким пристроєм на шині говоримо
    if (ioctl(fd, I2C_SLAVE, ADDR) < 0) {
        fprintf(stderr, "нема пристрою 0x%02X: %s\n", ADDR, strerror(errno));
        close(fd); return 1;
    }

    unsigned char reg = REG_ID;
    if (write(fd, &reg, 1) != 1) {           // крок 1: пишемо номер регістра
        fprintf(stderr, "запис регістра: %s\n", strerror(errno)); close(fd); return 1;
    }

    unsigned char id = 0;
    if (read(fd, &id, 1) != 1) {             // крок 2: читаємо його вміст
        fprintf(stderr, "читання: %s\n", strerror(errno)); close(fd); return 1;
    }

    printf("id давача = 0x%02X %s\n", id,
           id == 0x58 ? "(BMP280 — зв'язок є!)" : "(не той підпис?)");
    close(fd);
    return 0;
}
