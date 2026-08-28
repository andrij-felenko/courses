#include <iostream>
#include <string_view>
#include <array>
#include <span>
#include <vector>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

namespace mdns {

constexpr uint16_t MDNS_PORT = 5353;
constexpr std::string_view MDNS_MULTICAST_IPV4 = "224.0.0.251";
constexpr size_t BUFFER_SIZE = 1472;

enum class DnsType : uint16_t {
    A = 1,
    PTR = 12,
    TXT = 16,
    AAAA = 28,
    SRV = 33,
    ANY = 255
};

enum class DnsClass : uint16_t {
    IN = 1
};

constexpr uint16_t CACHE_FLUSH_BIT = 0x8000;

#pragma pack(push, 1)
struct DnsHeader {
    uint16_t id{0};
    uint16_t flags{0};
    uint16_t qdcount{0};
    uint16_t ancount{0};
    uint16_t nscount{0};
    uint16_t arcount{0};
};
#pragma pack(pop)

struct ServiceConfig {
    std::string_view hostname;
    std::string_view service_type;
    std::string_view instance_name;
    uint16_t port{80};
    uint32_t ipv4_addr{0};
    std::vector<std::string_view> txt_records;
};

// RAII обгортка для файлового дескриптора сокета
class UniqueSocket {
public:
    UniqueSocket() = default;
    explicit UniqueSocket(int fd) : fd_(fd) {}
    ~UniqueSocket() { reset(); }

    UniqueSocket(const UniqueSocket&) = delete;
    UniqueSocket& operator=(const UniqueSocket&) = delete;

    UniqueSocket(UniqueSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    UniqueSocket& operator=(UniqueSocket&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void reset() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
        }
    }

private:
    int fd_{-1};
};

class MdnsResponder {
public:
    explicit MdnsResponder(ServiceConfig config)
        : config_(std::move(config)) {
        setup_socket();
    }

    void send_announcement(uint32_t ttl) {
        size_t len = build_announcement(ttl, tx_buf_);
        if (len > 0) {
            ::sendto(sock_.get(), tx_buf_.data(), len, 0,
                     reinterpret_cast<const sockaddr*>(&mcast_addr_), sizeof(mcast_addr_));
        }
    }

    void process_incoming(std::span<const uint8_t> packet) {
        if (packet.size() < sizeof(DnsHeader)) return;
        const auto* hdr = reinterpret_cast<const DnsHeader*>(packet.data());

        // Ігноруємо власні відповіді (QR=1)
        if (ntohs(hdr->flags) & 0x8000) return;
        if (ntohs(hdr->qdcount) == 0) return;

        send_announcement(4500);
    }

    void run(int duration_seconds) {
        std::cout << "mDNS респондер C++ запущено: " << config_.hostname 
                  << ".local -> " << config_.instance_name << "." << config_.service_type << ".local\n";

        // Фаза анонсування: 2 пакети з інтервалом 1 с
        send_announcement(4500);
        ::sleep(1);
        send_announcement(4500);

        pollfd pfd{ .fd = sock_.get(), .events = POLLIN, .revents = 0 };
        for (int i = 0; i < duration_seconds; ++i) {
            int ret = ::poll(&pfd, 1, 1000);
            if (ret > 0 && (pfd.revents & POLLIN)) {
                ssize_t n = ::recvfrom(sock_.get(), rx_buf_.data(), rx_buf_.size(), 0, nullptr, nullptr);
                if (n > 0) {
                    process_incoming(std::span<const uint8_t>(rx_buf_.data(), static_cast<size_t>(n)));
                }
            }
        }

        std::cout << "Надсилання Good-bye пакету (TTL = 0)...\n";
        send_announcement(0);
    }

private:
    void setup_socket() {
        int fd = ::socket(AF_INET, SOCK_DGRAM, 0);
        if (fd < 0) throw std::runtime_error("Не вдалося створити UDP-сокет");
        sock_ = UniqueSocket(fd);

        int reuse = 1;
        ::setsockopt(sock_.get(), SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));
#ifdef SO_REUSEPORT
        ::setsockopt(sock_.get(), SOL_SOCKET, SO_REUSEPORT, &reuse, sizeof(reuse));
#endif

        sockaddr_in bind_addr{};
        bind_addr.sin_family = AF_INET;
        bind_addr.sin_port = htons(MDNS_PORT);
        bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);

        if (::bind(sock_.get(), reinterpret_cast<const sockaddr*>(&bind_addr), sizeof(bind_addr)) < 0) {
            throw std::runtime_error("Помилка bind на порт 5353");
        }

        ip_mreq mreq{};
        mreq.imr_multiaddr.s_addr = ::inet_addr(MDNS_MULTICAST_IPV4.data());
        mreq.imr_interface.s_addr = config_.ipv4_addr;

        if (::setsockopt(sock_.get(), IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
            mreq.imr_interface.s_addr = htonl(INADDR_ANY);
            if (::setsockopt(sock_.get(), IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
                throw std::runtime_error("Помилка IP_ADD_MEMBERSHIP");
            }
        }

        uint8_t ttl = 255;
        ::setsockopt(sock_.get(), IPPROTO_IP, IP_MULTICAST_TTL, &ttl, sizeof(ttl));

        std::memset(&mcast_addr_, 0, sizeof(mcast_addr_));
        mcast_addr_.sin_family = AF_INET;
        mcast_addr_.sin_port = htons(MDNS_PORT);
        mcast_addr_.sin_addr.s_addr = ::inet_addr(MDNS_MULTICAST_IPV4.data());
    }

    static size_t write_label(std::span<uint8_t> buf, size_t offset, std::string_view label) {
        if (offset + label.size() + 1 >= buf.size() || label.size() > 63) return 0;
        buf[offset++] = static_cast<uint8_t>(label.size());
        std::memcpy(&buf[offset], label.data(), label.size());
        return label.size() + 1;
    }

    static size_t write_domain(std::span<uint8_t> buf, size_t offset, std::string_view domain) {
        size_t written = 0;
        size_t start = 0;
        while (start < domain.size()) {
            size_t dot = domain.find('.', start);
            std::string_view part = (dot == std::string_view::npos) 
                ? domain.substr(start) 
                : domain.substr(start, dot - start);
            size_t n = write_label(buf, offset + written, part);
            if (n == 0) return 0;
            written += n;
            if (dot == std::string_view::npos) break;
            start = dot + 1;
        }
        if (offset + written >= buf.size()) return 0;
        buf[offset + written++] = 0x00;
        return written;
    }

    size_t build_announcement(uint32_t ttl, std::span<uint8_t> buf) {
        if (buf.size() < sizeof(DnsHeader)) return 0;

        auto* hdr = reinterpret_cast<DnsHeader*>(buf.data());
        hdr->id = 0;
        hdr->flags = htons(0x8400); // QR=1, AA=1
        hdr->qdcount = 0;
        hdr->ancount = htons(1);
        hdr->nscount = 0;
        hdr->arcount = htons(3);

        size_t cur = sizeof(DnsHeader);

        // 1. Answer: PTR
        size_t ptr_service_offset = cur;
        std::string service_fqdn = std::string(config_.service_type) + ".local";
        cur += write_domain(buf, cur, service_fqdn);

        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsType::PTR)); cur += 2;
        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsClass::IN)); cur += 2;
        *reinterpret_cast<uint32_t*>(&buf[cur]) = htonl(ttl); cur += 4;

        size_t rdlen_pos_ptr = cur; cur += 2;
        size_t rdata_start_ptr = cur;

        size_t instance_fqdn_offset = cur;
        cur += write_label(buf, cur, config_.instance_name);
        buf[cur++] = 0xC0 | static_cast<uint8_t>(ptr_service_offset >> 8);
        buf[cur++] = static_cast<uint8_t>(ptr_service_offset & 0xFF);
        *reinterpret_cast<uint16_t*>(&buf[rdlen_pos_ptr]) = htons(static_cast<uint16_t>(cur - rdata_start_ptr));

        // 2. Additional: SRV
        buf[cur++] = 0xC0 | static_cast<uint8_t>(instance_fqdn_offset >> 8);
        buf[cur++] = static_cast<uint8_t>(instance_fqdn_offset & 0xFF);

        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsType::SRV)); cur += 2;
        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsClass::IN) | CACHE_FLUSH_BIT); cur += 2;
        *reinterpret_cast<uint32_t*>(&buf[cur]) = htonl(ttl); cur += 4;

        size_t rdlen_pos_srv = cur; cur += 2;
        size_t rdata_start_srv = cur;

        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(0); cur += 2; // Priority
        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(0); cur += 2; // Weight
        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(config_.port); cur += 2; // Port

        size_t host_fqdn_offset = cur;
        std::string host_fqdn = std::string(config_.hostname) + ".local";
        cur += write_domain(buf, cur, host_fqdn);
        *reinterpret_cast<uint16_t*>(&buf[rdlen_pos_srv]) = htons(static_cast<uint16_t>(cur - rdata_start_srv));

        // 3. Additional: TXT
        buf[cur++] = 0xC0 | static_cast<uint8_t>(instance_fqdn_offset >> 8);
        buf[cur++] = static_cast<uint8_t>(instance_fqdn_offset & 0xFF);

        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsType::TXT)); cur += 2;
        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsClass::IN) | CACHE_FLUSH_BIT); cur += 2;
        *reinterpret_cast<uint32_t*>(&buf[cur]) = htonl(ttl); cur += 4;

        size_t rdlen_pos_txt = cur; cur += 2;
        size_t rdata_start_txt = cur;

        for (const auto& attr : config_.txt_records) {
            if (attr.size() > 255 || cur + attr.size() + 1 >= buf.size()) break;
            buf[cur++] = static_cast<uint8_t>(attr.size());
            std::memcpy(&buf[cur], attr.data(), attr.size());
            cur += attr.size();
        }
        if (cur == rdata_start_txt) buf[cur++] = 0x00;
        *reinterpret_cast<uint16_t*>(&buf[rdlen_pos_txt]) = htons(static_cast<uint16_t>(cur - rdata_start_txt));

        // 4. Additional: A
        buf[cur++] = 0xC0 | static_cast<uint8_t>(host_fqdn_offset >> 8);
        buf[cur++] = static_cast<uint8_t>(host_fqdn_offset & 0xFF);

        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsType::A)); cur += 2;
        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsClass::IN) | CACHE_FLUSH_BIT); cur += 2;
        *reinterpret_cast<uint32_t*>(&buf[cur]) = htonl(120); cur += 4; // Host TTL: 120s
        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(4); cur += 2;
        *reinterpret_cast<uint32_t*>(&buf[cur]) = config_.ipv4_addr; cur += 4;

        return cur;
    }

    ServiceConfig config_;
    UniqueSocket sock_;
    sockaddr_in mcast_addr_{};
    std::array<uint8_t, BUFFER_SIZE> rx_buf_{};
    std::array<uint8_t, BUFFER_SIZE> tx_buf_{};
};

} // namespace mdns

int main() {
    try {
        mdns::ServiceConfig config{
            .hostname = "sensor-node",
            .service_type = "_http._tcp",
            .instance_name = "Embedded Sensor C++",
            .port = 80,
            .ipv4_addr = ::inet_addr("192.168.1.120"),
            .txt_records = {"model=BME280", "firmware=2.1.0-cpp"}
        };

        mdns::MdnsResponder responder(config);
        responder.run(30);
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
