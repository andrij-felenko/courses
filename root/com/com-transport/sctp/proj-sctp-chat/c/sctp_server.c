/* sctp_server.c — Сервер телеметрії та команд на SCTP (C99 / POSIX) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/sctp.h>
#include <arpa/inet.h>

#define SERVER_PORT 9899
#define BUFFER_SIZE 2048
#define STREAM_CONTROL   0
#define STREAM_TELEMETRY 1
#define PPID_CONTROL   0x0100
#define PPID_TELEMETRY 0x0200

void handle_notification(const union sctp_notification *notif) {
    switch (notif->sn_header.sn_type) {
        case SCTP_ASSOC_CHANGE: {
            const struct sctp_assoc_change *sac = &notif->sn_assoc_change;
            if (sac->sac_state == SCTP_COMM_UP) {
                printf("[ПОДІЯ] Асоціацію встановлено (ID: %u, InStr: %u, OutStr: %u)\n",
                       sac->sac_assoc_id, sac->sac_inbound_streams, sac->sac_outbound_streams);
            } else if (sac->sac_state == SCTP_COMM_LOST) {
                printf("[ПОДІЯ] Асоціацію втрачено (ID: %u)\n", sac->sac_assoc_id);
            }
            break;
        }
        case SCTP_PEER_ADDR_CHANGE: {
            const struct sctp_paddr_change *spc = &notif->sn_paddr_change;
            char ip_str[INET_ADDRSTRLEN];
            const struct sockaddr_in *sin = (const struct sockaddr_in *)&spc->spc_aaddr;
            inet_ntop(AF_INET, &sin->sin_addr, ip_str, sizeof(ip_str));
            printf("[ПОДІЯ] Зміна стану адреси піра %s: стан = %u\n", ip_str, spc->spc_state);
            break;
        }
        case SCTP_SHUTDOWN_EVENT:
            printf("[ПОДІЯ] Пір ініціював плавне закриття (Shutdown)\n");
            break;
        default:
            break;
    }
}

int main(void) {
    int listen_fd = socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);
    if (listen_fd < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    /* 1. Налаштовуємо кількість потоків */
    struct sctp_initmsg initmsg;
    memset(&initmsg, 0, sizeof(initmsg));
    initmsg.sinit_num_ostreams = 5;
    initmsg.sinit_max_instreams = 5;
    initmsg.sinit_max_attempts = 4;
    if (setsockopt(listen_fd, IPPROTO_SCTP, SCTP_INITMSG, &initmsg, sizeof(initmsg)) < 0) {
        perror("setsockopt SCTP_INITMSG");
        close(listen_fd);
        return EXIT_FAILURE;
    }

    /* 2. Підписуємося на події ядра */
    struct sctp_event_subscribe events;
    memset(&events, 0, sizeof(events));
    events.sctp_data_io_event = 1;
    events.sctp_association_event = 1;
    events.sctp_address_event = 1;
    events.sctp_shutdown_event = 1;
    if (setsockopt(listen_fd, IPPROTO_SCTP, SCTP_EVENTS, &events, sizeof(events)) < 0) {
        perror("setsockopt SCTP_EVENTS");
        close(listen_fd);
        return EXIT_FAILURE;
    }

    /* 3. Прив'язка до порту */
    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(SERVER_PORT);

    if (bind(listen_fd, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
        perror("bind");
        close(listen_fd);
        return EXIT_FAILURE;
    }

    if (listen(listen_fd, 5) < 0) {
        perror("listen");
        close(listen_fd);
        return EXIT_FAILURE;
    }

    printf("SCTP Сервер запущено на порту %d. Очікування клієнтів...\n", SERVER_PORT);

    struct sockaddr_in cliaddr;
    socklen_t clilen = sizeof(cliaddr);
    int conn_fd = accept(listen_fd, (struct sockaddr *)&cliaddr, &clilen);
    if (conn_fd < 0) {
        perror("accept");
        close(listen_fd);
        return EXIT_FAILURE;
    }

    char client_ip[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &cliaddr.sin_addr, client_ip, sizeof(client_ip));
    printf("Клієнт підключився: %s:%d\n", client_ip, ntohs(cliaddr.sin_port));

    /* 4. Цикл прийому повідомлень та обробки потоків */
    char buffer[BUFFER_SIZE];
    struct sctp_sndrcvinfo sinfo;
    int flags = 0;

    while (1) {
        memset(buffer, 0, sizeof(buffer));
        memset(&sinfo, 0, sizeof(sinfo));
        flags = 0;

        ssize_t bytes = sctp_recvmsg(conn_fd, buffer, sizeof(buffer) - 1,
                                     NULL, 0, &sinfo, &flags);
        if (bytes <= 0) {
            printf("З'єднання закрито або виникла помилка.\n");
            break;
        }

        if (flags & MSG_NOTIFICATION) {
            handle_notification((const union sctp_notification *)buffer);
            continue;
        }

        buffer[bytes] = '\0';
        uint32_t ppid = ntohl(sinfo.sinfo_ppid);

        if (sinfo.sinfo_stream == STREAM_CONTROL) {
            printf("[КОМАНДА] Потік: %u, SSN: %u, TSN: %u, PPID: 0x%04X | Вміст: %s\n",
                   sinfo.sinfo_stream, sinfo.sinfo_ssn, sinfo.sinfo_tsn, ppid, buffer);
            /* Відправляємо підтвердження виконання команди */
            char ack_msg[64];
            snprintf(ack_msg, sizeof(ack_msg), "ACK-CMD:%s", buffer);
            sctp_sendmsg(conn_fd, ack_msg, strlen(ack_msg), NULL, 0,
                         htonl(PPID_CONTROL), 0, STREAM_CONTROL, 0, 0);
        } else if (sinfo.sinfo_stream == STREAM_TELEMETRY) {
            printf("[ТЕЛЕМЕТРІЯ] Потік: %u, SSN: %u (Unordered), TSN: %u | Дані: %s\n",
                   sinfo.sinfo_stream, sinfo.sinfo_ssn, sinfo.sinfo_tsn, buffer);
        } else {
            printf("[НЕВІДОМИЙ ПОТІК] Потік: %u | Дані: %s\n", sinfo.sinfo_stream, buffer);
        }
    }

    close(conn_fd);
    close(listen_fd);
    return EXIT_SUCCESS;
}
