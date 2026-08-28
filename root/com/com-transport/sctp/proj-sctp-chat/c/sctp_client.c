/* sctp_client.c — Клієнт телеметрії та команд на SCTP (C99 / POSIX) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/sctp.h>
#include <arpa/inet.h>

#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 9899
#define STREAM_CONTROL   0
#define STREAM_TELEMETRY 1
#define PPID_CONTROL   0x0100
#define PPID_TELEMETRY 0x0200

int main(void) {
    int sd = socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);
    if (sd < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    /* Налаштовуємо кількість потоків */
    struct sctp_initmsg initmsg;
    memset(&initmsg, 0, sizeof(initmsg));
    initmsg.sinit_num_ostreams = 5;
    initmsg.sinit_max_instreams = 5;
    initmsg.sinit_max_attempts = 4;
    setsockopt(sd, IPPROTO_SCTP, SCTP_INITMSG, &initmsg, sizeof(initmsg));

    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &servaddr.sin_addr);

    printf("Підключення до SCTP сервера %s:%d...\n", SERVER_IP, SERVER_PORT);
    if (connect(sd, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
        perror("connect");
        close(sd);
        return EXIT_FAILURE;
    }
    printf("Асоціацію успішно встановлено!\n");

    /* 1. Відправляємо впорядковані команди на Потоці 0 */
    const char *commands[] = {
        "CMD:INIT_SYSTEM",
        "CMD:CALIBRATE_SENSORS",
        "CMD:ARM_MOTORS",
        "CMD:TAKEOFF_ALT_20M"
    };
    for (int i = 0; i < 4; ++i) {
        sctp_sendmsg(sd, commands[i], strlen(commands[i]), NULL, 0,
                     htonl(PPID_CONTROL), 0, STREAM_CONTROL, 0, 0);
        printf("[КЛІЄНТ] Надіслано на Потік %d (Ordered): %s\n", STREAM_CONTROL, commands[i]);
        usleep(50000); // 50 мс
    }

    /* 2. Відправляємо високочастотну телеметрію на Потоці 1 (Unordered) */
    char telemetry[64];
    for (int i = 1; i <= 5; ++i) {
        snprintf(telemetry, sizeof(telemetry), "TELEM:pkt=%d;lat=50.4501;lon=30.5234;alt=%d.5", i, 20 + i);
        sctp_sendmsg(sd, telemetry, strlen(telemetry), NULL, 0,
                     htonl(PPID_TELEMETRY), SCTP_UNORDERED, STREAM_TELEMETRY, 0, 0);
        printf("[КЛІЄНТ] Надіслано на Потік %d (Unordered): %s\n", STREAM_TELEMETRY, telemetry);
        usleep(20000); // 20 мс
    }

    /* 3. Очікуємо підтвердження команд */
    char recv_buf[256];
    struct sctp_sndrcvinfo sinfo;
    int flags = 0;
    for (int i = 0; i < 4; ++i) {
        ssize_t n = sctp_recvmsg(sd, recv_buf, sizeof(recv_buf) - 1, NULL, 0, &sinfo, &flags);
        if (n > 0) {
            recv_buf[n] = '\0';
            printf("[КЛІЄНТ ВІДПОВІДЬ] Потік %d: %s\n", sinfo.sinfo_stream, recv_buf);
        }
    }

    printf("Завершення роботи клієнта.\n");
    close(sd);
    return EXIT_SUCCESS;
}
