#include <fcntl.h>
#include <unistd.h>

int persist_critical_data(int fd, const void *buf, size_t len) {
    /* 1. Запис у Page Cache */
    ssize_t w = write(fd, buf, len);
    if (w < 0 || (size_t)w != len) {
        return -1;
    }

    /* 2. Примусове виштовхування крізь усі 7 рівнів до NAND Flash */
    if (fdatasync(fd) < 0) {
        return -1;
    }

    return 0;
}
