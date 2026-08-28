#include <pthread.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

typedef struct {
    int fd;
    pthread_mutex_t lock;
} i2c_bus_context_t;

int i2c_bus_init(i2c_bus_context_t *ctx, int fd) {
    ctx->fd = fd;
    return pthread_mutex_init(&ctx->lock, NULL);
}

void i2c_bus_destroy(i2c_bus_context_t *ctx) {
    pthread_mutex_destroy(&ctx->lock);
}

int i2c_bus_transfer_locked(i2c_bus_context_t *ctx, struct i2c_msg *msgs, int nmsgs) {
    pthread_mutex_lock(&ctx->lock);

    struct i2c_rdwr_ioctl_data rdwr;
    rdwr.msgs  = msgs;
    rdwr.nmsgs = nmsgs;

    int ret = ioctl(ctx->fd, I2C_RDWR, &rdwr);
    pthread_mutex_unlock(&ctx->lock);

    return ret;
}
