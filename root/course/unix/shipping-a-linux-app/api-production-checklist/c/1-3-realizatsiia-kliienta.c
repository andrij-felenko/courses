#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <stddef.h>

/* Автономна відправка рядка стану в systemd через Unix-сокет */
int standalone_sd_notify(const char *state) {
    if (!state || !*state) {
        return 0;
    }

    const char *socket_path = getenv("NOTIFY_SOCKET");
    if (!socket_path) {
        return 0; /* Процес запущено не під керуванням systemd */
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;

    size_t path_len = strlen(socket_path);
    if (path_len >= sizeof(addr.sun_path)) {
        errno = ENAMETOOLONG;
        return -1;
    }

    /* Підтримка абстрактних сокетів Linux (починаються з символу @) */
    if (socket_path[0] == '@') {
        addr.sun_path[0] = '\0';
        memcpy(&addr.sun_path[1], &socket_path[1], path_len - 1);
    } else {
        memcpy(addr.sun_path, socket_path, path_len);
    }

    int fd = socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) {
        return -1;
    }

    socklen_t addr_len = offsetof(struct sockaddr_un, sun_path) + path_len;
    ssize_t written = sendto(fd, state, strlen(state), MSG_NOSIGNAL,
                             (struct sockaddr *)&addr, addr_len);

    int saved_errno = errno;
    close(fd);

    if (written < 0) {
        errno = saved_errno;
        return -1;
    }

    return 1;
}
