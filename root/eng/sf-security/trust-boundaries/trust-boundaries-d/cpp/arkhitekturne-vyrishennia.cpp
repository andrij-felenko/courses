#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <cstring>
#include <expected>
#include <span>
#include <system_error>

namespace security {

class [[nodiscard]] SocketChannel {
public:
    explicit SocketChannel(int fd) noexcept : sock_fd_(fd) {}
    ~SocketChannel() = default;

    std::expected<void, std::error_code> send_descriptor(int fd_to_send) const noexcept {
        msghdr msg{};
        alignas(cmsghdr) char control_buf[CMSG_SPACE(sizeof(int))]{};

        char payload[] = "FD";
        iovec io{ .iov_base = payload, .iov_len = sizeof(payload) - 1 };
        msg.msg_iov = &io;
        msg.msg_iovlen = 1;
        msg.msg_control = control_buf;
        msg.msg_controllen = sizeof(control_buf);

        cmsghdr* cmsg = CMSG_FIRSTHDR(&msg);
        cmsg->cmsg_level = SOL_SOCKET;
        cmsg->cmsg_type = SCM_RIGHTS;
        cmsg->cmsg_len = CMSG_LEN(sizeof(int));
        std::memcpy(CMSG_DATA(cmsg), &fd_to_send, sizeof(int));

        if (::sendmsg(sock_fd_, &msg, 0) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

private:
    int sock_fd_;
};

} // namespace security
