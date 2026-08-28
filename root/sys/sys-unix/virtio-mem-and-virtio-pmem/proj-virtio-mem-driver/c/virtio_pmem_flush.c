/* virtio_pmem_flush.c — Обробник флаш-запитів мовою C */
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>

#define VIRTIO_PMEM_REQ_TYPE_FLUSH 0

struct virtio_pmem_req {
    uint32_t type;
};

struct virtio_pmem_resp {
    int32_t status;
};

int handle_virtio_pmem_request(int backend_fd, const struct virtio_pmem_req *req, struct virtio_pmem_resp *resp) {
    if (!req || !resp || backend_fd < 0) return -1;

    if (req->type == VIRTIO_PMEM_REQ_TYPE_FLUSH) {
        /* Примусовий виклик fdatasync для гарантії запису на флеш/диск хоста */
        if (fdatasync(backend_fd) == 0) {
            resp->status = 0; /* Успіх */
            printf("[virtio-pmem host C] fdatasync успішно виконано\n");
        } else {
            resp->status = -errno; /* Збереження коду помилки I/O */
            perror("[virtio-pmem host C] fdatasync error");
        }
    } else {
        resp->status = -EINVAL; /* Невідома команда */
    }
    return 0;
}
