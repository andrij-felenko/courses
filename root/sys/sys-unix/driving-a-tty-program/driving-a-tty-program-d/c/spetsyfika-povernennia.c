#include <errno.h>
#include <stdio.h>
#include <unistd.h>

int drain_master_fd(int master_fd, char *buf, size_t cap) {
    for (;;) {
        ssize_t n = read(master_fd, buf, cap);
        if (n < 0) {
            if (errno == EIO) {
                /* Нормальне завершення: дочірній процес закрив PTY в Linux */
                return 0;
            }
            if (errno == EINTR) {
                continue;
            }
            perror("read master_fd");
            return -1;
        }
        if (n == 0) {
            /* Кінець файлу (трапляється в BSD/macOS) */
            return 0;
        }
        write(STDOUT_FILENO, buf, (size_t)n);
    }
}
