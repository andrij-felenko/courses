#include <iostream>
#include <vector>
#include <span>
#include <array>
#include <optional>
#include <cstdint>
#include <cstring>
#include <arpa/inet.h>

inline constexpr size_t DHCP_CHADDR_LEN     = 16;
inline constexpr size_t DHCP_SNAME_LEN      = 64;
inline constexpr size_t DHCP_FILE_LEN       = 128;
inline constexpr uint32_t DHCP_MAGIC_COOKIE = 0x63825363;

enum class DhcpOptionCode : uint8_t {
    Pad              = 0,
    SubnetMask       = 1,
    Router           = 3,
    DnsServer        = 6,
    HostName         = 12,
    DomainName       = 15,
    RequestedIp      = 50,
    LeaseTime        = 51,
    MessageType      = 53,
    ServerIdentifier = 54,
    ParamRequestList = 55,
    ClientIdentifier = 61,
    End              = 255
};

enum class DhcpMessageType : uint8_t {
    Discover = 1,
    Offer    = 2,
    Request  = 3,
    Decline  = 4,
    Ack      = 5,
    Nak      = 6,
    Release  = 7,
    Inform   = 8
};

#pragma pack(push, 1)
struct DhcpPacketHeader {
    uint8_t  op;
    uint8_t  htype;
    uint8_t  hlen;
    uint8_t  hops;
    uint32_t xid;
    uint16_t secs;
    uint16_t flags;
    uint32_t ciaddr;
    uint32_t yiaddr;
    uint32_t siaddr;
    uint32_t giaddr;
    std::array<uint8_t, DHCP_CHADDR_LEN> chaddr;
    std::array<char, DHCP_SNAME_LEN>     sname;
    std::array<char, DHCP_FILE_LEN>      file;
    uint32_t magic_cookie;
};
#pragma pack(pop)

struct DhcpOfferInfo {
    uint32_t xid{0};
    uint32_t offered_ip{0};
    uint32_t server_ip{0};
    uint32_t subnet_mask{0};
    uint32_t router_ip{0};
    uint32_t dns_ip{0};
    uint32_t lease_time{0};
    DhcpMessageType msg_type{DhcpMessageType::Discover};
};

class DhcpMessageBuilder {
public:
    static std::vector<uint8_t> create_discover(std::span<const uint8_t, 6> mac, uint32_t xid) {
        std::vector<uint8_t> buffer(sizeof(DhcpPacketHeader), 0);
        auto* hdr = reinterpret_cast<DhcpPacketHeader*>(buffer.data());

        hdr->op = 1; // BOOTREQUEST
        hdr->htype = 1; // Ethernet
        hdr->hlen = 6;
        hdr->hops = 0;
        hdr->xid = htonl(xid);
        hdr->secs = htons(0);
        hdr->flags = htons(0x8000); // Broadcast Flag
        std::memcpy(hdr->chaddr.data(), mac.data(), 6);
        hdr->magic_cookie = htonl(DHCP_MAGIC_COOKIE);

        add_option(buffer, DhcpOptionCode::MessageType, std::array<uint8_t, 1>{static_cast<uint8_t>(DhcpMessageType::Discover)});

        std::array<uint8_t, 7> client_id{1}; // Type 1: Ethernet
        std::memcpy(client_id.data() + 1, mac.data(), 6);
        add_option(buffer, DhcpOptionCode::ClientIdentifier, client_id);

        std::array<uint8_t, 4> req_params{
            static_cast<uint8_t>(DhcpOptionCode::SubnetMask),
            static_cast<uint8_t>(DhcpOptionCode::Router),
            static_cast<uint8_t>(DhcpOptionCode::DnsServer),
            static_cast<uint8_t>(DhcpOptionCode::DomainName)
        };
        add_option(buffer, DhcpOptionCode::ParamRequestList, req_params);

        buffer.push_back(static_cast<uint8_t>(DhcpOptionCode::End));
        return buffer;
    }

private:
    static void add_option(std::vector<uint8_t>& buf, DhcpOptionCode code, std::span<const uint8_t> data) {
        buf.push_back(static_cast<uint8_t>(code));
        buf.push_back(static_cast<uint8_t>(data.size()));
        buf.insert(buf.end(), data.begin(), data.end());
    }
};

class DhcpMessageParser {
public:
    static std::optional<DhcpOfferInfo> parse(std::span<const uint8_t> packet,
                                              std::span<const uint8_t, 6> expected_mac,
                                              uint32_t expected_xid) {
        if (packet.size() < sizeof(DhcpPacketHeader)) {
            return std::nullopt;
        }

        const auto* hdr = reinterpret_cast<const DhcpPacketHeader*>(packet.data());
        if (hdr->op != 2) return std::nullopt;
        if (ntohl(hdr->xid) != expected_xid) return std::nullopt;
        if (std::memcmp(hdr->chaddr.data(), expected_mac.data(), 6) != 0) return std::nullopt;
        if (ntohl(hdr->magic_cookie) != DHCP_MAGIC_COOKIE) return std::nullopt;

        DhcpOfferInfo info;
        info.xid = ntohl(hdr->xid);
        info.offered_ip = ntohl(hdr->yiaddr);

        size_t offset = sizeof(DhcpPacketHeader);
        while (offset < packet.size()) {
            uint8_t code = packet[offset++];
            if (code == static_cast<uint8_t>(DhcpOptionCode::Pad)) continue;
            if (code == static_cast<uint8_t>(DhcpOptionCode::End)) break;

            if (offset >= packet.size()) return std::nullopt;
            uint8_t len = packet[offset++];

            if (offset + len > packet.size()) return std::nullopt;

            auto val = packet.subspan(offset, len);
            auto opt = static_cast<DhcpOptionCode>(code);

            switch (opt) {
                case DhcpOptionCode::MessageType:
                    if (val.size() >= 1) info.msg_type = static_cast<DhcpMessageType>(val[0]);
                    break;
                case DhcpOptionCode::ServerIdentifier:
                    if (val.size() >= 4) {
                        uint32_t raw;
                        std::memcpy(&raw, val.data(), 4);
                        info.server_ip = ntohl(raw);
                    }
                    break;
                case DhcpOptionCode::SubnetMask:
                    if (val.size() >= 4) {
                        uint32_t raw;
                        std::memcpy(&raw, val.data(), 4);
                        info.subnet_mask = ntohl(raw);
                    }
                    break;
                case DhcpOptionCode::Router:
                    if (val.size() >= 4) {
                        uint32_t raw;
                        std::memcpy(&raw, val.data(), 4);
                        info.router_ip = ntohl(raw);
                    }
                    break;
                case DhcpOptionCode::DnsServer:
                    if (val.size() >= 4) {
                        uint32_t raw;
                        std::memcpy(&raw, val.data(), 4);
                        info.dns_ip = ntohl(raw);
                    }
                    break;
                case DhcpOptionCode::LeaseTime:
                    if (val.size() >= 4) {
                        uint32_t raw;
                        std::memcpy(&raw, val.data(), 4);
                        info.lease_time = ntohl(raw);
                    }
                    break;
                default:
                    break;
            }

            offset += len;
        }

        return info;
    }
};

int main() {
    std::array<uint8_t, 6> mac = {0x00, 0x1A, 0x2B, 0x3C, 0x4D, 0x5E};
    uint32_t xid = 0x39A4F2B1;

    auto discover_pkt = DhcpMessageBuilder::create_discover(mac, xid);
    std::cout << "Сформовано DHCPDISCOVER (C++20), розмір: " << discover_pkt.size() << " байтів.\n";

    return 0;
}
