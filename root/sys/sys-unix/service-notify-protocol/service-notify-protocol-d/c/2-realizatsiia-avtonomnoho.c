#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>

int custom_sd_notify(const char *state) {
    if (!state) return -1;

    const char *socket_path = getenv("NOTIFY_SOCKET");
    if (!socket_path) return 0; // NOTIFY_SOCKET не задано

    int fd = socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) return -1;

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;

    size_t path_len = strlen(socket_path);
    if (socket_path[0] == '@') {
        // Абстрактний простір імен: перший байт \0
        addr.sun_path[0] = '\0';
        if (path_len >= sizeof(addr.sun_path)) path_len = sizeof(addr.sun_path) - 1;
        memcpy(addr.sun_path + 1, socket_path + 1, path_len - 1);
    } else {
        if (path_len >= sizeof(addr.sun_path)) path_len = sizeof(addr.sun_path) - 1;
        memcpy(addr.sun_path, socket_path, path_len);
    }

    socklen_t addr_len = sizeof(sa_family_t) + path_len;
    ssize_t sent = sendto(fd, state, strlen(state), MSG_NOSIGNAL,
                          (struct sockaddr *)&addr, addr_len);

    close(fd);
    return (sent > 0) ? 1 : -1;
}

int main(void) {
    sleep(1);
    custom_sd_notify("READY=1\nSTATUS=Zero-dependency C notifier online.");
    return 0;
}
