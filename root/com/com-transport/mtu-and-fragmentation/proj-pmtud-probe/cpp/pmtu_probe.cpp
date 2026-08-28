// pmtu_probe.cpp — Ідіоматична реалізація сканера Path MTU на C++20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <chrono>
#include <optional>
#include <memory>
#include <span>
#include <numeric>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <arpa/inet.h>

// RAII обгортка для безпечного керування дескриптором сирого сокета
class RawSocket {
public:
    explicit RawSocket(int protocol) {
        fd_ = ::socket(AF_INET, SOCK_RAW, protocol);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(),
                                    "Не вдалося відкрити raw socket (потрібні привілеї root/CAP_NET_RAW)");
        }
    }

    ~RawSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    RawSocket(const RawSocket&) = delete;
    RawSocket& operator=(const RawSocket&) = delete;

    RawSocket(RawSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    RawSocket& operator=(RawSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

    void set_dont_fragment() {
        int val = IP_PMTUDISC_DO;
        if (::setsockopt(fd_, IPPROTO_IP, IP_MTU_DISCOVER, &val, sizeof(val)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка встановлення IP_MTU_DISCOVER");
        }
    }

    void set_timeout(std::chrono::milliseconds timeout) {
        auto sec = std::chrono::duration_cast<std::chrono::seconds>(timeout);
        auto usec = std::chrono::duration_cast<std::chrono::microseconds>(timeout - sec);
        struct timeval tv{
            .tv_sec = static_cast<time_t>(sec.count()),
            .tv_usec = static_cast<suseconds_t>(usec.count())
        };
        ::setsockopt(fd_, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    }

private:
    int fd_{-1};
};

// Клас високоточного бінарного зондування каналу
class PmtuProber {
public:
    explicit PmtuProber(std::string_view target_ip) {
        socket_.set_dont_fragment();
        socket_.set_timeout(std::chrono::milliseconds(1000));

        std::memset(&dst_addr_, 0, sizeof(dst_addr_));
        dst_addr_.sin_family = AF_INET;
        if (::inet_pton(AF_INET, target_ip.data(), &dst_addr_.sin_addr) <= 0) {
            throw std::invalid_argument("Некоректний формат цільової IP-адреси");
        }
        target_ip_str_ = target_ip;
    }

    std::optional<int> discover(int min_mtu = 576, int max_mtu = 9000) {
        std::cout << "Початок C++20 бінарного зондування Path MTU до " << target_ip_str_ << "...\n";
        int low = min_mtu;
        int high = max_mtu;
        std::optional<int> best_mtu;
        int iteration = 0;

        while (low <= high) {
            iteration++;
            int mid = low + (high - low) / 2;
            std::cout << "  [Ітерація " << iteration << "] Зонд розміром " << mid << " Б... " << std::flush;

            if (send_probe(mid)) {
                std::cout << "OK (Отримано Echo Reply)\n";
                best_mtu = mid;
                low = mid + 1;
            } else {
                std::cout << "DROP / TIMEOUT\n";
                high = mid - 1;
            }
        }
        return best_mtu;
    }

private:
    static uint16_t calculate_checksum(std::span<const uint8_t> data) noexcept {
        uint32_t sum = 0;
        size_t len = data.size();
        const auto* ptr = reinterpret_cast<const uint16_t*>(data.data());

        while (len > 1) {
            sum += *ptr++;
            len -= 2;
        }
        if (len == 1) {
            sum += *reinterpret_cast<const uint8_t*>(ptr);
        }
        sum = (sum >> 16) + (sum & 0xFFFF);
        sum += (sum >> 16);
        return static_cast<uint16_t>(~sum);
    }

    bool send_probe(int total_ip_size) {
        const int icmp_payload_len = total_ip_size - 20 - 8;
        if (icmp_payload_len < 0) return false;

        const size_t packet_len = sizeof(struct icmphdr) + static_cast<size_t>(icmp_payload_len);
        std::vector<uint8_t> packet(packet_len, 0x55);

        auto* icmp = reinterpret_cast<struct icmphdr*>(packet.data());
        icmp->type = ICMP_ECHO;
        icmp->code = 0;
        icmp->un.echo.id = htons(static_cast<uint16_t>(::getpid() & 0xFFFF));
        icmp->un.echo.sequence = htons(static_cast<uint16_t>(total_ip_size));
        icmp->checksum = 0;
        icmp->checksum = calculate_checksum(packet);

        ssize_t sent = ::sendto(socket_.get(), packet.data(), packet.size(), 0,
                                reinterpret_cast<const struct sockaddr*>(&dst_addr_),
                                sizeof(dst_addr_));
        if (sent < 0) {
            return false;
        }

        std::vector<uint8_t> recv_buf(2048);
        struct sockaddr_in from{};
        socklen_t from_len = sizeof(from);

        ssize_t recvd = ::recvfrom(socket_.get(), recv_buf.data(), recv_buf.size(), 0,
                                   reinterpret_cast<struct sockaddr*>(&from), &from_len);
        if (recvd < 0) {
            return false;
        }

        if (static_cast<size_t>(recvd) < sizeof(struct iphdr) + sizeof(struct icmphdr)) {
            return false;
        }

        const auto* ip_rep = reinterpret_cast<const struct iphdr*>(recv_buf.data());
        const size_t ip_hdr_bytes = ip_rep->ihl * 4;

        if (static_cast<size_t>(recvd) < ip_hdr_bytes + sizeof(struct icmphdr)) {
            return false;
        }

        const auto* icmp_rep = reinterpret_cast<const struct icmphdr*>(recv_buf.data() + ip_hdr_bytes);
        return (icmp_rep->type == ICMP_ECHOREPLY &&
                icmp_rep->un.echo.id == htons(static_cast<uint16_t>(::getpid() & 0xFFFF)));
    }

    RawSocket socket_{IPPROTO_ICMP};
    struct sockaddr_in dst_addr_{};
    std::string target_ip_str_;
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Використання: " << argv[0] << " <IP-адреса>\n";
        return 1;
    }

    try {
        PmtuProber prober(argv[1]);
        auto pmtu = prober.discover();

        std::cout << "\n=== Підсумок активного аналізу ===\n";
        if (pmtu) {
            std::cout << "Виявлений Path MTU  = " << *pmtu << " байтів\n"
                      << "Оптимальний TCP MSS = " << (*pmtu - 40) << " байтів\n";
        } else {
            std::cout << "Помилка: канал заблоковано або вузол не відповідає на зонди.\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Критична виняткова ситуація: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
