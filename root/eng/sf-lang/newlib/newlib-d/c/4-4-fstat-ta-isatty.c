#include <sys/stat.h>
#include <errno.h>

int _isatty(int fd) {
    if (fd >= 0 && fd <= 2) {
        return 1; /* Дескриптори 0, 1, 2 прив'язані до терміналу TTY */
    }
    errno = EBADF;
    return 0;
}

int _fstat(int fd, struct stat *st) {
    if (fd >= 0 && fd <= 2) {
        st->st_mode = S_IFCHR; /* Символьний пристрій (Character Device) */
        return 0;
    }
    errno = EBADF;
    return -1;
}
