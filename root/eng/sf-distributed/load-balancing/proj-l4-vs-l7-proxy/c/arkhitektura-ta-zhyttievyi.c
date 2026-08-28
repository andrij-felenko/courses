#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>

#define BUF_SIZE 16384

static int configure_socket(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    if (fcntl(fd, F_SETFL, flags | O_NONBLOCK) == -1) return -1;

    int one = 1;
    setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &one, sizeof(one));
    return 0;
}

/* L4 перекачування потоку байтів без інспекції вмісту */
void l4_bridge_loop(int client_fd, int backend_fd) {
    configure_socket(client_fd);
    configure_socket(backend_fd);

    struct pollfd fds[2];
    fds[0].fd = client_fd;
    fds[0].events = POLLIN;
    fds[1].fd = backend_fd;
    fds[1].events = POLLIN;

    char buf[BUF_SIZE];
    int active = 1;

    while (active) {
        int ret = poll(fds, 2, 5000);
        if (ret < 0) {
            if (errno == EINTR) continue;
            break;
        }
        if (ret == 0) continue; /* Таймаут активності */

        /* Дані від клієнта -> направляємо в бекенд */
        if (fds[0].revents & POLLIN) {
            ssize_t n = read(client_fd, buf, sizeof(buf));
            if (n > 0) {
                ssize_t written = 0;
                while (written < n) {
                    ssize_t w = write(backend_fd, buf + written, n - written);
                    if (w <= 0) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK) continue;
                        active = 0;
                        break;
                    }
                    written += w;
                }
            } else if (n == 0 || (n < 0 && errno != EAGAIN)) {
                shutdown(backend_fd, SHUT_WR);
                fds[0].events = 0;
            }
        }

        /* Дані від бекенда -> направляємо клієнту */
        if (fds[1].revents & POLLIN) {
            ssize_t n = read(backend_fd, buf, sizeof(buf));
            if (n > 0) {
                ssize_t written = 0;
                while (written < n) {
                    ssize_t w = write(client_fd, buf + written, n - written);
                    if (w <= 0) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK) continue;
                        active = 0;
                        break;
                    }
                    written += w;
                }
            } else if (n == 0 || (n < 0 && errno != EAGAIN)) {
                shutdown(client_fd, SHUT_WR);
                fds[1].events = 0;
            }
        }

        if ((fds[0].revents & (POLLERR | POLLHUP | POLLNVAL)) ||
            (fds[1].revents & (POLLERR | POLLHUP | POLLNVAL)) ||
            (fds[0].events == 0 && fds[1].events == 0)) {
            break;
        }
    }
}
