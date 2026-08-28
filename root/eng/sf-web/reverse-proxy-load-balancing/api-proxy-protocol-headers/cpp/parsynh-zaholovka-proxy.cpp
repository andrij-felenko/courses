#include <string>
#include <optional>
#include <span>
#include <cstring>
#include <arpa/inet.h>

struct ClientConnectionContext {
    std::string ip;
    uint16_t port{0};
};

std::optional<ClientConnectionContext> parse_proxy_v2_cpp(std::span<const uint8_t> buffer) {
    constexpr std::array<uint8_t, 12> MagicSig = {
        0x0D, 0x0A, 0x0D, 0x0A, 0x00, 0x0D, 0x0A, 0x51, 0x55, 0x49, 0x54, 0x0A
    };

    if (buffer.size() < 16) return std::nullopt;

    if (std::memcmp(buffer.data(), MagicSig.data(), MagicSig.size()) != 0) {
        return std::nullopt;
    }

    uint8_t ver = (buffer[12] >> 4) & 0x0F;
    if (ver != 2) return std::nullopt;

    uint8_t cmd = buffer[12] & 0x0F;
    if (cmd == 0x00) return ClientConnectionContext{"127.0.0.1", 0}; // LOCAL
    if (cmd != 0x01) return std::nullopt;

    uint8_t fam = (buffer[13] >> 4) & 0x0F;
    uint16_t payload_len = (static_cast<uint16_t>(buffer[14]) << 8) | buffer[15];
    if (buffer.size() < 16 + payload_len) return std::nullopt;

    const auto* hdr = reinterpret_cast<const ProxyHeaderV2*>(buffer.data());

    ClientConnectionContext ctx;
    if (fam == 0x01) { // IPv4
        char ip_str[INET_ADDRSTRLEN];
        in_addr in{hdr->addr.ipv4.src_addr};
        ::inet_ntop(AF_INET, &in, ip_str, sizeof(ip_str));
        ctx.ip = ip_str;
        ctx.port = ::ntohs(hdr->addr.ipv4.src_port);
        return ctx;
    } else if (fam == 0x02) { // IPv6
        char ip_str[INET6_ADDRSTRLEN];
        ::inet_ntop(AF_INET6, hdr->addr.ipv6.src_addr.data(), ip_str, sizeof(ip_str));
        ctx.ip = ip_str;
        ctx.port = ::ntohs(hdr->addr.ipv6.src_port);
        return ctx;
    }

    return std::nullopt;
}
