#include <iostream>
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <unistd.h>

namespace net {

struct SocketStats {
    uint32_t sacked_packets{0};
    uint32_t lost_packets{0};
    uint32_t retransmitted_packets{0};
    uint32_t rtt_us{0};
    uint32_t rttvar_us{0};
    uint32_t cwnd_segments{0};
};

[[nodiscard]] std::optional<SocketStats> get_tcp_sack_stats(int sockfd) noexcept {
    struct tcp_info info{};
    socklen_t len = sizeof(info);

    if (::getsockopt(sockfd, IPPROTO_TCP, TCP_INFO, &info, &len) != 0) {
        return std::nullopt;
    }

    return SocketStats{
        .sacked_packets = info.tcpi_sacked,
        .lost_packets = info.tcpi_lost,
        .retransmitted_packets = info.tcpi_retrans,
        .rtt_us = info.tcpi_rtt,
        .rttvar_us = info.tcpi_rttvar,
        .cwnd_segments = info.tcpi_snd_cwnd
    };
}

void print_stats(int sockfd) {
    if (const auto stats = get_tcp_sack_stats(sockfd)) {
        std::cout << "=== Статистика TCP SACK (C++) ===\n"
                  << "SACKed: " << stats->sacked_packets << "\n"
                  << "Lost:   " << stats->lost_packets << "\n"
                  << "Retrans:" << stats->retransmitted_packets << "\n"
                  << "RTT:    " << stats->rtt_us << " us\n";
    }
}

} // namespace net
