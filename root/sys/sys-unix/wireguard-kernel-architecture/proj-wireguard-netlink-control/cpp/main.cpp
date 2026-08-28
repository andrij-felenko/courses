#include <iostream>
#include <vector>
#include <string_view>
#include <array>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>
#include <arpa/inet.h>

namespace wireguard {

constexpr std::string_view WG_GENL_NAME = "wireguard";
constexpr uint8_t WG_GENL_VERSION = 1;

enum class WgCmd : uint8_t {
    GetDevice = 0,
    SetDevice = 1
};

enum WgDeviceAttr {
    WgDeviceAttrIfName = 2,
    WgDeviceAttrPeers = 8
};

enum WgPeerAttr {
    WgPeerAttrPublicKey = 1,
    WgPeerAttrEndpoint = 3,
    WgPeerAttrAllowedIps = 6
};

enum WgAllowedIpAttr {
    WgAllowedIpAttrFamily = 1,
    WgAllowedIpAttrIpAddr = 2,
    WgAllowedIpAttrCidrMask = 3
};

// RAII-обгортка для управління ресурсом Netlink сокету
class NetlinkSocket {
    int fd_{-1};
public:
    NetlinkSocket() {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити NETLINK_GENERIC сокет");
        }
        sockaddr_nl local{};
        local.nl_family = AF_NETLINK;
        if (::bind(fd_, reinterpret_cast<sockaddr*>(&local), sizeof(local)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Не вдалося прив'язати Netlink сокет");
        }
    }

    ~NetlinkSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;

    [[nodiscard]] int get() const noexcept { return fd_; }
};

// Динамічний буфер для формування повідомлення Netlink
class NetlinkBuffer {
    std::vector<uint8_t> buffer_;

public:
    explicit NetlinkBuffer(size_t initial_capacity = 4096) {
        buffer_.reserve(initial_capacity);
        buffer_.resize(NLMSG_LENGTH(sizeof(genlmsghdr)), 0);
        
        auto* nlh = reinterpret_cast<nlmsghdr*>(buffer_.data());
        nlh->nlmsg_len = NLMSG_LENGTH(sizeof(genlmsghdr));
        nlh->nlmsg_type = 0x10; // Символічний WireGuard Generic Netlink ID
        nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
        nlh->nlmsg_seq = 1;

        auto* genl = reinterpret_cast<genlmsghdr*>(NLMSG_DATA(nlh));
        genl->cmd = static_cast<uint8_t>(WgCmd::SetDevice);
        genl->version = WG_GENL_VERSION;
    }

    void add_attribute(uint16_t type, const void* data, uint16_t len) {
        auto* nlh = reinterpret_cast<nlmsghdr*>(buffer_.data());
        uint16_t rta_len = RTA_LENGTH(len);
        size_t old_size = buffer_.size();
        size_t aligned_len = RTA_ALIGN(rta_len);

        buffer_.resize(old_size + aligned_len, 0);
        auto* rta = reinterpret_cast<rtattr*>(buffer_.data() + old_size);
        rta->rta_type = type;
        rta->rta_len = rta_len;
        if (data && len > 0) {
            std::memcpy(RTA_DATA(rta), data, len);
        }

        nlh->nlmsg_len = static_cast<uint32_t>(buffer_.size());
    }

    [[nodiscard]] size_t start_nested(uint16_t type) {
        size_t offset = buffer_.size();
        add_attribute(type | NLA_F_NESTED, nullptr, 0);
        return offset;
    }

    void end_nested(size_t offset) {
        auto* rta = reinterpret_cast<rtattr*>(buffer_.data() + offset);
        rta->rta_len = static_cast<uint16_t>(buffer_.size() - offset);
    }

    [[nodiscard]] const uint8_t* data() const noexcept { return buffer_.data(); }
    [[nodiscard]] size_t size() const noexcept { return buffer_.size(); }
};

} // namespace wireguard

int main() {
    try {
        wireguard::NetlinkSocket sock;
        wireguard::NetlinkBuffer msg;

        // Вказуємо ім'я тунельного пристрою wg0
        std::string_view ifname = "wg0";
        msg.add_attribute(wireguard::WgDeviceAttrIfName, ifname.data(), static_cast<uint16_t>(ifname.size() + 1));

        // Створюємо вкладений блок пірів
        size_t peers_nest = msg.start_nested(wireguard::WgDeviceAttrPeers);
        size_t peer_nest = msg.start_nested(0);

        // Передаємо 32-байтний публічний ключ піра
        std::array<uint8_t, 32> pubkey = {
            0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
            0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10,
            0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18,
            0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20
        };
        msg.add_attribute(wireguard::WgPeerAttrPublicKey, pubkey.data(), pubkey.size());

        // Зовнішній endpoint 192.168.1.100:51820
        sockaddr_in ep{};
        ep.sin_family = AF_INET;
        ep.sin_port = htons(51820);
        inet_pton(AF_INET, "192.168.1.100", &ep.sin_addr);
        msg.add_attribute(wireguard::WgPeerAttrEndpoint, &ep, sizeof(ep));

        // Allowed IPs (10.0.0.2/32)
        size_t aips_nest = msg.start_nested(wireguard::WgPeerAttrAllowedIps);
        size_t aip_nest = msg.start_nested(0);

        uint16_t family = AF_INET;
        in_addr ip_addr{};
        inet_pton(AF_INET, "10.0.0.2", &ip_addr);
        uint8_t cidr = 32;

        msg.add_attribute(wireguard::WgAllowedIpAttrFamily, &family, sizeof(family));
        msg.add_attribute(wireguard::WgAllowedIpAttrIpAddr, &ip_addr, sizeof(ip_addr));
        msg.add_attribute(wireguard::WgAllowedIpAttrCidrMask, &cidr, sizeof(cidr));

        msg.end_nested(aip_nest);
        msg.end_nested(aips_nest);

        msg.end_nested(peer_nest);
        msg.end_nested(peers_nest);

        sockaddr_nl nl_kernel{};
        nl_kernel.nl_family = AF_NETLINK;

        if (::sendto(sock.get(), msg.data(), msg.size(), 0, reinterpret_cast<sockaddr*>(&nl_kernel), sizeof(nl_kernel)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка sendto до ядра");
        }

        std::cout << "Приклад C++ успішно сформував та надіслав конфігурацію WireGuard через Netlink\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
