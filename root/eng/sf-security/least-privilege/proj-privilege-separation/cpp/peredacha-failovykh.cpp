#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <cstring>
#include <expected>
#include <system_error>

namespace security {

[[nodiscard]] auto send_file_descriptor(int socket_fd, int fd_to_send) noexcept 
    -> std::expected<void, std::error_code> 
{
    struct msghdr msg{};
    char dummy = 'F';
    struct iovec iov{ .iov_base = &dummy, .iov_len = sizeof(dummy) };
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    char cmsg_buf[CMSG_SPACE(sizeof(int))]{};
    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);

    struct cmsghdr* cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));
    std::memcpy(CMSG_DATA(cmsg), &fd_to_send, sizeof(int));

    if (::sendmsg(socket_fd, &msg, 0) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

[[nodiscard]] auto receive_file_descriptor(int socket_fd) noexcept 
    -> std::expected<int, std::error_code> 
{
    struct msghdr msg{};
    char dummy = 0;
    struct iovec iov{ .iov_base = &dummy, .iov_len = sizeof(dummy) };
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    char cmsg_buf[CMSG_SPACE(sizeof(int))]{};
    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);

    if (::recvmsg(socket_fd, &msg, 0) <= 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    struct cmsghdr* cmsg = CMSG_FIRSTHDR(&msg);
    if (!cmsg || cmsg->cmsg_type != SCM_RIGHTS) {
        return std::unexpected(std::make_error_code(std::errc::bad_message));
    }

    int received_fd = -1;
    std::memcpy(&received_fd, CMSG_DATA(cmsg), sizeof(int));
    return received_fd;
}

} // namespace security
