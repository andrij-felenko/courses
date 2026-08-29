#include "link.h"

#include <errno.h>
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <poll.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

int link_connect(link_t *lk, const char *host, const char *port)
{
    memset(lk, 0, sizeof *lk);
    lk->fd = -1;

    struct addrinfo hints;
    memset(&hints, 0, sizeof hints);
    hints.ai_family   = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    struct addrinfo *list = NULL;
    int rc = getaddrinfo(host, port, &hints, &list);
    if (rc != 0) {
        fprintf(stderr, "[node] не розібрав адресу %s:%s — %s\n", host, port, gai_strerror(rc));
        return -1;
    }

    for (struct addrinfo *ai = list; ai != NULL; ai = ai->ai_next) {
        int fd = socket(ai->ai_family, ai->ai_socktype, ai->ai_protocol);
        if (fd < 0) {
            continue;
        }
        if (connect(fd, ai->ai_addr, ai->ai_addrlen) == 0) {
            /* Кадр — 16 байтів; накопичувати їх у Nagle означає затримку
               на керуванні, тому алгоритм вимикаємо. */
            int one = 1;
            (void)setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &one, sizeof one);
            lk->fd = fd;
            break;
        }
        close(fd);
    }
    freeaddrinfo(list);

    if (lk->fd < 0) {
        fprintf(stderr, "[node] шлюз %s:%s не відповідає — %s\n", host, port, strerror(errno));
        return -1;
    }
    return 0;
}

void link_close(link_t *lk)
{
    if (lk->fd >= 0) {
        close(lk->fd);
        lk->fd = -1;
    }
    lk->rx_len = 0;
}

int link_send_frame(link_t *lk, const uint8_t frame[FRAME_SIZE])
{
    size_t sent = 0;
    while (sent < FRAME_SIZE) {
        /* MSG_NOSIGNAL: обірваний канал має повернути помилку, а не вбити процес SIGPIPE. */
        ssize_t n = send(lk->fd, frame + sent, FRAME_SIZE - sent, MSG_NOSIGNAL);
        if (n > 0) {
            sent += (size_t)n;
            continue;
        }
        if (n < 0 && (errno == EINTR)) {
            continue;
        }
        fprintf(stderr, "[node] запис у канал обірвано — %s\n", strerror(errno));
        return -1;
    }
    return 0;
}

static void drop_front(link_t *lk, size_t count)
{
    memmove(lk->rx, lk->rx + count, lk->rx_len - count);
    lk->rx_len -= count;
}

/* Ковзне вікно: викидаємо все до першої магії, далі судимо кадр за CRC.
   1 — кадр знайдено, 0 — даних поки замало. */
static int try_extract(link_t *lk, uint8_t out[FRAME_SIZE])
{
    for (;;) {
        size_t start = 0;
        while (start < lk->rx_len && lk->rx[start] != FRAME_MAGIC) {
            start++;
        }
        if (start > 0) {
            lk->resync_drops += (uint32_t)start;
            drop_front(lk, start);
        }
        if (lk->rx_len < FRAME_SIZE) {
            return 0;
        }
        if (frame_valid(lk->rx)) {
            memcpy(out, lk->rx, FRAME_SIZE);
            drop_front(lk, FRAME_SIZE);
            return 1;
        }
        /* 0xAA трапилася всередині даних або кадр побито: крок на байт уперед. */
        lk->resync_drops++;
        drop_front(lk, 1);
    }
}

int link_read_frame(link_t *lk, uint8_t out[FRAME_SIZE], int timeout_ms)
{
    if (try_extract(lk, out) == 1) {
        return 1;
    }

    struct pollfd pfd = { .fd = lk->fd, .events = POLLIN, .revents = 0 };
    int pr = poll(&pfd, 1, timeout_ms);
    if (pr == 0) {
        return 0;
    }
    if (pr < 0) {
        if (errno == EINTR) {
            return 0;   /* сигнал — не збій каналу */
        }
        fprintf(stderr, "[node] poll упав — %s\n", strerror(errno));
        return -1;
    }

    size_t space = LINK_RX_CAP - lk->rx_len;
    if (space == 0) {
        /* Буфер повний, а кадру нема: у ньому самé сміття — рухаємо вікно. */
        lk->resync_drops++;
        drop_front(lk, 1);
        space = 1;
    }

    ssize_t n = recv(lk->fd, lk->rx + lk->rx_len, space, 0);
    if (n == 0) {
        fprintf(stderr, "[node] шлюз закрив з'єднання\n");
        return -1;
    }
    if (n < 0) {
        if (errno == EINTR || errno == EAGAIN) {
            return 0;
        }
        fprintf(stderr, "[node] читання з каналу впало — %s\n", strerror(errno));
        return -1;
    }
    lk->rx_len += (size_t)n;

    return try_extract(lk, out);
}
