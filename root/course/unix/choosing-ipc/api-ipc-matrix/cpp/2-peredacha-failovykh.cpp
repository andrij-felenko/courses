#include <sys/socket.h>
#include <cstring>
#include <expected>
#include <string_view>

std::expected<void, std::string_view> send_single_fd(int socket_fd, int fd_to_send) {
    struct msghdr msg{};
    struct iovec iov[1]{};
    char dummy = 'F';
    char cmsg_buf[CMSG_SPACE(sizeof(int))]{};

    iov[0].iov_base = &dummy;
    iov[0].iov_len = 1;
    msg.msg_iov = iov;
    msg.msg_iovlen = 1;

    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));

    *reinterpret_cast<int*>(CMSG_DATA(cmsg)) = fd_to_send;

    if (::sendmsg(socket_fd, &msg, 0) < 0) {
        return std::unexpected("sendmsg SCM_RIGHTS failed");
    }
    return {};
}
