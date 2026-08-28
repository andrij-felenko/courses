/* Повноцінне налаштування SCTP-сервера з мультихоумінгом мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/sctp.h>
#include <arpa/inet.h>

int init_sctp_multihome_server(const char *ip1, const char *ip2, uint16_t port) {
    int sd = socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);
    if (sd < 0) {
        perror("Помилка створення сокета SCTP");
        return -1;
    }

    /* 1. Конфігурація кількості потоків */
    struct sctp_initmsg initmsg;
    memset(&initmsg, 0, sizeof(initmsg));
    initmsg.sinit_num_ostreams = 10;
    initmsg.sinit_max_instreams = 10;
    initmsg.sinit_max_attempts = 4;
    initmsg.sinit_max_init_timeo = 5000;
    if (setsockopt(sd, IPPROTO_SCTP, SCTP_INITMSG, &initmsg, sizeof(initmsg)) < 0) {
        perror("Помилка setsockopt SCTP_INITMSG");
        close(sd);
        return -1;
    }

    /* 2. Підписка на події ядра */
    struct sctp_event_subscribe events;
    memset(&events, 0, sizeof(events));
    events.sctp_data_io_event = 1;
    events.sctp_association_event = 1;
    events.sctp_address_event = 1;
    events.sctp_shutdown_event = 1;
    if (setsockopt(sd, IPPROTO_SCTP, SCTP_EVENTS, &events, sizeof(events)) < 0) {
        perror("Помилка setsockopt SCTP_EVENTS");
        close(sd);
        return -1;
    }

    /* 3. Прив'язка двох IP-адрес через sctp_bindx */
    struct sockaddr_in bind_addrs[2];
    memset(bind_addrs, 0, sizeof(bind_addrs));

    bind_addrs[0].sin_family = AF_INET;
    bind_addrs[0].sin_port = htons(port);
    if (inet_pton(AF_INET, ip1, &bind_addrs[0].sin_addr) <= 0) {
        close(sd);
        return -1;
    }

    bind_addrs[1].sin_family = AF_INET;
    bind_addrs[1].sin_port = htons(port);
    if (inet_pton(AF_INET, ip2, &bind_addrs[1].sin_addr) <= 0) {
        close(sd);
        return -1;
    }

    if (sctp_bindx(sd, (struct sockaddr *)bind_addrs, 2, SCTP_BINDX_ADD_ADDR) < 0) {
        perror("Помилка sctp_bindx");
        close(sd);
        return -1;
    }

    if (listen(sd, 10) < 0) {
        perror("Помилка listen");
        close(sd);
        return -1;
    }

    return sd;
}
