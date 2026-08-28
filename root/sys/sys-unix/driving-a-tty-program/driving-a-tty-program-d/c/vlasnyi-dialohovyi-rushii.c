#define _XOPEN_SOURCE 600
#include <errno.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

int expect_prompt_and_reply(int master_fd, const char *prompt_pattern, const char *reply, int timeout_ms) {
    char buf[1024];
    size_t accumulated = 0;
    memset(buf, 0, sizeof(buf));

    struct pollfd pfd = {
        .fd = master_fd,
        .events = POLLIN | POLLHUP,
        .revents = 0
    };

    for (;;) {
        int ret = poll(&pfd, 1, timeout_ms);
        if (ret < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (ret == 0) {
            /* Перевищено ліміт часу очікування підказки */
            return -2;
        }

        if (pfd.revents & (POLLIN | POLLHUP)) {
            ssize_t n = read(master_fd, buf + accumulated, sizeof(buf) - accumulated - 1);
            if (n < 0) {
                if (errno == EINTR) continue;
                if (errno == EIO) break; /* Кінець виводу в Linux */
                return -1;
            }
            if (n == 0) break;

            accumulated += (size_t)n;
            buf[accumulated] = '\0';

            /* Перевіряємо наявність очікуваного тексту */
            if (strstr(buf, prompt_pattern) != NULL) {
                /* Надсилаємо відповідь з поверненням каретки */
                size_t reply_len = strlen(reply);
                if (write(master_fd, reply, reply_len) != (ssize_t)reply_len) {
                    return -1;
                }
                if (write(master_fd, "\r", 1) != 1) {
                    return -1;
                }
                return 0; /* Успішно знайдено підказку та надіслано відповідь */
            }

            if (accumulated >= sizeof(buf) - 1) {
                /* Зсуваємо буфер у разі переповнення */
                memmove(buf, buf + accumulated / 2, accumulated - accumulated / 2);
                accumulated -= accumulated / 2;
                buf[accumulated] = '\0';
            }
        }
    }

    return -3; /* Потік завершився до появи підказки */
}
