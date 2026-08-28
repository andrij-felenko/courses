/* io_stream.c — C-реалізація з умовною компіляцією на базі config.h */
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

int open_nonblocking_stream(const char *path) {
#if defined(HAVE_O_NONBLOCK) && defined(O_CLOEXEC)
    /* Сучасне ядро Linux: відкриття з прапорцями за один системний виклик */
    int fd = open(path, O_RDONLY | O_NONBLOCK | O_CLOEXEC);
    if (fd < 0) {
        return -1;
    }
    return fd;
#else
    /* Застарілі POSIX-системи: fallback через два системні виклики */
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return -1;
    }
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1 || fcntl(fd, F_SETFL, flags | O_NONBLOCK) == -1) {
        close(fd);
        return -1;
    }
    return fd;
#endif
}
