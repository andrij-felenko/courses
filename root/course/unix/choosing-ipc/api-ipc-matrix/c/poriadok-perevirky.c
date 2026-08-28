#define _GNU_SOURCE
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/fcntl.h>

int create_sealed_buffer(size_t size) {
    int fd = memfd_create("secure_shm", MFD_CLOEXEC | MFD_ALLOW_SEALING);
    if (fd < 0) return -1;

    if (ftruncate(fd, size) < 0) {
        close(fd);
        return -1;
    }

    /* Накладання печаток незмінності розміру та структури */
    if (fcntl(fd, F_ADD_SEALS, F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_SEAL) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}
