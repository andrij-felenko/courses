/* uplink.c — сокет, ARQ stop-and-wait і спул відкладених кадрів. */
#include "uplink.h"

#include <errno.h>
#include <netdb.h>
#include <netinet/in.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

static long long now_ms(void)
{
    struct timespec ts;
    /* Монотонний годинник: коригування системного часу посеред очікування
     * не має ані подовжити таймаут, ані обірвати його достроково. */
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

/* Сокет ми навмисно не connect()-имо: показуємо, що на голому UDP чужа
 * датаграма прилітає в той самий буфер, і відсіяти її — робота прикладного
 * рівня. Порівнюємо родину, порт і адресу, а не байти sockaddr цілком:
 * у sockaddr_in є padding, який ніхто не зобов'язаний заповнювати однаково. */
static int same_peer(const struct sockaddr *a, const struct sockaddr *b)
{
    if (a->sa_family != b->sa_family) {
        return 0;
    }
    if (a->sa_family == AF_INET) {
        const struct sockaddr_in *x = (const struct sockaddr_in *)(const void *)a;
        const struct sockaddr_in *y = (const struct sockaddr_in *)(const void *)b;
        return x->sin_port == y->sin_port &&
               x->sin_addr.s_addr == y->sin_addr.s_addr;
    }
    if (a->sa_family == AF_INET6) {
        const struct sockaddr_in6 *x = (const struct sockaddr_in6 *)(const void *)a;
        const struct sockaddr_in6 *y = (const struct sockaddr_in6 *)(const void *)b;
        return x->sin6_port == y->sin6_port &&
               memcmp(&x->sin6_addr, &y->sin6_addr, sizeof x->sin6_addr) == 0;
    }
    return 0;
}

int uplink_open(uplink_t *up, const char *host, const char *port,
                const char *spool_path, uint16_t first_seq)
{
    memset(up, 0, sizeof *up);
    up->fd = -1;
    up->spool_path = spool_path;
    up->seq = first_seq;

    struct addrinfo hints;
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_DGRAM;
    hints.ai_protocol = IPPROTO_UDP;

    struct addrinfo *res = NULL;
    /* DNS тут коштує окремий оберт по мережі. У прошивці розв'язану адресу
     * кладуть у NVS і повторюють запит хіба що після кількох невдач поспіль. */
    int rc = getaddrinfo(host, port, &hints, &res);
    if (rc != 0) {
        fprintf(stderr, "uplink: не розв'язав %s:%s — %s\n",
                host, port, gai_strerror(rc));
        return -1;
    }

    for (struct addrinfo *ai = res; ai != NULL; ai = ai->ai_next) {
        int fd = socket(ai->ai_family, ai->ai_socktype, ai->ai_protocol);
        if (fd < 0) {
            continue;
        }
        up->fd = fd;
        memcpy(&up->peer, ai->ai_addr, ai->ai_addrlen);
        up->peer_len = ai->ai_addrlen;
        break;
    }
    freeaddrinfo(res);

    if (up->fd < 0) {
        fprintf(stderr, "uplink: не відкрив сокет — %s\n", strerror(errno));
        return -1;
    }
    return 0;
}

void uplink_close(uplink_t *up)
{
    if (up->fd >= 0) {
        close(up->fd);
        up->fd = -1;
    }
}

/* Чекає ACK саме на want_seq, поки не вичерпається timeout_ms.
 * Чужі датаграми й запізнілі підтвердження минулих спроб не з'їдають
 * таймаут цілком: залишок часу перераховується на кожному оберті. */
static int wait_ack(uplink_t *up, uint16_t want_seq, int timeout_ms)
{
    const long long deadline = now_ms() + timeout_ms;

    for (;;) {
        long long left = deadline - now_ms();
        if (left <= 0) {
            return -1;
        }

        struct pollfd pfd;
        pfd.fd = up->fd;
        pfd.events = POLLIN;
        pfd.revents = 0;

        int rc = poll(&pfd, 1, (int)left);
        if (rc < 0) {
            if (errno == EINTR) {
                continue;   /* прокинулися від сигналу — дочекуємо залишок */
            }
            return -1;
        }
        if (rc == 0) {
            return -1;      /* тиша: час вийшов */
        }

        uint8_t buf[64];
        struct sockaddr_storage from;
        socklen_t from_len = sizeof from;
        ssize_t n = recvfrom(up->fd, buf, sizeof buf, 0,
                             (struct sockaddr *)&from, &from_len);
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            return -1;
        }

        if (!same_peer((const struct sockaddr *)&from,
                       (const struct sockaddr *)&up->peer)) {
            continue;       /* сканер портів або сусідній вузол */
        }

        uint16_t got = 0;
        if (frame_parse_ack(buf, (size_t)n, &got) != FRAME_OK) {
            continue;
        }
        if (got != want_seq) {
            continue;       /* підтвердження попередньої спроби, вже неактуальне */
        }
        return 0;
    }
}

/* Одна транзакція: до ARQ_ATTEMPTS відправок того самого кадру.
 * Номер кадру не міняється — сервер бачить повтор і не задвоює запис. */
static int send_frame_arq(uplink_t *up, const uint8_t *frame)
{
    const uint16_t seq = (uint16_t)((uint16_t)frame[2] | ((uint16_t)frame[3] << 8));

    for (int attempt = 1; attempt <= ARQ_ATTEMPTS; attempt++) {
        long long t0 = now_ms();

        ssize_t n = sendto(up->fd, frame, TELEMETRY_SIZE, 0,
                           (const struct sockaddr *)&up->peer, up->peer_len);
        if (n != (ssize_t)TELEMETRY_SIZE) {
            fprintf(stderr, "uplink: sendto — %s\n", strerror(errno));
            up->tx_ms += now_ms() - t0;
            /* Мережі зараз немає взагалі; повторювати негайно немає сенсу. */
            return -1;
        }

        int rc = wait_ack(up, seq, ARQ_TIMEOUT_MS);
        up->tx_ms += now_ms() - t0;

        if (rc == 0) {
            return 0;
        }
        fprintf(stderr, "uplink: кадр #%u без ACK, спроба %d з %d\n",
                (unsigned)seq, attempt, ARQ_ATTEMPTS);
    }
    return -1;
}

/* --- спул: те, що не пішло в ефір, чекає на диску (у прошивці — в NVS) --- */

static size_t spool_load(const uplink_t *up, uint8_t *out, size_t max_frames,
                         size_t *dropped)
{
    *dropped = 0;

    FILE *f = fopen(up->spool_path, "rb");
    if (f == NULL) {
        return 0;   /* спулу немає — і добре */
    }

    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return 0;
    }
    long size = ftell(f);
    if (size < 0) {
        fclose(f);
        return 0;
    }

    size_t frames = (size_t)size / TELEMETRY_SIZE;
    size_t skip = frames > max_frames ? frames - max_frames : 0;
    *dropped = skip;    /* переповнення: найстаріші виміри втрачаємо свідомо */

    if (fseek(f, (long)(skip * TELEMETRY_SIZE), SEEK_SET) != 0) {
        fclose(f);
        return 0;
    }
    size_t got = fread(out, TELEMETRY_SIZE, frames - skip, f);
    fclose(f);
    return got;
}

static void spool_store(const uplink_t *up, const uint8_t *frames, size_t count)
{
    if (count == 0) {
        remove(up->spool_path);
        return;
    }
    FILE *f = fopen(up->spool_path, "wb");
    if (f == NULL) {
        fprintf(stderr, "uplink: спул не відкрився на запис — %s\n",
                strerror(errno));
        return;
    }
    if (fwrite(frames, TELEMETRY_SIZE, count, f) != count) {
        fprintf(stderr, "uplink: спул не дописався — %s\n", strerror(errno));
    }
    fclose(f);
}

static void spool_append(uplink_t *up, const uint8_t *frame)
{
    static uint8_t buf[SPOOL_MAX_FRAMES * TELEMETRY_SIZE];
    size_t dropped = 0;
    size_t count = spool_load(up, buf, SPOOL_MAX_FRAMES, &dropped);

    if (count == SPOOL_MAX_FRAMES) {
        /* Місця більше немає: викидаємо найстаріший кадр. Свіжий вимір
         * цінніший за торішній — це рішення, а не аварія. */
        memmove(buf, buf + TELEMETRY_SIZE, (count - 1) * TELEMETRY_SIZE);
        count--;
        dropped++;
    }

    memcpy(buf + count * TELEMETRY_SIZE, frame, TELEMETRY_SIZE);
    count++;

    spool_store(up, buf, count);

    if (dropped > 0) {
        fprintf(stderr, "uplink: спул переповнено, втрачено %zu кадрів\n", dropped);
    }
}

int uplink_flush_spool(uplink_t *up)
{
    static uint8_t buf[SPOOL_MAX_FRAMES * TELEMETRY_SIZE];
    size_t dropped = 0;
    size_t count = spool_load(up, buf, SPOOL_MAX_FRAMES, &dropped);
    if (count == 0) {
        if (dropped > 0) {
            spool_store(up, buf, 0);
        }
        return 0;
    }

    size_t sent = 0;
    while (sent < count) {
        if (send_frame_arq(up, buf + sent * TELEMETRY_SIZE) != 0) {
            break;  /* канал знову мовчить — решту лишаємо на наступний сеанс */
        }
        sent++;
    }

    if (sent < count) {
        memmove(buf, buf + sent * TELEMETRY_SIZE,
                (count - sent) * TELEMETRY_SIZE);
    }
    spool_store(up, buf, count - sent);

    return (int)sent;
}

int uplink_send(uplink_t *up, const sensor_sample_t *sample)
{
    uint8_t frame[TELEMETRY_SIZE];

    int len = frame_pack_telemetry(sample, up->seq, frame, sizeof frame);
    if (len < 0) {
        fprintf(stderr, "uplink: кадр не склався — %s\n", frame_strerror(len));
        return -1;
    }

    /* Номер росте навіть тоді, коли кадр не пішов: сервер по розривах у
     * послідовності бачить, скільки вимірів не доїхало взагалі. */
    up->seq++;

    if (send_frame_arq(up, frame) == 0) {
        return 0;
    }

    spool_append(up, frame);
    return -1;
}
