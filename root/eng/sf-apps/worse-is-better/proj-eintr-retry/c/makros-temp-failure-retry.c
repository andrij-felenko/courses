#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <errno.h>

// Використання стандартного макросу glibc для безпечного відкриття файлу
int open_file_safe(const char *path) {
    int fd = TEMP_FAILURE_RETRY(open(path, O_RDONLY | O_CLOEXEC));
    if (fd == -1) {
        perror("open failed");
        return -1;
    }
    return fd;
}
