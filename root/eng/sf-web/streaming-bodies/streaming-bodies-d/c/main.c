#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <poll.h>
#include <sys/socket.h>

#define CHUNK_BUF_SIZE (64 * 1024)

/* Відправлення точної кількості байтів у сокет з урахуванням зворотного тиску */
static int write_exact(int fd, const char *buf, size_t len) {
    size_t written = 0;
    while (written < len) {
        ssize_t n = send(fd, buf + written, len - written, 0);
        if (n > 0) {
            written += (size_t)n;
            continue;
        }
        if (n < 0) {
            if (errno == EINTR) continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                struct pollfd pfd = { .fd = fd, .events = POLLOUT, .revents = 0 };
                if (poll(&pfd, 1, 5000) > 0 && (pfd.revents & POLLOUT)) continue;
                return -1;
            }
            return -1;
        }
        return -1; /* З'єднання розірвано */
    }
    return 0;
}

/* Потоковий тунель: перекачує потік між двома сокетами зі сталим використанням RAM */
int stream_pipe(int in_sock, int out_sock, size_t *transferred) {
    char *buffer = malloc(CHUNK_BUF_SIZE);
    if (!buffer) return -1;

    size_t total = 0;
    int err = 0;

    for (;;) {
        ssize_t r = recv(in_sock, buffer, CHUNK_BUF_SIZE, 0);
        if (r > 0) {
            if (write_exact(out_sock, buffer, (size_t)r) != 0) {
                err = -2;
                break;
            }
            total += (size_t)r;
            continue;
        }
        if (r == 0) break; /* Кінець вхідного потоку (EOF) */
        if (errno == EINTR) continue;
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            struct pollfd pfd = { .fd = in_sock, .events = POLLIN, .revents = 0 };
            if (poll(&pfd, 1, 5000) > 0 && (pfd.revents & POLLIN)) continue;
            err = -3;
            break;
        }
        err = -1;
        break;
    }

    free(buffer);
    if (transferred) *transferred = total;
    return err;
}
