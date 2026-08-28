/* Блокування сигналу SIGPIPE у виклику send() у C */
#include <sys/socket.h>
#include <errno.h>

ssize_t send_safe_c(int fd, const void *buf, size_t len) {
    ssize_t res = send(fd, buf, len, MSG_NOSIGNAL);
    if (res < 0 && errno == EPIPE) {
        /* Обробка закриття сокета без аварійного виходу з програми */
    }
    return res;
}
