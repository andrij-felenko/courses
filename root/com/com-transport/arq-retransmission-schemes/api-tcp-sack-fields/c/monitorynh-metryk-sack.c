#include <stdio.h>
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <unistd.h>

/* Отримання статистики SACK та повторних передач для відкритого сокета TCP */
void print_socket_sack_stats(int sockfd) {
    struct tcp_info info;
    socklen_t len = sizeof(info);

    if (getsockopt(sockfd, IPPROTO_TCP, TCP_INFO, &info, &len) == 0) {
        printf("=== Статистика TCP SACK сокета ===\n");
        printf("Кількість підтверджених через SACK пакетів: %u\n", info.tcpi_sacked);
        printf("Кількість зафіксованих втрачених пакетів:      %u\n", info.tcpi_lost);
        printf("Кількість виконаних повторних передач:        %u\n", info.tcpi_retrans);
        printf("Оцінка RTT:                                   %u мкс (RTTvar: %u мкс)\n", 
               info.tcpi_rtt, info.tcpi_rttvar);
        printf("Поточний розмір вікна перевантаження (CWND):   %u сегментів\n", info.tcpi_snd_cwnd);
    }
}
