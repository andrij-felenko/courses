#include <sys/stat.h>
#include <cerrno>

extern "C" {

auto _isatty(int fd) noexcept -> int {
    if (fd >= 0 && fd <= 2) {
        return 1; // Дескриптори 0, 1, 2 є терміналом TTY
    }
    errno = EBADF;
    return 0;
}

auto _fstat(int fd, struct stat *st) noexcept -> int {
    if (fd >= 0 && fd <= 2) {
        st->st_mode = S_IFCHR; // Символьний пристрій (Character Device)
        return 0;
    }
    errno = EBADF;
    return -1;
}

} // extern "C"
