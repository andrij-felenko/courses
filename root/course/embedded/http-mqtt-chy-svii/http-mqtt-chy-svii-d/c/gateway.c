/* gateway.c — та сама ціна власного протоколу: приймати кадри нікому,
 * тож шлюз пишемо самі. Слухає UDP, перевіряє CRC, розбирає структуру,
 * відсіює дублікати після втраченого ACK і підтверджує кожен кадр.
 *
 * Збірка: cc -std=c11 -O2 -Wall -Wextra -o gateway gateway.c frame.c */
#include <errno.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#include "frame.h"

#define PEERS_MAX 16

/* Дублікати неминучі: якщо ACK загубився, вузол шле той самий кадр удруге.
 * Тримаємо останній підтверджений номер на кожного відправника — цього
 * досить, бо ARQ у вузла stop-and-wait і в польоті завжди один кадр. */
struct peer_slot {
    char     key[NI_MAXHOST + NI_MAXSERV + 2];
    uint16_t last_seq;
    int      used;
};

static struct peer_slot peers[PEERS_MAX];
static int peers_next;   /* кругова заміна, коли всі слоти зайняті */

static int is_duplicate(const char *key, uint16_t seq)
{
    for (int i = 0; i < PEERS_MAX; i++) {
        if (peers[i].used && strcmp(peers[i].key, key) == 0) {
            int dup = (peers[i].last_seq == seq);
            peers[i].last_seq = seq;
            return dup;
        }
    }

    int slot = -1;
    for (int i = 0; i < PEERS_MAX; i++) {
        if (!peers[i].used) {
            slot = i;
            break;
        }
    }
    if (slot < 0) {
        slot = peers_next;
        peers_next = (peers_next + 1) % PEERS_MAX;
    }

    snprintf(peers[slot].key, sizeof peers[slot].key, "%s", key);
    peers[slot].last_seq = seq;
    peers[slot].used = 1;
    return 0;
}

static int bind_udp(const char *port)
{
    struct addrinfo hints;
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET6;      /* один сокет на IPv6 і IPv4-mapped */
    hints.ai_socktype = SOCK_DGRAM;
    hints.ai_flags = AI_PASSIVE;

    struct addrinfo *res = NULL;
    int rc = getaddrinfo(NULL, port, &hints, &res);
    if (rc != 0) {
        fprintf(stderr, "gateway: порт %s — %s\n", port, gai_strerror(rc));
        return -1;
    }

    int fd = -1;
    for (struct addrinfo *ai = res; ai != NULL; ai = ai->ai_next) {
        fd = socket(ai->ai_family, ai->ai_socktype, ai->ai_protocol);
        if (fd < 0) {
            continue;
        }
        int off = 0;
        setsockopt(fd, IPPROTO_IPV6, IPV6_V6ONLY, &off, sizeof off);
        if (bind(fd, ai->ai_addr, ai->ai_addrlen) == 0) {
            break;
        }
        close(fd);
        fd = -1;
    }
    freeaddrinfo(res);

    if (fd < 0) {
        fprintf(stderr, "gateway: не сів на порт %s — %s\n", port, strerror(errno));
    }
    return fd;
}

int main(int argc, char **argv)
{
    const char *port = (argc > 1) ? argv[1] : "9000";

    int fd = bind_udp(port);
    if (fd < 0) {
        return 1;
    }
    printf("gateway: слухаю UDP %s\n", port);

    for (;;) {
        uint8_t buf[128];
        struct sockaddr_storage from;
        socklen_t from_len = sizeof from;

        ssize_t n = recvfrom(fd, buf, sizeof buf, 0,
                             (struct sockaddr *)&from, &from_len);
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            fprintf(stderr, "gateway: recvfrom — %s\n", strerror(errno));
            break;
        }

        char host[NI_MAXHOST];
        char serv[NI_MAXSERV];
        if (getnameinfo((const struct sockaddr *)&from, from_len,
                        host, sizeof host, serv, sizeof serv,
                        NI_NUMERICHOST | NI_NUMERICSERV) != 0) {
            snprintf(host, sizeof host, "?");
            snprintf(serv, sizeof serv, "?");
        }
        char key[sizeof peers[0].key];
        snprintf(key, sizeof key, "%s:%s", host, serv);

        sensor_packet_t pkt;
        int rc = frame_parse_telemetry(buf, (size_t)n, &pkt);
        if (rc != FRAME_OK) {
            /* Побитий або чужий кадр не підтверджуємо: хай вузол повторить. */
            fprintf(stderr, "gateway: %s — кадр відкинуто (%s)\n",
                    key, frame_strerror(rc));
            continue;
        }

        int dup = is_duplicate(key, pkt.seq_num);
        if (!dup) {
            printf("%s #%u ts=%u  %d.%02d °C  %u.%02u %%  %u мВ\n",
                   key, (unsigned)pkt.seq_num, (unsigned)pkt.timestamp,
                   pkt.temperature / 100, (pkt.temperature % 100 + 100) % 100,
                   pkt.humidity / 100, pkt.humidity % 100,
                   pkt.vbat_mv);
            fflush(stdout);
        } else {
            printf("%s #%u — повтор, у базу не пишемо\n", key, (unsigned)pkt.seq_num);
            fflush(stdout);
        }

        /* Підтверджуємо і повтор теж: саме втрата ACK його й спричинила. */
        uint8_t ack[ACK_SIZE];
        int len = frame_pack_ack(pkt.seq_num, ack, sizeof ack);
        if (len > 0) {
            if (sendto(fd, ack, (size_t)len, 0,
                       (const struct sockaddr *)&from, from_len) < 0) {
                fprintf(stderr, "gateway: ACK не пішов — %s\n", strerror(errno));
            }
        }
    }

    close(fd);
    return 1;
}
