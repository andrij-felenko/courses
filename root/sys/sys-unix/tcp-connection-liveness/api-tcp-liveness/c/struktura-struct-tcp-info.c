#include <sys/socket.h>
#include <netinet/tcp.h>

struct tcp_info info;
socklen_t len = sizeof(info);
if (getsockopt(sockfd, IPPROTO_TCP, TCP_INFO, &info, &len) == 0) {
    /* info.tcpi_state — поточний стан TCP (напр. TCP_ESTABLISHED) */
    /* info.tcpi_rto — поточний очікуваний таймаут повтору (RTO) у мікросекундах */
    /* info.tcpi_unacked — кількість непідтверджених пакетів у мережі */
    /* info.tcpi_probes — кількість вже надісланих зондувальних пакетів */
    /* info.tcpi_backoff — поточний ступінь експоненційного відступу RTO */
    /* info.tcpi_retransmits — кількість виконаних повторних передач */
}
