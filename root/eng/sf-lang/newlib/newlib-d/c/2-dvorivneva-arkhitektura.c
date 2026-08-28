/* Типова реалізація з libnosys */
#include <errno.h>
#undef errno
extern int errno;

__attribute__((weak))
int _write(int fd, const char *buf, int nbytes) {
    (void)fd;
    (void)buf;
    (void)nbytes;
    errno = ENOSYS; /* Функцію не реалізовано */
    return -1;
}
