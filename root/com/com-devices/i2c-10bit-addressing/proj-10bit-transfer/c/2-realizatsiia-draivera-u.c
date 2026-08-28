#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

/* Перевірка підтримки 10-бітної адресації апаратним адаптером */
int i2c_check_10bit_support(int fd) {
    unsigned long funcs = 0;
    if (ioctl(fd, I2C_FUNCS, &funcs) < 0) {
        return -1;
    }
    if (!(funcs & I2C_FUNC_10BIT_ADDR)) {
        errno = EOPNOTSUPP;
        return -1;
    }
    if (!(funcs & I2C_FUNC_I2C)) {
        errno = EOPNOTSUPP;
        return -1;
    }
    return 0;
}

/* Запис буфера даних у 10-бітний пристрій */
int i2c_10bit_write(int fd, uint16_t addr10, const uint8_t *data, size_len) {
    struct i2c_msg msg;
    struct i2c_rdwr_ioctl_data rdwr;

    memset(&msg, 0, sizeof(msg));
    msg.addr  = addr10;
    msg.flags = I2C_M_TEN;             /* Прапорець 10-бітної адресації */
    msg.len   = (uint16_t)data_len;
    msg.buf   = (uint8_t *)data;

    rdwr.msgs  = &msg;
    rdwr.nmsgs = 1;

    if (ioctl(fd, I2C_RDWR, &rdwr) < 0) {
        return -1;
    }
    return 0;
}

/* Зчитування даних із регістра 10-бітного пристрою (Write Register Address + Repeated START + Read Data) */
int i2c_10bit_read_reg(int fd, uint16_t addr10, uint8_t reg_addr, uint8_t *out_buf, size_t len) {
    struct i2c_msg msgs[2];
    struct i2c_rdwr_ioctl_data rdwr;

    memset(msgs, 0, sizeof(msgs));

    /* Повідомлення 1: Запис адреси внутрішнього регістра */
    msgs[0].addr  = addr10;
    msgs[0].flags = I2C_M_TEN;         /* 10-бітний запис (R/W = 0) */
    msgs[0].len   = 1;
    msgs[0].buf   = &reg_addr;

    /* Повідомлення 2: Зчитування результату через Repeated START */
    msgs[1].addr  = addr10;
    msgs[1].flags = I2C_M_TEN | I2C_M_RD; /* 10-бітне читання (R/W = 1) */
    msgs[1].len   = (uint16_t)len;
    msgs[1].buf   = out_buf;

    rdwr.msgs  = msgs;
    rdwr.nmsgs = 2;

    if (ioctl(fd, I2C_RDWR, &rdwr) < 0) {
        return -1;
    }
    return 0;
}
