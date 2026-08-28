#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

/* Сканування всього 10-бітного адресного простору I2C */
void i2c_10bit_scan(int fd) {
    printf("Початок сканування 10-бітної шини I2C...\n");
    int found_count = 0;

    for (uint16_t addr = 0x008; addr <= 0x3F7; addr++) {
        struct i2c_msg msg;
        struct i2c_rdwr_ioctl_data rdwr;

        /* Формуємо порожнє повідомлення запису (перевірка наявності ACK) */
        msg.addr  = addr;
        msg.flags = I2C_M_TEN;
        msg.len   = 0;
        msg.buf   = NULL;

        rdwr.msgs  = &msg;
        rdwr.nmsgs = 1;

        if (ioctl(fd, I2C_RDWR, &rdwr) >= 0) {
            printf("Знайдено 10-бітний пристрій на адресі: 0x%03X (%u)\n", addr, addr);
            found_count++;
        }
    }

    printf("Сканування завершено. Знайдено пристроїв: %d\n", found_count);
}
