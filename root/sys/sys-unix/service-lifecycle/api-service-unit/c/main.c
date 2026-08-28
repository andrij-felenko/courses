#include <sys/socket.h>
#include <sys/un.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

int notify(const char *state) {
    const char *path = getenv("NOTIFY_SOCKET");
    if (!path) return 0;                      /* менеджер нас не слухає — не помилка */

    struct sockaddr_un sa = { .sun_family = AF_UNIX };
    size_t len = strlen(path);
    if (len >= sizeof sa.sun_path) return -1;
    memcpy(sa.sun_path, path, len + 1);
    if (sa.sun_path[0] == '@') sa.sun_path[0] = '\0';   /* абстрактне ім'я */

    int fd = socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) return -1;
    ssize_t n = sendto(fd, state, strlen(state), MSG_NOSIGNAL,
                       (struct sockaddr *)&sa,
                       offsetof(struct sockaddr_un, sun_path) + len);
    close(fd);
    return n < 0 ? -1 : 0;
}
