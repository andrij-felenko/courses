#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

/* Зчитування двох байтів із внутрішнього регістра 10-бітного веденого */
int read_sensor_10bit(int fd, uint16_t addr10, uint8_t reg, uint8_t *val_high, uint8_t *val_low) {
    uint8_t buffer[2] = {0};
    struct i2c_msg msgs[2];
    struct i2c_rdwr_ioctl_data rdwr;

    /* 1-й кадр: передача адреси регістра в режимі запису */
    msgs[0].addr  = addr10;
    msgs[0].flags = I2C_M_TEN;         /* 10-бітна адреса, R/W = 0 */
    msgs[0].len   = 1;
    msgs[0].buf   = &reg;

    /* 2-й кадр: читання даних через Repeated START */
    msgs[1].addr  = addr10;
    msgs[1].flags = I2C_M_TEN | I2C_M_RD; /* 10-бітна адреса, R/W = 1 */
    msgs[1].len   = 2;
    msgs[1].buf   = buffer;

    rdwr.msgs  = msgs;
    rdwr.nmsgs = 2;

    if (ioctl(fd, I2C_RDWR, &rdwr) < 0) {
        return -1;
    }

    *val_high = buffer[0];
    *val_low  = buffer[1];
    return 0;
}
