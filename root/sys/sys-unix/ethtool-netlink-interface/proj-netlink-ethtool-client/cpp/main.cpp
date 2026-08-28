#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span >
#include <memory>
#include <stdexcept>
#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>
#include <linux/ethtool_netlink.h>

class NetlinkSocket {
public:
    explicit NetlinkSocket(int protocol = NETLINK_GENERIC) {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW, protocol);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to create AF_NETLINK socket");
        }

        sockaddr_nl local{};
        local.nl_family = AF_NETLINK;
        local.nl_pid = static_cast<uint32_t>(::getpid());

        if (::bind(fd_, reinterpret_cast<sockaddr*>(&local), sizeof(local)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Failed to bind Netlink socket");
        }
    }

    ~NetlinkSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;

    NetlinkSocket(NetlinkSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    NetlinkSocket& operator=(NetlinkSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

    void send(std::span<const uint8_t> data) const {
        sockaddr_nl nladdr{};
        nladdr.nl_family = AF_NETLINK;

        if (::sendto(fd_, data.data(), data.size(), 0,
                     reinterpret_cast<sockaddr*>(&nladdr), sizeof(nladdr)) < 0) {
            throw std::system_error(errno, std::generic_category(), "sendto failed");
        }
    }

    std::vector<uint8_t> receive(size_t max_size = 8192) const {
        std::vector<uint8_t> buffer(max_size);
        ssize_t bytes_read = ::recv(fd_, buffer.data(), buffer.size(), 0);
        if (bytes_read < 0) {
            throw std::system_error(errno, std::generic_category(), "recv failed");
        }
        buffer.resize(static_cast<size_t>(bytes_read));
        return buffer;
    }

private:
    int fd_{-1};
};

struct LinkInfo {
    uint32_t speed{0};
    uint8_t duplex{0};
    bool autoneg{false};
};

class EthtoolNetlinkClient {
public:
    explicit EthtoolNetlinkClient(NetlinkSocket& socket)
        : socket_(socket), family_id_(resolveFamilyId(ETHTOOL_GENL_NAME)) {}

    [[nodiscard]] uint16_t family_id() const noexcept { return family_id_; }

    [[nodiscard]] LinkInfo getLinkModes(std::string_view ifname) const {
        std::vector<uint8_t> request_buf(8192, 0);

        auto* nlh = reinterpret_cast<nlmsghdr*>(request_buf.data());
        nlh->nlmsg_len = NLMSG_LENGTH(GENL_HDRLEN);
        nlh->nlmsg_type = family_id_;
        nlh->nlmsg_flags = NLM_F_REQUEST;
        nlh->nlmsg_seq = 2;
        nlh->nlmsg_pid = static_cast<uint32_t>(::getpid());

        auto* ghdr = reinterpret_cast<genlmsghdr*>(NLMSG_DATA(nlh));
        ghdr->cmd = ETHTOOL_MSG_LINKMODES_GET;
        ghdr->version = ETHTOOL_GENL_VERSION;

        // Вкладений заголовок ETHTOOL_A_HEADER
        size_t header_offset = nlh->nlmsg_len;
        auto* hdr_attr = reinterpret_cast<rtattr*>(request_buf.data() + header_offset);
        hdr_attr->rta_type = NLA_F_NESTED | ETHTOOL_A_LINKMODES_HEADER;
        hdr_attr->rta_len = RTA_LENGTH(0);
        nlh->nlmsg_len += RTA_LENGTH(0);

        appendAttr(nlh, request_buf.size(), ETHTOOL_A_HEADER_DEV_NAME, ifname.data(), ifname.size() + 1);
        hdr_attr->rta_len = static_cast<unsigned short>(nlh->nlmsg_len - header_offset);

        request_buf.resize(nlh->nlmsg_len);
        socket_.send(request_buf);

        auto response = socket_.receive();
        return parseLinkModes(response);
    }

private:
    NetlinkSocket& socket_;
    uint16_t family_id_{0};

    static void appendAttr(nlmsghdr* nlh, size_t maxlen, int type, const void* data, size_t alen) {
        size_t len = RTA_LENGTH(alen);
        if (NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(len) > maxlen) {
            throw std::runtime_error("Netlink message buffer overflow");
        }
        auto* rta = reinterpret_cast<rtattr*>(reinterpret_cast<char*>(nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
        rta->rta_type = static_cast<unsigned short>(type);
        rta->rta_len = static_cast<unsigned short>(len);
        if (alen > 0 && data != nullptr) {
            std::memcpy(RTA_DATA(rta), data, alen);
        }
        nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(len);
    }

    uint16_t resolveFamilyId(std::string_view family_name) {
        std::vector<uint8_t> request_buf(4096, 0);

        auto* nlh = reinterpret_cast<nlmsghdr*>(request_buf.data());
        nlh->nlmsg_len = NLMSG_LENGTH(GENL_HDRLEN);
        nlh->nlmsg_type = GENL_ID_CTRL;
        nlh->nlmsg_flags = NLM_F_REQUEST;
        nlh->nlmsg_seq = 1;
        nlh->nlmsg_pid = static_cast<uint32_t>(::getpid());

        auto* ghdr = reinterpret_cast<genlmsghdr*>(NLMSG_DATA(nlh));
        ghdr->cmd = CTRL_CMD_GETFAMILY;
        ghdr->version = 1;

        appendAttr(nlh, request_buf.size(), CTRL_ATTR_FAMILY_NAME, family_name.data(), family_name.size() + 1);
        request_buf.resize(nlh->nlmsg_len);

        socket_.send(request_buf);
        auto response = socket_.receive();

        auto* res_nlh = reinterpret_cast<nlmsghdr*>(response.data());
        if (!NLMSG_OK(res_nlh, response.size()) || res_nlh->nlmsg_type == NLMSG_ERROR) {
            throw std::runtime_error("Failed to resolve Generic Netlink family ID");
        }

        auto* res_ghdr = reinterpret_cast<genlmsghdr*>(NLMSG_DATA(res_nlh));
        auto* attr = reinterpret_cast<rtattr*>(reinterpret_cast<char*>(res_ghdr) + GENL_HDRLEN);
        int attrlen = static_cast<int>(res_nlh->nlmsg_len - NLMSG_LENGTH(GENL_HDRLEN));

        while (RTA_OK(attr, attrlen)) {
            if (attr->rta_type == CTRL_ATTR_FAMILY_ID) {
                return *reinterpret_cast<const uint16_t*>(RTA_DATA(attr));
            }
            attr = RTA_NEXT(attr, attrlen);
        }
        throw std::runtime_error("Family ID attribute missing in response");
    }

    static LinkInfo parseLinkModes(std::span<const uint8_t> response) {
        const auto* nlh = reinterpret_cast<const nlmsghdr*>(response.data());
        LinkInfo info{};

        if (NLMSG_OK(nlh, response.size())) {
            const auto* ghdr = reinterpret_cast<const genlmsghdr*>(NLMSG_DATA(nlh));
            const auto* attr = reinterpret_cast<const rtattr*>(reinterpret_cast<const char*>(ghdr) + GENL_HDRLEN);
            int attrlen = static_cast<int>(nlh->nlmsg_len - NLMSG_LENGTH(GENL_HDRLEN));

            while (RTA_OK(attr, attrlen)) {
                if (attr->rta_type == ETHTOOL_A_LINKMODES_SPEED) {
                    info.speed = *reinterpret_cast<const uint32_t*>(RTA_DATA(attr));
                } else if (attr->rta_type == ETHTOOL_A_LINKMODES_DUPLEX) {
                    info.duplex = *reinterpret_cast<const uint8_t*>(RTA_DATA(attr));
                } else if (attr->rta_type == ETHTOOL_A_LINKMODES_AUTONEG) {
                    info.autoneg = (*reinterpret_cast<const uint8_t*>(RTA_DATA(attr)) != 0);
                }
                attr = RTA_NEXT(attr, attrlen);
            }
        }
        return info;
    }
};

int main(int argc, char* argv[]) {
    try {
        std::string_view ifname = (argc > 1) ? argv[1] : "eth0";

        NetlinkSocket socket;
        EthtoolNetlinkClient client(socket);

        std::cout << "Resolved Ethtool Generic Netlink Family ID: " << client.family_id() << "\n";

        LinkInfo info = client.getLinkModes(ifname);
        std::cout << "[" << ifname << "] Speed: " << info.speed << " Mbps, Duplex: "
                  << (info.duplex == 1 ? "Full" : "Half")
                  << ", Autoneg: " << (info.autoneg ? "on" : "off") << "\n";

    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
