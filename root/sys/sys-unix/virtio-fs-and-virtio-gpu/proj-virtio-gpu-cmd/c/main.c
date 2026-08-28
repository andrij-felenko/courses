#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>

/* Коди команд Virtio GPU */
#define VIRTIO_GPU_CMD_RESOURCE_CREATE_2D      0x0101
#define VIRTIO_GPU_CMD_RESOURCE_UNREF          0x0102
#define VIRTIO_GPU_CMD_TRANSFER_TO_HOST_2D     0x0105
#define VIRTIO_GPU_CMD_RESOURCE_FLUSH          0x0104
#define VIRTIO_GPU_CMD_RESOURCE_ATTACH_BACKING 0x0106
#define VIRTIO_GPU_CMD_RESOURCE_DETACH_BACKING 0x0107

/* Коди відповідей Virtio GPU */
#define VIRTIO_GPU_RESP_OK_NODATA              0x1100
#define VIRTIO_GPU_RESP_ERR_UNSPEC             0x1200
#define VIRTIO_GPU_RESP_ERR_OUT_OF_MEMORY      0x1201
#define VIRTIO_GPU_RESP_ERR_INVALID_RESOURCE_ID 0x1203

/* Формати пікселів */
#define VIRTIO_GPU_FORMAT_B8G8R8A8_UNORM       1

/* Заголовок управління Virtio GPU */
struct virtio_gpu_ctrl_hdr {
    uint32_t type;
    uint32_t flags;
    uint64_t fence_id;
    uint32_t ctx_id;
    uint8_t  ring_idx;
    uint8_t  padding[3];
};

/* Прямокутник кадрового буфера */
struct virtio_gpu_rect {
    uint32_t x;
    uint32_t y;
    uint32_t width;
    uint32_t height;
};

/* Структура створення 2D-ресурсу */
struct virtio_gpu_resource_create_2d {
    struct virtio_gpu_ctrl_hdr hdr;
    uint32_t resource_id;
    uint32_t format;
    uint32_t width;
    uint32_t height;
};

/* Елемент опису фізичної сторінки гостя */
struct virtio_gpu_mem_entry {
    uint64_t addr;
    uint32_t length;
    uint32_t padding;
};

/* Структура прив'язки сторінок пам'яті */
struct virtio_gpu_resource_attach_backing {
    struct virtio_gpu_ctrl_hdr hdr;
    uint32_t resource_id;
    uint32_t nr_entries;
};

/* Структура передачі піксельних даних на хост */
struct virtio_gpu_transfer_to_host_2d {
    struct virtio_gpu_ctrl_hdr hdr;
    struct virtio_gpu_rect r;
    uint64_t offset;
    uint32_t resource_id;
    uint32_t padding;
};

/* Структура примусового скидання кадрів (Flush) */
struct virtio_gpu_resource_flush {
    struct virtio_gpu_ctrl_hdr hdr;
    struct virtio_gpu_rect r;
    uint32_t resource_id;
    uint32_t padding;
};

/* Структура видалення ресурсу */
struct virtio_gpu_resource_unref {
    struct virtio_gpu_ctrl_hdr hdr;
    uint32_t resource_id;
    uint32_t padding;
};

/**
 * virtio_gpu_submit_create_2d - Формує та надсилає команду створення 2D ресурсу
 */
int virtio_gpu_submit_create_2d(uint32_t res_id, uint32_t width, uint32_t height,
                                struct virtio_gpu_ctrl_hdr *resp_out)
{
    if (!resp_out || width == 0 || height == 0 || res_id == 0) {
        return -EINVAL;
    }

    struct virtio_gpu_resource_create_2d cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.hdr.type = VIRTIO_GPU_CMD_RESOURCE_CREATE_2D;
    cmd.resource_id = res_id;
    cmd.format = VIRTIO_GPU_FORMAT_B8G8R8A8_UNORM;
    cmd.width = width;
    cmd.height = height;

    /* Імітація обробки гіпервізором */
    resp_out->type = VIRTIO_GPU_RESP_OK_NODATA;
    resp_out->flags = 0;
    resp_out->fence_id = 0;
    resp_out->ctx_id = 0;

    return 0;
}

/**
 * virtio_gpu_submit_attach_backing - Прив'язує сторінки RAM гостя до ресурсу
 */
int virtio_gpu_submit_attach_backing(uint32_t res_id,
                                      const struct virtio_gpu_mem_entry *entries,
                                      uint32_t nr_entries,
                                      struct virtio_gpu_ctrl_hdr *resp_out)
{
    if (!resp_out || !entries || nr_entries == 0 || res_id == 0) {
        return -EINVAL;
    }

    struct virtio_gpu_resource_attach_backing cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.hdr.type = VIRTIO_GPU_CMD_RESOURCE_ATTACH_BACKING;
    cmd.resource_id = res_id;
    cmd.nr_entries = nr_entries;

    /*
     * У реальному драйвері за командою cmd у дескрипторний ланцюжок
     * додається масив entries розміром nr_entries * sizeof(struct virtio_gpu_mem_entry).
     */

    resp_out->type = VIRTIO_GPU_RESP_OK_NODATA;
    return 0;
}

/**
 * virtio_gpu_submit_transfer_2d - Надсилає команду копіювання пікселів на хост
 */
int virtio_gpu_submit_transfer_2d(uint32_t res_id, uint64_t offset,
                                   uint32_t x, uint32_t y,
                                   uint32_t width, uint32_t height,
                                   struct virtio_gpu_ctrl_hdr *resp_out)
{
    if (!resp_out || res_id == 0 || width == 0 || height == 0) {
        return -EINVAL;
    }

    struct virtio_gpu_transfer_to_host_2d cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.hdr.type = VIRTIO_GPU_CMD_TRANSFER_TO_HOST_2D;
    cmd.r.x = x;
    cmd.r.y = y;
    cmd.r.width = width;
    cmd.r.height = height;
    cmd.offset = offset;
    cmd.resource_id = res_id;

    resp_out->type = VIRTIO_GPU_RESP_OK_NODATA;
    return 0;
}

/**
 * virtio_gpu_submit_flush - Надсилає команду оновлення області ресурсу на моніторі
 */
int virtio_gpu_submit_flush(uint32_t res_id, uint32_t x, uint32_t y,
                            uint32_t width, uint32_t height,
                            struct virtio_gpu_ctrl_hdr *resp_out)
{
    if (!resp_out || res_id == 0) {
        return -EINVAL;
    }

    struct virtio_gpu_resource_flush cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.hdr.type = VIRTIO_GPU_CMD_RESOURCE_FLUSH;
    cmd.r.x = x;
    cmd.r.y = y;
    cmd.r.width = width;
    cmd.r.height = height;
    cmd.resource_id = res_id;

    resp_out->type = VIRTIO_GPU_RESP_OK_NODATA;
    return 0;
}

/**
 * virtio_gpu_submit_unref - Видаляє ресурс на хості
 */
int virtio_gpu_submit_unref(uint32_t res_id, struct virtio_gpu_ctrl_hdr *resp_out)
{
    if (!resp_out || res_id == 0) {
        return -EINVAL;
    }

    struct virtio_gpu_resource_unref cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.hdr.type = VIRTIO_GPU_CMD_RESOURCE_UNREF;
    cmd.resource_id = res_id;

    resp_out->type = VIRTIO_GPU_RESP_OK_NODATA;
    return 0;
}
