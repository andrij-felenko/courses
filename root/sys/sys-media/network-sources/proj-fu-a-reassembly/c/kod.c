#include <arpa/inet.h>
#include <stdio.h>
#include <sys/socket.h>

static uint8_t au_buf[4u << 20];        /* 4 МіБ — з запасом на ключовий кадр */

static void on_au(const h264_au *au, void *user)
{
    (void)user;
    printf("AU %zu Б, ts=%u%s%s\n", au->len, au->rtp_ts,
           au->keyframe ? ", ключовий" : "",
           au->damaged  ? ", БИТИЙ"    : "");
}

int main(void)
{
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    struct sockaddr_in a = { .sin_family = AF_INET,
                             .sin_port   = htons(5600),
                             .sin_addr.s_addr = htonl(INADDR_ANY) };
    bind(fd, (struct sockaddr *)&a, sizeof(a));

    h264_depay d;
    h264_depay_init(&d, au_buf, sizeof(au_buf), 96, on_au, NULL);

    uint8_t pkt[2048];
    for (;;) {
        ssize_t n = recv(fd, pkt, sizeof(pkt), 0);
        if (n <= 0) break;
        h264_depay_packet(&d, pkt, (size_t)n);
    }
    return 0;
}
