#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <span>
#include <format>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <arpa/inet.h>

namespace net {

// RAII-обгортка для керування життєвим циклом сокетного дескриптора
class UniqueSocket {
public:
    explicit UniqueSocket(int fd = -1) noexcept : fd_{fd} {}
    ~UniqueSocket() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    UniqueSocket(const UniqueSocket&) = delete;
    UniqueSocket& operator=(const UniqueSocket&) = delete;

    UniqueSocket(UniqueSocket&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }
    UniqueSocket& operator=(UniqueSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

private:
    int fd_;
};

// Обчислення контрольної суми RFC 1071 над константним діапазоном пам'яті
[[nodiscard]] constexpr uint16_t compute_checksum(std::span<const uint8_t> bytes) noexcept {
    uint32_t sum = 0;
    size_t i = 0;
    while (i + 1 < bytes.size()) {
        const uint16_t word = static_cast<uint16_t>(bytes[i]) | 
                              (static_cast<uint16_t>(bytes[i + 1]) << 8);
        sum += word;
        i += 2;
    }
    if (i < bytes.size()) {
        sum += static_cast<uint16_t>(bytes[i]);
    }
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return static_cast<uint16_t>(~sum);
}

class TracerouteEngine {
public:
    static constexpr int MaxHops = 30;
    static constexpr int TimeoutMs = 1000;

    explicit TracerouteEngine(std::string target_ip) 
        : target_ip_{std::move(target_ip)} {}

    void execute() {
        sockaddr_in target{};
        target.sin_family = AF_INET;
        if (::inet_pton(AF_INET, target_ip_.c_str(), &target.sin_addr) <= 0) {
            std::cerr << "Некоректна IP-адреса: " << target_ip_ << "\n";
            return;
        }

        UniqueSocket sock{::socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)};
        if (!sock.valid()) {
            std::cerr << "Помилка відкриття SOCK_RAW (потрібен CAP_NET_RAW): " 
                      << std::strerror(errno) << "\n";
            return;
        }

        timeval tv{
            .tv_sec = TimeoutMs / 1000,
            .tv_usec = (TimeoutMs % 1000) * 1000
        };
        if (::setsockopt(sock.get(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
            std::cerr << "Помилка встановлення таймауту сокета\n";
            return;
        }

        const auto pid = static_cast<uint16_t>(::getpid() & 0xFFFF);
        std::cout << "Трасування маршруту до " << target_ip_ 
                  << " (максимум " << MaxHops << " хопів):\n";

        for (int ttl = 1; ttl <= MaxHops; ++ttl) {
            if (::setsockopt(sock.get(), IPPROTO_IP, IP_TTL, &ttl, sizeof(ttl)) < 0) {
                std::cerr << "Помилка setsockopt(IP_TTL)\n";
                break;
            }

            icmphdr req{};
            req.type = ICMP_ECHO;
            req.code = 0;
            req.un.echo.id = htons(pid);
            req.un.echo.sequence = htons(static_cast<uint16_t>(ttl));
            
            auto req_span = std::span<const uint8_t>(
                reinterpret_cast<const uint8_t*>(&req), sizeof(req)
            );
            req.checksum = compute_checksum(req_span);

            const auto start_time = std::chrono::steady_clock::now();

            const auto sent = ::sendto(sock.get(), &req, sizeof(req), 0,
                                       reinterpret_cast<const sockaddr*>(&target), 
                                       sizeof(target));
            if (sent < 0) {
                std::cerr << "Помилка sendto: " << std::strerror(errno) << "\n";
                break;
            }

            std::vector<uint8_t> buffer(512);
            sockaddr_in reply_addr{};
            socklen_t addr_len = sizeof(reply_addr);

            const auto received = ::recvfrom(sock.get(), buffer.data(), buffer.size(), 0,
                                             reinterpret_cast<sockaddr*>(&reply_addr), 
                                             &addr_len);
            const auto end_time = std::chrono::steady_clock::now();

            if (received < 0) {
                if (errno == EAGAIN || errno == EWOULDBLOCK) {
                    std::cout << std::format("{:2d}  * * * (таймаут вузла)\n", ttl);
                    continue;
                }
                std::cerr << "Помилка recvfrom: " << std::strerror(errno) << "\n";
                break;
            }

            const std::chrono::duration<double, std::milli> rtt = end_time - start_time;

            if (static_cast<size_t>(received) < sizeof(iphdr)) {
                continue;
            }

            const auto* ip_hdr = reinterpret_cast<const iphdr*>(buffer.data());
            const size_t ip_hdr_bytes = ip_hdr->ihl * 4;
            if (static_cast<size_t>(received) < ip_hdr_bytes + sizeof(icmphdr)) {
                continue;
            }

            const auto* icmp_reply = reinterpret_cast<const icmphdr*>(buffer.data() + ip_hdr_bytes);
            char ip_str[INET_ADDRSTRLEN]{};
            ::inet_ntop(AF_INET, &reply_addr.sin_addr, ip_str, sizeof(ip_str));

            if (icmp_reply->type == ICMP_TIME_EXCEEDED && icmp_reply->code == 0) {
                std::cout << std::format("{:2d}  {:15s}  {:.3f} ms\n", ttl, ip_str, rtt.count());
            } else if (icmp_reply->type == ICMP_ECHOREPLY) {
                std::cout << std::format("{:2d}  {:15s}  {:.3f} ms (досягнуто призначення)\n", ttl, ip_str, rtt.count());
                break;
            } else {
                std::cout << std::format("{:2d}  {:15s}  ICMP type={} code={}  {:.3f} ms\n",
                                         ttl, ip_str, icmp_reply->type, icmp_reply->code, rtt.count());
            }
        }
    }

private:
    std::string target_ip_;
};

} // namespace net

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Використання: " << argv[0] << " <IPv4-адреса>\n";
        return EXIT_FAILURE;
    }

    net::TracerouteEngine engine{argv[1]};
    engine.execute();
    return EXIT_SUCCESS;
}
