#define _XOPEN_SOURCE 600
#include <fcntl.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <unistd.h>

/* Повертає дескриптор ведучого кінця; ім'я підлеглого кладе в name. */
int pty_open(char *name, size_t n) {
    int m = posix_openpt(O_RDWR | O_NOCTTY | O_CLOEXEC);
    if (m < 0) return -1;
    if (grantpt(m) < 0 || unlockpt(m) < 0) goto fail;
    if (ptsname_r(m, name, n) != 0) goto fail;
    return m;
fail:
    close(m);
    return -1;
}
