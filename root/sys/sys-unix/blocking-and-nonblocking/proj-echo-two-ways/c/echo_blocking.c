/* echo_blocking.c — потік на з'єднання, усі виклики блокуючі.
 * gcc -O2 -Wall -Wextra -pthread -o echo_blocking echo_blocking.c
 */
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <pthread.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define PORT      9000
#define MAX_BODY  (64u * 1024u)

/* Читає рівно n байтів. 1 — прочитано, 0 — інший бік закрив, -1 — помилка. */
static int read_full(int fd, void *buf, size_t n)
{
    char *p = buf;
    while (n > 0) {
        ssize_t k = read(fd, p, n);
        if (k == 0) return 0;
        if (k < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        p += k;
        n -= (size_t)k;
    }
    return 1;
}

/* Пише рівно n байтів. 1 — записано, -1 — помилка. */
static int write_full(int fd, const void *buf, size_t n)
{
    const char *p = buf;
    while (n > 0) {
        ssize_t k = write(fd, p, n);
        if (k < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        p += k;
        n -= (size_t)k;
    }
    return 1;
}
