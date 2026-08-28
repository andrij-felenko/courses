#include <systemd/sd-daemon.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <string.h>

/* Повертає номер переданого сокета з іменем name або -1. */
int listen_fd_by_name(const char *name)
{
    char **names = NULL;
    int fd = -1;
    int n = sd_listen_fds_with_names(1, &names);   /* 1 — прибрати змінні з оточення */

    if (n <= 0)
        return -1;                                 /* нам нічого не передавали */

    for (int i = 0; i < n; i++) {
        if (fd < 0 && strcmp(names[i], name) == 0)
            fd = SD_LISTEN_FDS_START + i;          /* перше влучання, імена не унікальні */
        free(names[i]);
    }
    free(names);

    /* Потоковий IP-сокет, що вже слухає; порт не перевіряємо. */
    if (fd >= 0 && sd_is_socket_inet(fd, AF_UNSPEC, SOCK_STREAM, 1, 0) <= 0)
        return -1;

    return fd;
}
