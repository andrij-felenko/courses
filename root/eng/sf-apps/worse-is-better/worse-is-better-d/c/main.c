#include <unistd.h>
#include <errno.h>

// Класичний патерн Unix: прикладний код бере на себе складність перезапуску
ssize_t robust_read(int fd, void *buf, size_t count) {
    ssize_t result;
    do {
        result = read(fd, buf, count);
    } while (result == -1 && errno == EINTR);
    return result;
}
