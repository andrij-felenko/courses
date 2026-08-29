#include "i2c_linux.h"

#include <errno.h>
#include <fcntl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <time.h>
#include <unistd.h>

bool i2c_linux_open(i2c_linux *bus, const char *path)
{
    bus->fd = open(path, O_RDWR);
    if (bus->fd < 0) {
        fprintf(stderr, "не вдалося відкрити %s: %s\n", path, strerror(errno));
        return false;
    }
    return true;
}

void i2c_linux_close(i2c_linux *bus)
{
    if (bus->fd >= 0) {
        close(bus->fd);
        bus->fd = -1;
    }
}

/* I2C_RDWR, а не звичайні read/write: він дозволяє задати адресу для кожного
 * повідомлення окремо — саме це потрібно для запису на адресу 0x00, якою
 * драйвер виготовляє імпульс пробудження. */
static bool xfer(int fd, uint8_t addr7, uint8_t *buf, size_t len, uint16_t flags)
{
    struct i2c_msg msg = {
        .addr = addr7,
        .flags = flags,
        .len = (uint16_t)len,
        .buf = buf,
    };
    struct i2c_rdwr_ioctl_data req = {
        .msgs = &msg,
        .nmsgs = 1,
    };

    while (ioctl(fd, I2C_RDWR, &req) < 0) {
        if (errno == EINTR) {
            continue;
        }
        /* ENXIO/EREMOTEIO — пристрій не підтвердив адресу. Для крипточипа це
         * штатна відповідь «ще рахую», тож галасу тут не робимо. */
        return false;
    }
    return true;
}

static bool hal_write(void *ctx, uint8_t addr7, const uint8_t *buf, size_t len)
{
    i2c_linux *bus = (i2c_linux *)ctx;
    uint8_t tmp[72];

    if (len > sizeof tmp) {
        return false;
    }
    memcpy(tmp, buf, len); /* ioctl бере не-const покажчик */
    return xfer(bus->fd, addr7, tmp, len, 0);
}

static bool hal_read(void *ctx, uint8_t addr7, uint8_t *buf, size_t len)
{
    i2c_linux *bus = (i2c_linux *)ctx;
    return xfer(bus->fd, addr7, buf, len, I2C_M_RD);
}

static void hal_delay_ms(void *ctx, uint32_t ms)
{
    (void)ctx;
    struct timespec req = {
        .tv_sec = (time_t)(ms / 1000u),
        .tv_nsec = (long)(ms % 1000u) * 1000000L,
    };
    struct timespec rem;

    while (nanosleep(&req, &rem) < 0 && errno == EINTR) {
        req = rem; /* сигнал не має вкорочувати паузу виконання команди */
    }
}

atecc_hal i2c_linux_hal(i2c_linux *bus)
{
    atecc_hal hal = {
        .write = hal_write,
        .read = hal_read,
        .delay_ms = hal_delay_ms,
        .ctx = bus,
    };
    return hal;
}
