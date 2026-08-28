#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>

int main(void)
{
    int fd = openat(AT_FDCWD, "/etc/hostname", O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        fprintf(stderr, "open: %s\n", strerror(errno));
        return 1;
    }

    char buf[64];
    ssize_t n;
    do {
        n = read(fd, buf, sizeof buf);
    } while (n < 0 && errno == EINTR);   /* read повторювати можна */

    if (n < 0)
        fprintf(stderr, "read: %s\n", strerror(errno));
    else
        fwrite(buf, 1, (size_t) n, stdout);

    if (close(fd) < 0)                   /* рівно один раз, без повтору */
        fprintf(stderr, "close: %s\n", strerror(errno));
    fd = -1;

    return n < 0;
}
