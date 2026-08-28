#include <iostream>
#include <array>
#include <span>
#include <string>
#include <string_view>
#include <expected>
#include <random>
#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netdb.h>

namespace net::p2p {

inline constexpr uint32_t STUN_MAGIC_COOKIE = 0x2112A442;
inline constexpr uint16_t STUN_BINDING_REQ   = 0x0001;
inline constexpr uint16_t STUN_BINDING_RESP  = 0x0101;
inline constexpr uint16_t ATTR_XOR_MAPPED_ADDR = 0x0020;

struct Endpoint {
    std::string ip;
    uint16_t port{0};
};

#pragma pack(push, 1)
struct StunHeader {
    uint16_t msg_type;
    uint16_t msg_length;
    uint32_t magic_cookie;
    std::array<uint8_t, 12> transaction_id;
};

struct StunAttr {
    uint16_t type;
    uint16_t length;
};
#pragma pack(pop)

/* RAII-клас для безпечного володіння та управління сокетом */
class UdpSocket {
    int fd_{-1};
public:
    UdpSocket() : fd_(::socket(AF_INET, SOCK_DGRAM, 0)) {}
    ~UdpSocket() {
        if (fd_ >= 0) ::close(fd_);
    }
    UdpSocket(const UdpSocket&) = delete;
    UdpSocket& operator=(const UdpSocket&) = delete;
    UdpSocket(UdpSocket&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool isValid() const noexcept { return fd_ >= 0; }

    bool bind(uint16_t port) {
        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port);
        return ::bind(fd_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == 0;
    }
};

class StunClient {
public:
    static std::expected<Endpoint, std::string> queryReflexive(const UdpSocket& sock,
                                                               std::string_view host,
                                                               uint16_t port) {
        addrinfo hints{}, *res = nullptr;
        hints.ai_family = AF_INET;
        hints.ai_socktype = SOCK_DGRAM;

        if (::getaddrinfo(host.data(), std::to_string(port).c_str(), &hints, &res) != 0 || !res) {
            return std::unexpected("Не вдалося розв'язати DNS-ім'я STUN-сервера");
        }

        StunHeader req{};
        req.msg_type = htons(STUN_BINDING_REQ);
        req.msg_length = htons(0);
        req.magic_cookie = htonl(STUN_MAGIC_COOKIE);

        std::random_device rd;
        for (auto& b : req.transaction_id) {
            b = static_cast<uint8_t>(rd() & 0xFF);
        }

        if (::sendto(sock.get(), &req, sizeof(req), 0, res->ai_addr, res->ai_addrlen) < 0) {
            ::freeaddrinfo(res);
            return std::unexpected("Помилка надсилання STUN Binding Request");
        }
        ::freeaddrinfo(res);

        std::array<uint8_t, 512> buffer{};
        sockaddr_in from{};
        socklen_t from_len = sizeof(from);

        ssize_t n = ::recvfrom(sock.get(), buffer.data(), buffer.size(), 0,
                               reinterpret_cast<sockaddr*>(&from), &from_len);
        if (n < static_cast<ssize_t>(sizeof(StunHeader))) {
            return std::unexpected("Отримано занадто коротку або пошкоджену відповідь");
        }

        const auto* resp = reinterpret_cast<const StunHeader*>(buffer.data());
        if (ntohs(resp->msg_type) != STUN_BINDING_RESP ||
            ntohl(resp->magic_cookie) != STUN_MAGIC_COOKIE ||
            resp->transaction_id != req.transaction_id) {
            return std::unexpected("Помилка автентифікації або незбіг Transaction ID STUN");
        }

        size_t offset = sizeof(StunHeader);
        size_t total = sizeof(StunHeader) + ntohs(resp->msg_length);

        while (offset + sizeof(StunAttr) <= total && offset + sizeof(StunAttr) <= static_cast<size_t>(n)) {
            const auto* attr = reinterpret_cast<const StunAttr*>(buffer.data() + offset);
            uint16_t type = ntohs(attr->type);
            uint16_t len = ntohs(attr->length);
            offset += sizeof(StunAttr);

            if (type == ATTR_XOR_MAPPED_ADDR && len >= 8) {
                uint8_t family = buffer[offset + 1];
                if (family == 0x01) { /* IPv4 */
                    uint16_t raw_port;
                    uint32_t raw_addr;
                    std::memcpy(&raw_port, buffer.data() + offset + 2, 2);
                    std::memcpy(&raw_addr, buffer.data() + offset + 4, 4);

                    uint16_t mapped_port = ntohs(raw_port) ^ (STUN_MAGIC_COOKIE >> 16);
                    uint32_t mapped_addr = ntohl(raw_addr) ^ STUN_MAGIC_COOKIE;

                    in_addr in{};
                    in.s_addr = htonl(mapped_addr);
                    char ip_buf[INET_ADDRSTRLEN];
                    ::inet_ntop(AF_INET, &in, ip_buf, sizeof(ip_buf));

                    return Endpoint{std::string(ip_buf), mapped_port};
                }
            }
            offset += (len + 3) & ~3;
        }

        return std::unexpected("Атрибут XOR-MAPPED-ADDRESS не знайдено у відповіді");
    }

    static bool punchHole(const UdpSocket& sock, std::string_view peer_ip, uint16_t peer_port) {
        sockaddr_in peer_addr{};
        peer_addr.sin_family = AF_INET;
        peer_addr.sin_port = htons(peer_port);
        if (::inet_pton(AF_INET, peer_ip.data(), &peer_addr.sin_addr) <= 0) {
            return false;
        }

        constexpr std::string_view ping_msg = "HOLE_PUNCH_PING";
        for (int i = 0; i < 5; ++i) {
            ::sendto(sock.get(), ping_msg.data(), ping_msg.size(), 0,
                     reinterpret_cast<const sockaddr*>(&peer_addr), sizeof(peer_addr));
            ::usleep(100000);
        }
        return true;
    }
};

} // namespace net::p2p

int main(int argc, char* argv[]) {
    using namespace net::p2p;

    UdpSocket sock;
    if (!sock.isValid() || !sock.bind(50000)) {
        std::cerr << "Помилка створення або прив'язки UDP-сокета\n";
        return 1;
    }

    std::cout << "[STUN C++20] Запит рефлексивної адреси через stun1.l.google.com:19302...\n";
    auto result = StunClient::queryReflexive(sock, "stun1.l.google.com", 19302);

    if (result) {
        std::cout << "[STUN C++20] Успіх! Публічний сокет: "
                  << result->ip << ":" << result->port << "\n";
    } else {
        std::cerr << "[STUN C++20] Помилка: " << result.error() << "\n";
    }

    if (argc >= 3) {
        std::string_view peer_ip = argv[1];
        uint16_t peer_port = static_cast<uint16_t>(std::stoi(argv[2]));
        std::cout << "[P2P C++20] Початок UDP Hole Punching до " << peer_ip << ":" << peer_port << "...\n";
        if (StunClient::punchHole(sock, peer_ip, peer_port)) {
            std::cout << "[P2P C++20] Пробні пакети надіслано. Канал готовий.\n";
        }
    }

    return 0;
}
