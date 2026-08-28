/* Збірка: cc gcs.c -o gcs -I ./mavlink            (заголовки mavgen — самі лише .h) */
#include <mavlink/common/mavlink.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define GCS_SYSID  255                     /* так себе називають наземні станції */
#define GCS_COMPID MAV_COMP_ID_MISSIONPLANNER

static uint64_t now_ms(void) {                /* монотонний час: годинник системи може стрибнути */
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

static int open_udp(uint16_t port) {
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    struct sockaddr_in me = { .sin_family = AF_INET,
                              .sin_addr.s_addr = htonl(INADDR_ANY),
                              .sin_port = htons(port) };
    bind(fd, (struct sockaddr *)&me, sizeof me);

    /* Читання з таймаутом: цикл мусить прокидатися, навіть коли борт мовчить,
       інакше нема кому ні повторити команду, ні оновити рядок на екрані. */
    struct timeval tv = { .tv_sec = 0, .tv_usec = 200000 };   /* 200 мс */
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);
    return fd;
}
