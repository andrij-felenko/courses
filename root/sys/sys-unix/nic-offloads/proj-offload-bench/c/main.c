#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/udp.h>
#include <arpa/inet.h>

#define SEGMENT_SIZE 1472
#define NUM_SEGMENTS 44
#define TOTAL_PAYLOAD (SEGMENT_SIZE * NUM_SEGMENTS) // 64768 байт
#define ITERATIONS 20000

static double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <IP> <PORT> [gso|std]\n", argv[0]);
        return 1;
    }

    const char *ip_str = argv[1];
    int port = atoi(argv[2]);
    int use_gso = (argc >= 4 && strcmp(argv[3], "gso") == 0);

    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket");
        return 1;
    }

    struct sockaddr_in dst_addr;
    memset(&dst_addr, 0, sizeof(dst_addr));
    dst_addr.sin_family = AF_INET;
    dst_addr.sin_port = htons(port);
    inet_pton(AF_INET, ip_str, &dst_addr.sin_addr);

    char *buffer = malloc(TOTAL_PAYLOAD);
    memset(buffer, 'A', TOTAL_PAYLOAD);

    printf("Розпочинаємо тест: режим = %s, обсяг на ітерацію = %d B, ітерацій = %d\n",
           use_gso ? "UDP-GSO" : "Стандартний UDP", TOTAL_PAYLOAD, ITERATIONS);

    double start_time = get_time_sec();

    for (int i = 0; i < ITERATIONS; ++i) {
        if (use_gso) {
            struct iovec iov;
            iov.iov_base = buffer;
            iov.iov_len = TOTAL_PAYLOAD;

            char cbuf[CMSG_SPACE(sizeof(uint16_t))];
            memset(cbuf, 0, sizeof(cbuf));

            struct msghdr msg;
            memset(&msg, 0, sizeof(msg));
            msg.msg_name = &dst_addr;
            msg.msg_namelen = sizeof(dst_addr);
            msg.msg_iov = &iov;
            msg.msg_iovlen = 1;
            msg.msg_control = cbuf;
            msg.msg_controllen = sizeof(cbuf);

            struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
            cmsg->cmsg_level = SOL_UDP;
            cmsg->cmsg_type = UDP_SEGMENT;
            cmsg->cmsg_len = CMSG_LEN(sizeof(uint16_t));
            *(uint16_t *)CMSG_DATA(cmsg) = SEGMENT_SIZE;

            if (sendmsg(sockfd, &msg, 0) < 0) {
                perror("sendmsg");
                break;
            }
        } else {
            for (int j = 0; j < NUM_SEGMENTS; ++j) {
                if (sendto(sockfd, buffer + (j * SEGMENT_SIZE), SEGMENT_SIZE, 0,
                           (struct sockaddr *)&dst_addr, sizeof(dst_addr)) < 0) {
                    perror("sendto");
                    break;
                }
            }
        }
    }

    double elapsed = get_time_sec() - start_time;
    double total_bytes = (double)TOTAL_PAYLOAD * ITERATIONS;
    double mbits = (total_bytes * 8.0) / (elapsed * 1e6);

    printf("Тест завершено за %.4f сек. Пропускна здатність: %.2f Mbit/s\n", elapsed, mbits);

    free(buffer);
    close(sockfd);
    return 0;
}
