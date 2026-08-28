#include <iostream>
#include <span>
#include <system_error>
#include <expected>
#include <vector>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/udp.h>

class UdpSocket {
    int fd_{-1};
public:
    explicit UdpSocket(int fd) : fd_(fd) {}
    ~UdpSocket() { if (fd_ >= 0) ::close(fd_); }
    UdpSocket(const UdpSocket&) = delete;
    UdpSocket& operator=(const UdpSocket&) = delete;
    UdpSocket(UdpSocket&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    UdpSocket& operator=(UdpSocket&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int native_handle() const noexcept { return fd_; }
};

std::expected<size_t, std::error_code> send_udp_gso(
    int sockfd,
    const sockaddr_in& dst_addr,
    std::span<const std::byte> payload,
    uint16_t segment_size)
{
    ::iovec iov{};
    iov.iov_base = const_cast<void*>(static_cast<const void*>(payload.data()));
    iov.iov_len = payload.size();

    alignas(struct cmsghdr) char cbuf[CMSG_SPACE(sizeof(uint16_t))]{};

    ::msghdr msg{};
    msg.msg_name = const_cast<sockaddr_in*>(&dst_addr);
    msg.msg_namelen = sizeof(dst_addr);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cbuf;
    msg.msg_controllen = sizeof(cbuf);

    ::cmsghdr* cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_UDP;
    cmsg->cmsg_type = UDP_SEGMENT;
    cmsg->cmsg_len = CMSG_LEN(sizeof(uint16_t));

    auto* val_ptr = reinterpret_cast<uint16_t*>(CMSG_DATA(cmsg));
    *val_ptr = segment_size;

    ssize_t ret = ::sendmsg(sockfd, &msg, 0);
    if (ret < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return static_cast<size_t>(ret);
}
