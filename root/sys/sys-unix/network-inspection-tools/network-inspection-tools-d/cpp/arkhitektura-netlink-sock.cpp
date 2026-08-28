#include <iostream>
#include <vector>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/sock_diag.h>
#include <linux/inet_diag.h>
#include <span>
#include <expected>

namespace net {

// RAII-дескриптор для сокета Netlink
class NetlinkSocket {
public:
    explicit NetlinkSocket() {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_INET_DIAG);
    }
    ~NetlinkSocket() noexcept {
        if (fd_ >= 0) ::close(fd_);
    }

    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;
    NetlinkSocket(NetlinkSocket&& o) noexcept : fd_{o.fd_} { o.fd_ = -1; }
    NetlinkSocket& operator=(NetlinkSocket&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_open() const noexcept { return fd_ >= 0; }

    [[nodiscard]] std::expected<void, int> request_listen_dump() const noexcept {
        struct Request {
            nlmsghdr nlh;
            inet_diag_req_v2 req;
        } msg{};

        msg.nlh.nlmsg_len = sizeof(msg);
        msg.nlh.nlmsg_type = SOCK_DIAG_BY_FAMILY;
        msg.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_DUMP;
        msg.nlh.nlmsg_seq = 1;

        msg.req.sdiag_family = AF_INET;
        msg.req.sdiag_protocol = IPPROTO_TCP;
        msg.req.idiag_states = (1U << TCP_LISTEN);
        msg.req.idiag_ext = (1U << (INET_DIAG_INFO - 1));

        sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;

        if (::sendto(fd_, &msg, sizeof(msg), 0,
                     reinterpret_cast<const sockaddr*>(&sa), sizeof(sa)) < 0) {
            return std::unexpected(errno);
        }
        return {};
    }

private:
    int fd_{-1};
};

} // namespace net
