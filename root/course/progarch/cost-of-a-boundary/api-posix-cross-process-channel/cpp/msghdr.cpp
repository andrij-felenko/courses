#include <sys/socket.h>
#include <cstring>
#include <unistd.h>
#include <array>
#include <system_error>

// Безпечна передача дескриптора через сокетний канал у C++
void send_fd(int channel_fd, int fd_to_send) {
    struct msghdr msg{};
    struct iovec iov{};
    char dummy_byte = 'D';

    union ControlStorage {
        std::array<char, CMSG_SPACE(sizeof(int))> buf{};
        struct cmsghdr align;
    } u;

    iov.iov_base = &dummy_byte;
    iov.iov_len = sizeof(dummy_byte);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    msg.msg_control = u.buf.data();
    msg.msg_controllen = u.buf.size();

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));

    std::memcpy(CMSG_DATA(cmsg), &fd_to_send, sizeof(int));

    if (::sendmsg(channel_fd, &msg, 0) == -1) {
        throw std::system_error(errno, std::generic_category(), "sendmsg failed");
    }
}

// Безпечне отримання дескриптора з перевіркою MSG_CTRUNC у C++
int recv_fd(int channel_fd) {
    struct msghdr msg{};
    struct iovec iov{};
    char dummy_byte{};

    union ControlStorage {
        std::array<char, CMSG_SPACE(sizeof(int))> buf{};
        struct cmsghdr align;
    } u;

    iov.iov_base = &dummy_byte;
    iov.iov_len = sizeof(dummy_byte);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    msg.msg_control = u.buf.data();
    msg.msg_controllen = u.buf.size();

    ssize_t n = ::recvmsg(channel_fd, &msg, 0);
    if (n <= 0) {
        throw std::system_error(n == 0 ? ECONNRESET : errno, 
                                std::generic_category(), 
                                "recvmsg failed or channel closed");
    }

    if (msg.msg_flags & MSG_CTRUNC) {
        throw std::system_error(EMSGSIZE, std::generic_category(), "Control message truncated");
    }

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    if (!cmsg || cmsg->cmsg_level != SOL_SOCKET || cmsg->cmsg_type != SCM_RIGHTS) {
        throw std::system_error(EPROTO, std::generic_category(), "Invalid ancillary message");
    }

    int received_fd = -1;
    std::memcpy(&received_fd, CMSG_DATA(cmsg), sizeof(int));
    return received_fd;
}
