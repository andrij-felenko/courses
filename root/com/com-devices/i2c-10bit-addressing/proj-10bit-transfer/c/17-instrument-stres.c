#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

/* Виконання 1000 циклів читання для оцінки надійності зв'язку */
void i2c_10bit_stress_test(int fd, uint16_t addr10, int iterations) {
    int errors = 0;
    uint8_t reg = 0x00;
    uint8_t val = 0;

    printf("Початок стрес-тесту для адреси 0x%03X (%d ітерацій)...\n", addr10, iterations);

    for (int i = 0; i < iterations; i++) {
        struct i2c_msg msgs[2];
        msgs[0].addr  = addr10;
        msgs[0].flags = I2C_M_TEN;
        msgs[0].len   = 1;
        msgs[0].buf   = &reg;

        msgs[1].addr  = addr10;
        msgs[1].flags = I2C_M_TEN | I2C_M_RD;
        msgs[1].len   = 1;
        msgs[1].buf   = &val;

        struct i2c_rdwr_ioctl_data rdwr;
        rdwr.msgs  = msgs;
        rdwr.nmsgs = 2;

        if (ioctl(fd, I2C_RDWR, &rdwr) < 0) {
            errors++;
        }
        usleep(1000); /* Пауза 1 мс між циклами */
    }

    printf("Тест завершено. Помилок: %d / %d (%.2f%%)\n",
           errors, iterations, (float)errors * 100.0f / (float)iterations);
}
