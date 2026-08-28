// bridge_fdb_inject.cpp - Ідіоматична C++ реалізація керування FDB моста
#include <iostream>
#include <vector>
#include <array>
#include <string>
#include <string_view>
#include <format>
#include <expected>
#include <system_error>
#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/rtnetlink.h>
#include <linux/if_bridge.h>
#include <linux/neighbour.h>
#include <net/if.h>

class NetlinkSocket {
public:
    NetlinkSocket() {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "socket(AF_NETLINK) failed");
        }
    }

    ~NetlinkSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;
    NetlinkSocket(NetlinkSocket&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    NetlinkSocket& operator=(NetlinkSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    int native_handle() const noexcept { return fd_; }

private:
    int fd_{-1};
};

struct MacAddress {
    std::array<uint8_t, 6> bytes{};

    static std::expected<MacAddress, std::string> from_string(std::string_view str) {
        MacAddress mac;
        int parsed = std::sscanf(str.data(), "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx",
                                 &mac.bytes[0], &mac.bytes[1], &mac.bytes[2],
                                 &mac.bytes[3], &mac.bytes[4], &mac.bytes[5]);
        if (parsed != 6) {
            return std::unexpected("Invalid MAC format, expected XX:XX:XX:XX:XX:XX");
        }
        return mac;
    }
};

class BridgeController {
public:
    static std::expected<void, std::error_code> add_static_fdb(
        std::string_view ifname,
        const MacAddress& mac,
        uint16_t vid = 0)
    {
        unsigned int ifindex = ::if_nametoindex(ifname.data());
        if (ifindex == 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
        }

        NetlinkSocket nl_sock;
        std::vector<uint8_t> buffer(4096, 0);

        auto* nlh = reinterpret_cast<struct nlmsghdr*>(buffer.data());
        nlh->nlmsg_len = NLMSG_LENGTH(sizeof(struct ndmsg));
        nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_REPLACE | NLM_F_ACK;
        nlh->nlmsg_type = RTM_NEWNEIGH;
        nlh->nlmsg_seq = 1;

        auto* ndm = reinterpret_cast<struct ndmsg*>(NLMSG_DATA(nlh));
        ndm->ndm_family = AF_BRIDGE;
        ndm->ndm_ifindex = static_cast<int>(ifindex);
        ndm->ndm_state = NUD_PERMANENT;
        ndm->ndm_flags = NTF_MASTER;

        // Додавання MAC-адреси
        add_rtattr(buffer, nlh, NDA_LLADDR, mac.bytes.data(), mac.bytes.size());

        // Додавання VLAN ID (якщо активний)
        if (vid > 0) {
            add_rtattr(buffer, nlh, NDA_VLAN, &vid, sizeof(vid));
        }

        struct sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;

        if (::sendto(nl_sock.native_handle(), nlh, nlh->nlmsg_len, 0,
                     reinterpret_cast<struct sockaddr*>(&sa), sizeof(sa)) < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
        }

        std::array<uint8_t, 4096> recv_buf{};
        ssize_t len = ::recv(nl_sock.native_handle(), recv_buf.data(), recv_buf.size(), 0);
        if (len < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
        }

        auto* resp = reinterpret_cast<struct nlmsghdr*>(recv_buf.data());
        if (resp->nlmsg_type == NLMSG_ERROR) {
            auto* err = reinterpret_cast<struct nlmsgerr*>(NLMSG_DATA(resp));
            if (err->error != 0) {
                return std::unexpected(std::make_error_code(static_cast<std::errc>(-err->error)));
            }
        }

        return {};
    }

private:
    static void add_rtattr(std::vector<uint8_t>& buf, struct nlmsghdr* nlh,
                           unsigned short type, const void* data, size_t data_len)
    {
        size_t rta_len = RTA_LENGTH(data_len);
        auto* rta = reinterpret_cast<struct rtattr*>(buf.data() + NLMSG_ALIGN(nlh->nlmsg_len));
        rta->rta_type = type;
        rta->rta_len = static_cast<unsigned short>(rta_len);
        std::memcpy(RTA_DATA(rta), data, data_len);
        nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(rta_len);
    }
};

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <ifname> <MAC-адреса> [VLAN_ID]\n";
        return 1;
    }

    auto mac_res = MacAddress::from_string(argv[2]);
    if (!mac_res) {
        std::cerr << "Помилка: " << mac_res.error() << "\n";
        return 1;
    }

    uint16_t vid = (argc >= 4) ? static_cast<uint16_t>(std::stoi(argv[3])) : 0;
    auto res = BridgeController::add_static_fdb(argv[1], *mac_res, vid);

    if (!res) {
        std::cerr << "Помилка налаштування FDB: " << res.error().message() << "\n";
        return 1;
    }

    std::cout << "Статичний запис FDB успішно додано.\n";
    return 0;
}
