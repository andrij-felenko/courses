/* Читання чужого середовища через /proc/$PID/environ мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

void dump_process_environ(pid_t target_pid) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/environ", target_pid);

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        perror("open /proc/$PID/environ");
        return;
    }

    char buf[4096];
    ssize_t bytes_read;
    while ((bytes_read = read(fd, buf, sizeof(buf))) > 0) {
        for (ssize_t i = 0; i < bytes_read; ++i) {
            if (buf[i] == '\0') {
                putchar('\n');
            } else {
                putchar(buf[i]);
            }
        }
    }
    close(fd);
}
