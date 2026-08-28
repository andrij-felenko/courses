#include <ublksrv.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#define RAMDISK_SIZE (64 * 1024 * 1024) // 64 MiB

struct ramdisk_ctx {
    char *data;
};

static int ramdisk_handle_io(const struct ublksrv_queue *q,
                             const struct ublk_io_data *data)
{
    struct ramdisk_ctx *ctx = (struct ramdisk_ctx *)ublksrv_get_queue_app_data(q);
    const struct ublksrv_io_desc *desc = data->desc;

    uint32_t op = ublksrv_get_op(desc);
    uint64_t sector = ublksrv_get_sector(desc);
    uint32_t nr_bytes = ublksrv_get_nr_bytes(desc);
    uint64_t offset = sector << 9;

    void *buf = ublksrv_get_io_buf(q, data);

    if (offset + nr_bytes > RAMDISK_SIZE) {
        ublksrv_complete_io(q, data, -EIO);
        return 0;
    }

    if (op == UBLK_IO_OP_READ) {
        memcpy(buf, ctx->data + offset, nr_bytes);
    } else if (op == UBLK_IO_OP_WRITE) {
        memcpy(ctx->data + offset, buf, nr_bytes);
    }

    ublksrv_complete_io(q, data, nr_bytes);
    return 0;
}

int main(int argc, char *argv[])
{
    struct ramdisk_ctx ctx;
    ctx.data = (char *)calloc(1, RAMDISK_SIZE);
    if (!ctx.data) {
        perror("calloc");
        return 1;
    }

    struct ublksrv_dev *dev = ublksrv_dev_init(0, ramdisk_handle_io, &ctx);
    if (!dev) {
        fprintf(stderr, "Помилка ініціалізації ublk пристрою\n");
        free(ctx.data);
        return 1;
    }

    printf("ublk RAM-диск успішно створено, розмір: %d MiB\n", RAMDISK_SIZE / (1024 * 1024));
    ublksrv_start_dev(dev);

    ublksrv_dev_deinit(dev);
    free(ctx.data);
    return 0;
}
