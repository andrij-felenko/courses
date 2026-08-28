#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

void inspect_tcp_socket(int sockfd) {
    char name_buf[32] = {0};
    socklen_t name_len = sizeof(name_buf);

    /* Читання поточного названого алгоритму */
    if (getsockopt(sockfd, IPPROTO_TCP, TCP_CONGESTION, name_buf, &name_len) == 0) {
        printf("Поточний алгоритм CC: %s\n", name_buf);
    } else {
        perror("getsockopt TCP_CONGESTION");
    }

    /* Отримання детальної метрики tcp_info */
    struct tcp_info info;
    socklen_t info_len = sizeof(info);
    if (getsockopt(sockfd, IPPROTO_TCP, TCP_INFO, &info, &info_len) == 0) {
        printf("Метрики TCP_INFO:\n");
        printf("  - cwnd:          %u MSS (у байтах: %u)\n", 
               info.tcpi_snd_cwnd, info.tcpi_snd_cwnd * info.tcpi_snd_mss);
        printf("  - ssthresh:      %u\n", info.tcpi_snd_ssthresh);
        printf("  - RTT:           %.2f ms (var: %.2f ms)\n", 
               info.tcpi_rtt / 1000.0, info.tcpi_rttvar / 1000.0);
        printf("  - Min RTT:       %.2f ms\n", info.tcpi_min_rtt / 1000.0);
        printf("  - Pacing rate:   %.2f Mbit/s\n", 
               (info.tcpi_pacing_rate * 8.0) / 1000000.0);
        printf("  - Delivery rate: %.2f Mbit/s\n", 
               (info.tcpi_delivery_rate * 8.0) / 1000000.0);
    } else {
        perror("getsockopt TCP_INFO");
    }
}

int main(void) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) {
        perror("socket failed");
        return 1;
    }

    /* Встановлення алгоритму CUBIC */
    const char *algo = "cubic";
    if (setsockopt(fd, IPPROTO_TCP, TCP_CONGESTION, algo, strlen(algo) + 1) != 0) {
        perror("setsockopt TCP_CONGESTION failed");
    }

    inspect_tcp_socket(fd);

    close(fd);
    return 0;
}
