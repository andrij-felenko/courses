#include <poll.h>

struct pollfd fds[1];
fds[0].fd = sockfd;
fds[0].events = POLLIN | POLLPRI;

int ret = poll(fds, 1, -1);
if (ret > 0) {
    if (fds[0].revents & POLLPRI) {
        char oob_byte;
        recv(sockfd, &oob_byte, 1, MSG_OOB);
        printf("Отримано OOB через poll(POLLPRI): %c\n", oob_byte);
    }
    if (fds[0].revents & POLLIN) {
        // Читання звичайних даних
    }
}
