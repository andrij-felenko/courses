// ospf_sniffer.cpp — ідіоматичний та безпечний парсер OSPFv2 на C++20
#include <iostream>
#include <iomanip>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <expected>
#include <memory>
#include <cstring>
#include <arpa/inet.h>
#include <unistd.h>
#include <sys/socket.h>

enum class OspfType : uint8_t {
    Hello         = 1,
    DatabaseDesc  = 2,
    LinkStateReq  = 3,
    LinkStateUpd  = 4,
    LinkStateAck  = 5
};

constexpr std::string_view to_string(OspfType type) noexcept {
    switch (type) {
        case OspfType::Hello:        return "Hello";
        case OspfType::DatabaseDesc: return "Database Description (DBD)";
        case OspfType::LinkStateReq: return "Link State Request (LSR)";
        case OspfType::LinkStateUpd: return "Link State Update (LSU)";
        case OspfType::LinkStateAck: return "Link State Ack (LSAck)";
    }
    return "Unknown";
}

struct [[gnu::packed]] OspfHeaderLayout {
    uint8_t  version;
    uint8_t  type;
    uint16_t length;
    uint32_t router_id;
    uint32_t area_id;
    uint16_t checksum;
    uint16_t autype;
    uint64_t authentication;
};

struct [[gnu::packed]] OspfHelloLayout {
    uint32_t network_mask;
    uint16_t hello_interval;
    uint8_t  options;
    uint8_t  priority;
    uint32_t dead_interval;
    uint32_t dr;
    uint32_t bdr;
};

struct OspfParsedMessage {
    uint8_t     version;
    OspfType    type;
    uint16_t    length;
    std::string router_id;
    std::string area_id;
    uint16_t    checksum;
    uint16_t    auth_type;
};

class ScopedRawSocket {
    int fd_{-1};
public:
    explicit ScopedRawSocket(int proto) {
        fd_ = ::socket(AF_INET, SOCK_RAW, proto);
    }
    ~ScopedRawSocket() {
        if (fd_ >= 0) ::close(fd_);
    }
    ScopedRawSocket(const ScopedRawSocket&) = delete;
    ScopedRawSocket& operator=(const ScopedRawSocket&) = delete;

    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

std::string format_ipv4(uint32_t net_order_ip) {
    char str_buf[INET_ADDRSTRLEN];
    struct in_addr addr{net_order_ip};
    if (::inet_ntop(AF_INET, &addr, str_buf, sizeof(str_buf))) {
        return str_buf;
    }
    return "0.0.0.0";
}

std::expected<OspfParsedMessage, std::string_view> parse_header(std::span<const uint8_t> bytes) {
    if (bytes.size() < sizeof(OspfHeaderLayout)) {
        return std::unexpected("Розмір пакета менший за обов'язковий заголовок OSPF (24 байти)");
    }

    OspfHeaderLayout raw{};
    std::memcpy(&raw, bytes.data(), sizeof(OspfHeaderLayout));

    return OspfParsedMessage{
        .version   = raw.version,
        .type      = static_cast<OspfType>(raw.type),
        .length    = ntohs(raw.length),
        .router_id = format_ipv4(raw.router_id),
        .area_id   = format_ipv4(raw.area_id),
        .checksum  = ntohs(raw.checksum),
        .auth_type = ntohs(raw.autype)
    };
}

int main() {
    ScopedRawSocket sock(89);
    if (!sock.is_valid()) {
        std::cerr << "Не вдалося відкрити SOCK_RAW (89). Перевірте наявність прав суперкористувача (sudo).
";
        return 1;
    }

    std::cout << "Слухаємо інтерфейси на наявність трафіку OSPF...
";
    std::vector<uint8_t> rx_buffer(4096);

    while (true) {
        ssize_t bytes_read = ::recvfrom(sock.get(), rx_buffer.data(), rx_buffer.size(), 0, nullptr, nullptr);
        if (bytes_read <= 0) continue;

        uint8_t ip_hdr_len = (rx_buffer[0] & 0x0F) * 4;
        if (bytes_read <= ip_hdr_len) continue;

        std::span<const uint8_t> ospf_span(rx_buffer.data() + ip_hdr_len, bytes_read - ip_hdr_len);
        auto parsed = parse_header(ospf_span);

        if (parsed) {
            const auto& msg = *parsed;
            std::cout << "
[OSPFv" << static_cast<int>(msg.version) << " Пакет]
"
                      << "  Тип: " << to_string(msg.type)
                      << " (довжина " << msg.length << " байтів)
"
                      << "  Router ID: " << msg.router_id
                      << " | Area ID: " << msg.area_id << "
"
                      << "  AuthType: " << msg.auth_type
                      << " | Checksum: 0x" << std::hex << std::uppercase << msg.checksum << std::dec << "
";
        } else {
            std::cerr << "Помилка аналізу: " << parsed.error() << "
";
        }
    }
    return 0;
}
