#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

int redirect_stdout_safe(const char *filename) {
    int fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
    if (fd < 0) {
        perror("open failed");
        return -1;
    }

    /* Атомарно замінюємо STDOUT_FILENO (FD 1) і ставимо O_CLOEXEC на випадок exec */
    if (dup3(fd, STDOUT_FILENO, O_CLOEXEC) < 0) {
        perror("dup3 failed");
        close(fd);
        return -1;
    }

    /* Закриваємо тимчасовий дескриптор, бо FD 1 вже вказує на файл */
    close(fd);
    return 0;
}
