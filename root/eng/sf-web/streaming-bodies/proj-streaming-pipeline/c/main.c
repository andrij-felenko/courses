#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/types.h>

#define BUFFER_SIZE (64 * 1024)

/* Надійне відправлення всього буфера крізь сокет з урахуванням часткових записів */
static int send_all(int fd, const char *buf, size_t len) {
    size_t total_sent = 0;
    while (total_sent < len) {
        ssize_t n = send(fd, buf + total_sent, len - total_sent, 0);
        if (n > 0) {
            total_sent += (size_t)n;
            continue;
        }
        if (n < 0) {
            if (errno == EINTR) continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                struct pollfd pfd = { .fd = fd, .events = POLLOUT, .revents = 0 };
                int res = poll(&pfd, 1, 5000);
                if (res > 0 && (pfd.revents & POLLOUT)) continue;
                return -1;
            }
            return -1;
        }
        return -1; /* З'єднання закрито віддаленим вузлом */
    }
    return 0;
}

/* Перенаправлення потоку між сокетами з фіксованим буфером O(1) пам'яті */
int pipe_stream_fixed_buffer(int src_fd, int dst_fd, size_t *out_bytes) {
    char *buffer = malloc(BUFFER_SIZE);
    if (!buffer) return -1;

    size_t total_transferred = 0;
    int status = 0;

    for (;;) {
        ssize_t bytes_read = recv(src_fd, buffer, BUFFER_SIZE, 0);
        if (bytes_read > 0) {
            if (send_all(dst_fd, buffer, (size_t)bytes_read) != 0) {
                status = -2; /* Помилка запису у вихідний сокет */
                break;
            }
            total_transferred += (size_t)bytes_read;
            continue;
        }
        if (bytes_read == 0) {
            /* Досягнуто кінця вхідного потоку (EOF) */
            status = 0;
            break;
        }
        if (errno == EINTR) continue;
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            struct pollfd pfd = { .fd = src_fd, .events = POLLIN, .revents = 0 };
            int res = poll(&pfd, 1, 5000);
            if (res > 0 && (pfd.revents & POLLIN)) continue;
            status = -3; /* Таймаут читання */
            break;
        }
        status = -1; /* Помилка читання */
        break;
    }

    free(buffer);
    if (out_bytes) *out_bytes = total_transferred;
    return status;
}
