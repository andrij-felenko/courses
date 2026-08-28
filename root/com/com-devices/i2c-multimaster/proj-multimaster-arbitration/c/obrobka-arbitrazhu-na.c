#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

/* Обробка втрати арбітражу I2C у Linux (C) */
int linux_i2c_transfer_with_retry(int fd, struct i2c_msg *msgs, int num_msgs, int max_retries) {
    struct i2c_rdwr_ioctl_data packets = {
        .msgs = msgs,
        .nmsgs = num_msgs
    };

    for (int attempt = 0; attempt < max_retries; ++attempt) {
        if (ioctl(fd, I2C_RDWR, &packets) >= 0) {
            return 0; /* Успішна передача */
        }

        if (errno == EAGAIN || errno == EBUSY) {
            /* Втрата арбітражу: робимо випадковий мікросекундний відступ */
            uint32_t delay_us = 100 + (uint32_t)(rand() % 500);
            usleep(delay_us);
        } else {
            /* Фатальна апаратна помилка (наприклад, NACK) */
            return -1;
        }
    }
    errno = ETIMEDOUT;
    return -1;
}
