#define _GNU_SOURCE
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

/* Виробник: наповнити й заморозити. Повертає дескриптор або -1. */
int sealed_blob(const void *data, size_t len)
{
    int e, fd = memfd_create("payload", MFD_CLOEXEC | MFD_ALLOW_SEALING);
    if (fd < 0)
        return -1;

    if (ftruncate(fd, (off_t)len) < 0)
        goto fail;

    void *p = mmap(NULL, len, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (p == MAP_FAILED)
        goto fail;
    memcpy(p, data, len);
    munmap(p, len);                 /* доки воно живе, F_SEAL_WRITE дасть EBUSY */

    if (fcntl(fd, F_ADD_SEALS, F_SEAL_SHRINK | F_SEAL_GROW
                             | F_SEAL_WRITE  | F_SEAL_SEAL) < 0)
        goto fail;

    return fd;

fail:
    e = errno;
    close(fd);
    errno = e;
    return -1;
}

/* Отримувач: вірити лише ядру. 0 — пломби на місці. */
int blob_is_frozen(int fd)
{
    const int need = F_SEAL_SHRINK | F_SEAL_WRITE;
    int seals = fcntl(fd, F_GET_SEALS);

    if (seals < 0)                  /* EINVAL — це не memfd */
        return -1;
    return (seals & need) == need ? 0 : -1;
}
