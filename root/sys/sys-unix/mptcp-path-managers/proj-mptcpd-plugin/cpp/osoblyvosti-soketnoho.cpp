// C++ Implementation: RAII Modern Standalone Netlink socket monitor
#include <iostream>
#include <vector>
#include <memory>
#include <system_error>
#include <expected>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>

namespace mptcp::netlink {

class NetlinkSocket {
public:
    explicit NetlinkSocket(int fd) noexcept : fd_(fd) {}

    ~NetlinkSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NetlinkSocket(NetlinkSocket const&) = delete;
    NetlinkSocket& operator=(NetlinkSocket const&) = delete;

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

    [[nodiscard]] static std::expected<NetlinkSocket, std::error_code> create(uint32_t multicast_group) noexcept {
        int fd = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        sockaddr_nl local{};
        local.nl_family = AF_NETLINK;
        local.nl_groups = multicast_group;

        if (::bind(fd, reinterpret_cast<sockaddr*>(&local), sizeof(local)) < 0) {
            int const err = errno;
            ::close(fd);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        return NetlinkSocket{ fd };
    }

    void listen_loop() const {
        std::vector<uint8_t> buffer(8192);

        while (true) {
            ssize_t const bytes_read = ::recv(fd_, buffer.data(), buffer.size(), 0);
            if (bytes_read < 0) {
                std::cerr << "[cpp-netlink-mon] Receive error: " 
                          << std::generic_category().message(errno) << "\n";
                break;
            }

            auto* nlh = reinterpret_cast<nlmsghdr*>(buffer.data());
            auto remaining = static_cast<size_t>(bytes_read);

            while (NLMSG_OK(nlh, remaining)) {
                if (nlh->nlmsg_type == NLMSG_DONE) break;
                if (nlh->nlmsg_type == NLMSG_ERROR) {
                    std::cerr << "[cpp-netlink-mon] Netlink payload error message\n";
                    break;
                }

                auto const* genl = static_cast<genlmsghdr const*>(NLMSG_DATA(nlh));
                std::cout << "[cpp-netlink-mon] Received MPTCP Event Cmd ID: " 
                          << static_cast<int>(genl->cmd) << "\n";

                nlh = NLMSG_NEXT(nlh, remaining);
            }
        }
    }

private:
    int fd_ = -1;
};

} // namespace mptcp::netlink
