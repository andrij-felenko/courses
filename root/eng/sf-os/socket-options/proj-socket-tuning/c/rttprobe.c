/* rttprobe.c — збірка: cc -std=c11 -Wall -Wextra -O2 rttprobe.c -o rttprobe */
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

#define HDR    8      /* «заголовок» повідомлення */
#define BODY 200      /* тіло: менше за сегмент, інакше притримування не діє */
#define WARMUP 200    /* обміни, які викидаємо; чому — нижче */

static void histogram(double *v, int n);   /* означено нижче */

static double now_us(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e6 + ts.tv_nsec / 1e3;
}

/* recv віддає СКІЛЬКИ Є, а не скільки просили — це не помилка, а норма. */
static int read_exact(int fd, void *buf, size_t need)
{
    size_t got = 0;
    while (got < need) {
        ssize_t n = recv(fd, (char *)buf + got, need - got, 0);
        if (n == 0) return -1;                       /* інший бік закрив */
        if (n < 0) { if (errno == EINTR) continue; return -1; }
        got += (size_t)n;
    }
    return 0;
}

static void run_server(int port)
{
    int ls = socket(AF_INET, SOCK_STREAM, 0);
    int on = 1;
    setsockopt(ls, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);   /* ДО bind */

    struct sockaddr_in a = { .sin_family = AF_INET,
                             .sin_addr.s_addr = htonl(INADDR_ANY),
                             .sin_port = htons((uint16_t)port) };
    if (bind(ls, (struct sockaddr *)&a, sizeof a) < 0) { perror("bind"); return; }
    listen(ls, 4);

    for (;;) {
        int cs = accept(ls, NULL, NULL);
        if (cs < 0) continue;
        unsigned char hdr[HDR], body[BODY];
        /* Читаємо заголовок, тоді тіло — саме через цю паузу сервер і не
           відповідає, доки не прийде другий запис клієнта. */
        while (read_exact(cs, hdr, HDR) == 0 && read_exact(cs, body, BODY) == 0)
            if (send(cs, hdr, HDR, 0) != (ssize_t)HDR) break;  /* відповідь одним записом */
        close(cs);
    }
}
