#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <fcntl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>
#include <string.h>
#include <sys/ioctl.h>
#include <time.h>
#include <unistd.h>

#include "linux_i2c.h"

/* Найдовший запис драйвера — один байт адреси регістру плюс дані. */
#define LINUX_I2C_WRITE_MAX 32u

int linux_i2c_open(linux_i2c_bus_t *bus, const char *device_path)
{
    if (bus == NULL || device_path == NULL) {
        return -EINVAL;
    }

    bus->fd = open(device_path, O_RDWR | O_CLOEXEC);
    if (bus->fd < 0) {
        return -errno;
    }
    return 0;
}

void linux_i2c_close(linux_i2c_bus_t *bus)
{
    if (bus != NULL && bus->fd >= 0) {
        close(bus->fd);
        bus->fd = -1;
    }
}

/* Читання: адреса регістру йде окремим повідомленням БЕЗ умови STOP, далі
 * повторний старт і читання. Саме це й дає ioctl(I2C_RDWR) з двома msg:
 * ядро формує Repeated Start між ними. Поле addr — семибітне, зсув на біт
 * напрямку робить контролер, а не ми (класична пастка 0x19 проти 0x32). */
static int32_t linux_i2c_read(void *user_ctx, uint8_t dev_addr,
                              uint8_t reg, uint8_t *data, uint16_t len)
{
    linux_i2c_bus_t *bus = (linux_i2c_bus_t *)user_ctx;
    if (bus == NULL || bus->fd < 0) {
        return -1;
    }

    uint8_t reg_addr = reg;
    struct i2c_msg msgs[2];
    msgs[0].addr = dev_addr;
    msgs[0].flags = 0;
    msgs[0].len = 1;
    msgs[0].buf = &reg_addr;

    msgs[1].addr = dev_addr;
    msgs[1].flags = I2C_M_RD;
    msgs[1].len = len;
    msgs[1].buf = data;

    struct i2c_rdwr_ioctl_data xfer;
    xfer.msgs = msgs;
    xfer.nmsgs = 2;

    if (ioctl(bus->fd, I2C_RDWR, &xfer) < 0) {
        return -1; /* NACK, зайнята шина, від'єднаний пристрій */
    }
    return 0;
}

static int32_t linux_i2c_write(void *user_ctx, uint8_t dev_addr,
                               uint8_t reg, const uint8_t *data, uint16_t len)
{
    linux_i2c_bus_t *bus = (linux_i2c_bus_t *)user_ctx;
    if (bus == NULL || bus->fd < 0) {
        return -1;
    }
    if (len + 1u > LINUX_I2C_WRITE_MAX) {
        return -1;
    }

    uint8_t frame[LINUX_I2C_WRITE_MAX];
    frame[0] = reg;
    memcpy(&frame[1], data, len);

    struct i2c_msg msg;
    msg.addr = dev_addr;
    msg.flags = 0;
    msg.len = (uint16_t)(len + 1u);
    msg.buf = frame;

    struct i2c_rdwr_ioctl_data xfer;
    xfer.msgs = &msg;
    xfer.nmsgs = 1;

    if (ioctl(bus->fd, I2C_RDWR, &xfer) < 0) {
        return -1;
    }
    return 0;
}

static void linux_delay_ms(uint32_t ms)
{
    struct timespec req;
    req.tv_sec = (time_t)(ms / 1000u);
    req.tv_nsec = (long)(ms % 1000u) * 1000000L;

    /* nanosleep уміє повернутися раніше через сигнал — досипаємо залишок. */
    struct timespec rem;
    while (nanosleep(&req, &rem) != 0 && errno == EINTR) {
        req = rem;
    }
}

static const chip_bus_ops_t g_linux_i2c_ops = {
    .read = linux_i2c_read,
    .write = linux_i2c_write,
    .delay_ms = linux_delay_ms
};

const chip_bus_ops_t *linux_i2c_ops(void)
{
    return &g_linux_i2c_ops;
}
